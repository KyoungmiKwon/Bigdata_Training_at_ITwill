#######################################################################################################################
# Import Packages
#######################################################################################################################
import numpy as np
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'
#######################################################################################################################
# 변수 모음
#######################################################################################################################
t_view = 1
cut = 25
col_num = 2
lstm_num = 16
dense_num = 4
col_list = ['','Sentiment Dict', 'Kobert', 'One-Hot', 'Ensemble']

label_df = pd.read_excel(f'stock_label_rev_Sentiment Dict_0.xlsx')[0]
avg_df = label_df
for col in col_list:
    for lks in range(100):
#######################################################################################################################
# scaling
#######################################################################################################################
# ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Sentiment Dict', 'Kobert', 'One-Hot', 'Ensemble']
        if col == '':
            temp1 = pd.read_excel(f'stock_pred_rev_{lks}.xlsx')[0]
        else:
            temp1 = pd.read_excel(f'stock_pred_rev_{col}_{lks}.xlsx')[0]
        if lks == 0:
            temp2 = temp1
        else:
            temp2 = pd.concat((temp2, temp1), axis=1)
    temp2.columns = [i for i in range(temp2.shape[1])]
    temp2[f'{col}_avg'] = temp2.mean(axis=1)
    temp2.to_excel(f'stock_pred_{col}.xlsx', index=False)
    avg_df = pd.concat((avg_df, temp2[f'{col}_avg']),axis=1)
avg_df.to_excel(f'stock_avg.xlsx', index=False)
avg_df.columns=['exact','close_avg','Sentiment Dict_avg','Kobert_avg','One-Hot_avg','Ensemble_avg']
avg_df = avg_df.drop(['close_avg','Sentiment Dict_avg','One-Hot_avg','Ensemble_avg' ], axis=1)
# avg_df.drop(['exact','close_avg','Sentiment Dict_avg','One-Hot_avg','Ensemble_avg'], axis=1)
# print(avg_df.shape, avg_df.columns)


avg_df.plot(figsize=(12, 9))
plt.grid()
plt.savefig(f'with_senti.png', dpi=200)
plt.show()
