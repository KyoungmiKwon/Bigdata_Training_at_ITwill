#######################################################################################################################
# Install Packages
#######################################################################################################################
# pip install transformers
# pip install sentencepiece
# pip install tensorflow_addons
# conda install pytorch torchvision torchaudio cudatoolkit=11.0 -c pytorch


#######################################################################################################################
# Import Packages
#######################################################################################################################
from tqdm import tqdm
import unicodedata
from shutil import copyfile

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
import tensorflow_addons as tfa

from transformers import *
from transformers import PreTrainedTokenizer

import os
import logging
import json
import sentencepiece as spm
# os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'
#######################################################################################################################
# Settings and Class Definition
#######################################################################################################################
logger = logging.getLogger(__name__)

VOCAB_FILES_NAMES = {"vocab_file": "tokenizer_78b3253a26.model",
                     "vocab_txt": "vocab.txt"}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/tokenizer_78b3253a26.model",
        "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/tokenizer_78b3253a26.model",
        "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/tokenizer_78b3253a26.model"
    },
    "vocab_txt": {
        "monologg/kobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert/vocab.txt",
        "monologg/kobert-lm": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/kobert-lm/vocab.txt",
        "monologg/distilkobert": "https://s3.amazonaws.com/models.huggingface.co/bert/monologg/distilkobert/vocab.txt"
    }
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "monologg/kobert": 512,
    "monologg/kobert-lm": 512,
    "monologg/distilkobert": 512
}

PRETRAINED_INIT_CONFIGURATION = {
    "monologg/kobert": {"do_lower_case": False},
    "monologg/kobert-lm": {"do_lower_case": False},
    "monologg/distilkobert": {"do_lower_case": False}
}

SPIECE_UNDERLINE = u'???'


