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
# 함수 정의
#######################################################################################################################
def reverse_min_max_scaling(org_x, x):
    org_x_np = np.asarray(org_x)
    x_np = np.asarray(x)
    return (x_np * (org_x_np.max() - org_x_np.min() + 1e-7)) + org_x_np.min()

def stock_preprocessing(data, t_view=20, DATE = 'Date', TARGET = 'Volume'):
    global col_num
    date_j = []
    data_j = []
    label_j = []

    for j in range(len(data)-t_view):
        for i in range(t_view):
            if i == 0:
                temp_df = data.iloc[[j+i]]
            else:
                temp_df = pd.concat((temp_df, data.iloc[[j+i]]), axis=0)

        date_j.append(data.iloc[[j + t_view]][DATE].to_numpy())
        if col_num == 1:
            data_j.append(temp_df[TARGET].to_numpy())
        if col_num == 4:
            data_j.append(temp_df.drop([DATE, TARGET], axis=1).to_numpy())
        if col_num == 5:
            data_j.append(temp_df.drop([DATE], axis=1).to_numpy())
        label_j.append(data.iloc[[j + t_view]][TARGET].to_numpy())

    return np.array(date_j), np.array(data_j), np.array(label_j)



#######################################################################################################################
# 변수 모음
#######################################################################################################################
# 예측하는데 사용되는 날 수
t_view_list = [1]
# 예측할 날 수
cut_list = [25]
# close를 예측하는데 사용하지 않으면 4, 사용하면 5, close만 사용하면 1
col_list = [1]
lstm_list = [16]
dense_list = [4]

for lks in range(100):
    for t_view in t_view_list:
        for cut in cut_list:
            for col_num in col_list:
                for lstm_num in lstm_list:
                    for dense_num in dense_list:
    #######################################################################################################################
    # 주가 URL
    #######################################################################################################################
                        try:
                            preprocessed = pd.read_excel(f'stock_pre_{t_view}_{col_num}_{cut}.xlsx')
                            preprocessed.columns = [i for i in range(t_view*col_num+2)]
                            Date = preprocessed[0].to_numpy()
                            Data = preprocessed.drop([0, t_view*col_num+1], axis=1).to_numpy().reshape(-1, t_view, col_num)
                            Label = preprocessed[t_view*col_num+1].to_numpy()

                            samsung_url = 'refer.xlsx'
                            samsung_stock = pd.read_excel(samsung_url, header=0).drop('Change', axis=1)
    #######################################################################################################################
    # 주가 URL
    #######################################################################################################################
                        except:
                            samsung_url = 'refer.xlsx'
                            samsung_stock = pd.read_excel(samsung_url, header=0).drop('Change', axis=1)
    #######################################################################################################################
    # scaling
    #######################################################################################################################
                            scaler = MinMaxScaler()
                            scale_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                            scaler.fit(samsung_stock[scale_cols])
                            samsung_scaled = scaler.transform(samsung_stock[scale_cols])
                            samsung_scaled = pd.DataFrame(samsung_scaled)
                            samsung_scaled.columns = scale_cols
                            samsung_scaled['Date'] = samsung_stock['Date']
    #######################################################################################################################
    # 주식 자료 전처리
    #######################################################################################################################
                            Date, Data, Label = stock_preprocessing(samsung_scaled, t_view)
                            pd.concat(
                                (pd.DataFrame(Date),
                                 pd.DataFrame(Data.reshape(-1, t_view * col_num)),
                                 pd.DataFrame(Label)),
                                axis=1
                            ).to_excel(f'stock_pre_{t_view}_{col_num}_{cut}.xlsx', index=False)
    #######################################################################################################################
    # Train / Test 분리
    #######################################################################################################################
                        Data_train = Data[:-cut].astype(np.float32)
                        Data_test = Data[-cut:].astype(np.float32)
                        Label_train = Label[:-cut].astype(np.float32)
                        Label_test = Label[-cut:].astype(np.float32)
    #######################################################################################################################
    # Keras 모델
    #######################################################################################################################
                        model = Sequential()
                        model.add(Bidirectional(LSTM(lstm_num, input_shape=(Data_train.shape[1], Data_train.shape[2]), return_sequences=False)))
                        model.add(Dropout(0.0))
                        model.add(Dense(dense_num))
                        model.add(Dropout(0.0))
                        model.add(Dense(1))

                        model.compile(optimizer='adam', loss='mean_squared_error')

    #####
    ## optimizer 참고 : https://ganghee-lee.tistory.com/24
    ## loss 간략 참고 : https://needjarvis.tistory.com/567
    #####

    #######################################################################################################################
    # Keras 학습 및 예측
    #######################################################################################################################
                        # early_stop = keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True,)
                        # check_point = keras.callbacks.ModelCheckpoint('stock.h5', save_best_only=True)
                        history = model.fit(Data_train,Label_train, epochs=75, batch_size=4, validation_split=0.1,
                                            # callbacks=[early_stop, check_point]
                                            )
    #####
    ## batch 참고1 : https://goodtogreate.tistory.com/entry/Batch-%ED%81%AC%EA%B8%B0%EC%9D%98-%EA%B2%B0%EC%A0%95-%EB%B0%A9%EB%B2%95
    ## batch 참고2 : https://blog.lunit.io/2018/08/03/batch-size-in-deep-learning/
    #####

                        model.save('stock_keras.h5')
                        model = keras.models.load_model('stock_keras.h5')

                        pred = model.predict(Data_test)
                        pred_rev = reverse_min_max_scaling(samsung_stock['Close'], pred)
                        y_rev = reverse_min_max_scaling(samsung_stock['Close'], Label_test)
                        pd.DataFrame(pred).to_excel(f'stock_pred_{lks}.xlsx')
                        pd.DataFrame(pred_rev).to_excel(f'stock_pred_rev_{lks}.xlsx')
                        pd.DataFrame(Label_test).to_excel(f'stock_label_orig_{lks}.xlsx')
                        pd.DataFrame(y_rev).to_excel(f'stock_label_rev_{lks}.xlsx')



                        plt.figure(figsize=(12, 9))
                        plt.plot(y_rev, label = 'actual')
                        plt.plot(pred_rev, label = 'prediction')
                        plt.legend()
                        plt.savefig(f'{t_view}_{col_num}_{cut}_l{lstm_num}_d{dense_num}_{lks}.png', dpi=200)