class KoBertTokenizer(PreTrainedTokenizer):
    """
        SentencePiece based tokenizer. Peculiarities:
            - requires `SentencePiece <https://github.com/google/sentencepiece>`_
    """
    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    pretrained_init_configuration = PRETRAINED_INIT_CONFIGURATION
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES

    def __init__(
            self,
            vocab_file,
            vocab_txt,
            do_lower_case=False,
            remove_space=True,
            keep_accents=False,
            unk_token="[UNK]",
            sep_token="[SEP]",
            pad_token="[PAD]",
            cls_token="[CLS]",
            mask_token="[MASK]",
            **kwargs):
        super().__init__(
            unk_token=unk_token,
            sep_token=sep_token,
            pad_token=pad_token,
            cls_token=cls_token,
            mask_token=mask_token,
            **kwargs
        )

        # Build vocab
        self.token2idx = dict()
        self.idx2token = []
        with open(vocab_txt, 'r', encoding='utf-8') as f:
            for idx, token in enumerate(f):
                token = token.strip()
                self.token2idx[token] = idx
                self.idx2token.append(token)

        try:
            import sentencepiece as spm
        except ImportError:
            logger.warning("You need to install SentencePiece to use KoBertTokenizer: https://github.com/google/sentencepiece"
                           "pip install sentencepiece")

        self.do_lower_case = do_lower_case
        self.remove_space = remove_space
        self.keep_accents = keep_accents
        self.vocab_file = vocab_file
        self.vocab_txt = vocab_txt

        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.Load(vocab_file)

    @property
    def vocab_size(self):
        return len(self.idx2token)

    def get_vocab(self):
        return dict(self.token2idx, **self.added_tokens_encoder)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["sp_model"] = None
        return state

    def __setstate__(self, d):
        self.__dict__ = d
        try:
            import sentencepiece as spm
        except ImportError:
            logger.warning("You need to install SentencePiece to use KoBertTokenizer: https://github.com/google/sentencepiece"
                           "pip install sentencepiece")
        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.Load(self.vocab_file)

    def preprocess_text(self, inputs):
        if self.remove_space:
            outputs = " ".join(inputs.strip().split())
        else:
            outputs = inputs
        outputs = outputs.replace("``", '"').replace("''", '"')

        if not self.keep_accents:
            outputs = unicodedata.normalize('NFKD', outputs)
            outputs = "".join([c for c in outputs if not unicodedata.combining(c)])
        if self.do_lower_case:
            outputs = outputs.lower()

        return outputs

    def _tokenize(self, text, return_unicode=True, sample=False):
        """ Tokenize a string. """
        text = self.preprocess_text(text)

        if not sample:
            pieces = self.sp_model.EncodeAsPieces(text)
        else:
            pieces = self.sp_model.SampleEncodeAsPieces(text, 64, 0.1)
        new_pieces = []
        for piece in pieces:
            if len(piece) > 1 and piece[-1] == str(",") and piece[-2].isdigit():
                cur_pieces = self.sp_model.EncodeAsPieces(piece[:-1].replace(SPIECE_UNDERLINE, ""))
                if piece[0] != SPIECE_UNDERLINE and cur_pieces[0][0] == SPIECE_UNDERLINE:
                    if len(cur_pieces[0]) == 1:
                        cur_pieces = cur_pieces[1:]
                    else:
                        cur_pieces[0] = cur_pieces[0][1:]
                cur_pieces.append(piece[-1])
                new_pieces.extend(cur_pieces)
            else:
                new_pieces.append(piece)

        return new_pieces

    def _convert_token_to_id(self, token):
        """ Converts a token (str/unicode) in an id using the vocab. """
        return self.token2idx.get(token, self.token2idx[self.unk_token])

    def _convert_id_to_token(self, index, return_unicode=True):
        """Converts an index (integer) in a token (string/unicode) using the vocab."""
        return self.idx2token[index]

    def convert_tokens_to_string(self, tokens):
        """Converts a sequence of tokens (strings for sub-words) in a single string."""
        out_string = "".join(tokens).replace(SPIECE_UNDERLINE, " ").strip()
        return out_string

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks
        by concatenating and adding special tokens.
        A KoBERT sequence has the following format:
            single sequence: [CLS] X [SEP]
            pair of sequences: [CLS] A [SEP] B [SEP]
        """
        if token_ids_1 is None:
            return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + token_ids_1 + sep

    def get_special_tokens_mask(self, token_ids_0, token_ids_1=None, already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer ``prepare_for_model`` or ``encode_plus`` methods.
        Args:
            token_ids_0: list of ids (must not contain special tokens)
            token_ids_1: Optional list of ids (must not contain special tokens), necessary when fetching sequence ids
                for sequence pairs
            already_has_special_tokens: (default False) Set to True if the token list is already formated with
                special tokens for the model
        Returns:
            A list of integers in the range [0, 1]: 0 for a special token, 1 for a sequence token.
        """

        if already_has_special_tokens:
            if token_ids_1 is not None:
                raise ValueError(
                    "You should not supply a second sequence if the provided sequence of "
                    "ids is already formated with special tokens for the model."
                )
            return list(map(lambda x: 1 if x in [self.sep_token_id, self.cls_token_id] else 0, token_ids_0))

        if token_ids_1 is not None:
            return [1] + ([0] * len(token_ids_0)) + [1] + ([0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]

    def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1=None):
        """
        Creates a mask from the two sequences passed to be used in a sequence-pair classification task.
        A KoBERT sequence pair mask has the following format:
        0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1
        | first sequence    | second sequence
        if token_ids_1 is None, only returns the first portion of the mask (0's).
        """
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None:
            return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]

    def save_vocabulary(self, save_directory):
        """ Save the sentencepiece vocabulary (copy original file) and special tokens file
            to a directory.
        """
        if not os.path.isdir(save_directory):
            logger.error("Vocabulary path ({}) should be a directory".format(save_directory))
            return

        # 1. Save sentencepiece model
        out_vocab_model = os.path.join(save_directory, VOCAB_FILES_NAMES["vocab_file"])

        if os.path.abspath(self.vocab_file) != os.path.abspath(out_vocab_model):
            copyfile(self.vocab_file, out_vocab_model)

        # 2. Save vocab.txt
        index = 0
        out_vocab_txt = os.path.join(save_directory, VOCAB_FILES_NAMES["vocab_txt"])
        with open(out_vocab_txt, "w", encoding="utf-8") as writer:
            for token, token_index in sorted(self.token2idx.items(), key=lambda kv: kv[1]):
                if index != token_index:
                    logger.warning(
                        "Saving vocabulary to {}: vocabulary indices are not consecutive."
                        " Please check that the vocabulary is not corrupted!".format(out_vocab_txt)
                    )
                    index = token_index
                writer.write(token + "\n")
                index += 1

        return out_vocab_model, out_vocab_txt



#######################################################################################################################
# Tokenizer from KoBERT
#######################################################################################################################
tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')



#######################################################################################################################
# ?????? ??????(df -> train/test), BERT Input ????????? ?????? ??????
#######################################################################################################################
def convert_data(data_df, DATA_COLUMN, LABEL_COLUMN, SEQ_LEN):
    global tokenizer
    tokens, masks, segments, targets = [], [], [], []

    for i in tqdm(range(len(data_df))):
        # token : ????????? ????????????
        token = tokenizer.encode(data_df[DATA_COLUMN][i], truncation=True, padding='max_length', max_length=SEQ_LEN)

        # ???????????? ???????????? ???????????? ????????? ?????? ????????? 1, ????????? ????????? 0?????? ??????
        num_zeros = token.count(0)
        mask = [1] * (SEQ_LEN - num_zeros) + [0] * num_zeros

        # ????????? ??????????????? ??????????????? ??????????????? ????????? 1????????? ???????????? ?????? 0
        segment = [0] * SEQ_LEN

        # ?????? ???????????? ???????????? token, mask, segment??? tokens, segments??? ?????? ??????
        tokens.append(token)
        masks.append(mask)
        segments.append(segment)

        # ??????(?????? : 1 ?????? 0)??? targets ????????? ????????? ???
        targets.append(data_df[LABEL_COLUMN][i])

    # tokens, masks, segments, ?????? ?????? targets??? numpy array??? ??????
    tokens = np.array(tokens)
    masks = np.array(masks)
    segments = np.array(segments)
    targets = np.array(targets)

    return [tokens, masks, segments], targets


# ?????? ????????? convert_data ????????? ???????????? ????????? ??????
def load_data(data_df, DATA_COLUMN, LABEL_COLUMN, SEQ_LEN):
    data_df[DATA_COLUMN] = data_df[DATA_COLUMN].astype(str)
    data_df[LABEL_COLUMN] = data_df[LABEL_COLUMN].astype(int)
    data_x, data_y = convert_data(data_df, DATA_COLUMN, LABEL_COLUMN, SEQ_LEN)
    return data_x, data_y


#######################################################################################################################
# Import Data
#######################################################################################################################
df_resize = pd.read_excel('News_resize_di.xlsx')
df_re = pd.read_excel('News_resize.xlsx')
df_3 = pd.read_excel('3_whole.xlsx')
df_a = pd.read_excel('a_whole.xlsx')


X = df_resize['Text']
y = df_resize['S'].astype(int)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)

train_df = pd.concat([X_train, y_train], axis=1).reset_index(drop=True)
test_df = pd.concat([X_test, y_test], axis=1).reset_index(drop=True)



#######################################################################################################################
# ?????? ??????(df -> train/test), BERT Input
#######################################################################################################################
# ?????? ??????
X_col='Text'
y_col="S"
seq_len=200

X_train, y_train = load_data(train_df, X_col, y_col, seq_len)
X_test, y_test = load_data(test_df, X_col, y_col, seq_len)



#######################################################################################################################
# BERT??? ????????? Keras Modeling
#######################################################################################################################
model = TFBertModel.from_pretrained("monologg/kobert", from_pt=True)
# ?????? ??????, ????????? ??????, ???????????? ?????? ??????
token_inputs = tf.keras.layers.Input((seq_len,), dtype=tf.int32, name='input_word_ids')
mask_inputs = tf.keras.layers.Input((seq_len,), dtype=tf.int32, name='input_masks')
segment_inputs = tf.keras.layers.Input((seq_len,), dtype=tf.int32, name='input_segment')
# ????????? [??????, ?????????, ????????????]??? ?????? ??????
bert_outputs = model([token_inputs, mask_inputs, segment_inputs])
bert_outputs = bert_outputs[1]

sentiment_drop = tf.keras.layers.Dropout(0.2)(bert_outputs)
sentiment_first = tf.keras.layers.Dense(1, activation='sigmoid', kernel_initializer=tf.keras.initializers.TruncatedNormal(stddev=0.02))(sentiment_drop)
sentiment_model = tf.keras.Model([token_inputs, mask_inputs, segment_inputs], sentiment_first)

# Rectified Adam ??????????????? ??????
opt = tfa.optimizers.RectifiedAdam(lr=5.0e-5, total_steps = 2344*2, warmup_proportion=0.1, min_lr=1e-5, epsilon=1e-08, clipnorm=1.0)
sentiment_model.compile(optimizer=opt, loss='binary_crossentropy', metrics = ['accuracy'])


sentiment_model.summary()
#######################################################################################################################
# Keras ??????
#######################################################################################################################
history = sentiment_model.fit(X_train,y_train, epochs=50, batch_size=64, validation_split=0.2)
# hist = pd.DataFrame(history.history)
# hist.plot()
# plt.show()



#######################################################################################################################
# Keras ??????
#######################################################################################################################
# sentiment_model.save('bert_binary_equal_ratio_test.h5')
# sentiment_model = tf.keras.models.load_model('bert_binary_equal_ratio_test.h5')



#######################################################################################################################
# Keras ??????
#######################################################################################################################
sentiment_model.evaluate(X_test, y_test)
pred = sentiment_model.predict(X_test)
pd.DataFrame(pred).to_excel('kobert_resize_pred.xlsx')
pd.DataFrame(y_test).to_excel('kobert_resize_label.xlsx')
#######################################################################################################################
X = df_re['Text']
y = df_re['S']
df_re_2 = pd.concat([X, y], axis=1)

X_re, y_re = load_data(df_re_2, X_col, y_col, seq_len)
sentiment_model.evaluate(X_re, y_re)
pred_re = sentiment_model.predict(X_re)
pd.DataFrame(pred_re).to_excel('kobert_re_pred.xlsx')
pd.DataFrame(y_re).to_excel('kobert_re_label.xlsx')
#######################################################################################################################
X = df_3['Text']
y = df_3['S']
df_3_2 = pd.concat([X, y], axis=1)

X_3, y_3 = load_data(df_3_2, X_col, y_col, seq_len)
pred_3 = sentiment_model.predict(X_3)
pd.DataFrame(pred_3).to_excel('kobert_3_pred.xlsx')
#######################################################################################################################
X = df_a['Text']
y = df_a['S']
df_a_2 = pd.concat([X, y], axis=1)

X_a, y_a = load_data(df_a_2, X_col, y_col, seq_len)
pred_a = sentiment_model.predict(X_a)
pd.DataFrame(pred_a).to_excel('kobert_a_pred.xlsx')
#######################################################################################################################

# dropout 0.2
#     74, 76.9, 77.6, 77.9, 78.7, 76.90, 79.78, 76.90, 72.56
# dropout 0.5
#     80.87, 73.65, 75.09, 79.42, 74.01, 78.34, 75.09, 71.84
#######################################################################################################################
# ?????? ????????? ?????? ???. separate
#######################################################################################################################
# 250
#a     71.59, 70.11, 67.90, 77.86, 71.59, 75.65
#3     76.26, 64.38, 70.78, 68.04, 70.78, 74.89
#######################################################################################################################
# C03_KM_Text_Preprocessing_2????????? ?????? ????????? ?????? ?????? ?????????????????? ??????
#######################################################################################################################
# ar   76.01, 78.97, 77.12, 74.54, 76.75, 76.01, 72.32, 79.70, 76.75, 75.65
# 3r   79.00, 77.17, 78.54, 76.26, 73.06, 72.15, 76.71, 76.71, 77.17, 77.17
# 3a   77.78,