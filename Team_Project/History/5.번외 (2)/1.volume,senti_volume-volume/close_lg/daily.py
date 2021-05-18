#######################################################################################################################
# Import Packages
#######################################################################################################################
import numpy as np
import pandas as pd
import os
import datetime
######################################################################################################################
# Import Data, timedelta setting
#######################################################################################################################
samsung_url = 'Data.xlsx'
samsung_stock = pd.read_excel(samsung_url, header=0).drop('Change', axis=1)

df = pd.read_excel('Data2.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
d_init = df['Date'][0]
d_fin = df['Date'][df.shape[0]-1]

d_init = datetime.datetime.strptime(d_init.strftime('%Y-%m-%d'), '%Y-%m-%d')
d_fin = datetime.datetime.strptime(d_fin.strftime('%Y-%m-%d'), '%Y-%m-%d')

d_1 = datetime.timedelta(days=1)
h_m = datetime.timedelta(hours=8, minutes=30)
h_p = datetime.timedelta(hours=15, minutes=30)

######################################################################################################################
# Counting
#######################################################################################################################
# # ['No', 'Code', 'Date', 'Journal', 'Title', 'Text', 'In Charge', 'S',
# #        'Sentiment Dict', 'Polarity', 'Kobert', 'One-Hot', 'Ensemble']
col_list = ['Sentiment Dict', 'Kobert', 'One-Hot', 'Ensemble']
temp_list = []
for col_name in col_list:
    d_now = d_init- d_1
    day_list = []
    all_list = []
    pos_list = []
    neg_list = []

    while d_now <= d_fin+d_1:
        d_now_1 = d_now
        d_now += d_1
        while len(samsung_stock[samsung_stock['Date']==d_now]) == 0:
            d_now += d_1

        d_now_2 = d_now
        d_now_s = d_now_1 + h_p
        d_now_e = d_now_2 + h_p

        all = len(df[df['Date'].between(d_now_s, d_now_e)])
        pos = np.sum(df[df['Date'].between(d_now_s, d_now_e)][col_name].to_numpy())
        neg = all - pos
        day_list.append(d_now_2)
        all_list.append(all)
        pos_list.append(pos)
        neg_list.append(neg)
        d_now = d_now_2

    all_df = pd.DataFrame(all_list)
    all_df.columns = [f'{col_name}_all']
    pos_df = pd.DataFrame(pos_list)
    pos_df.columns = [f'{col_name}_pos']
    neg_df = pd.DataFrame(neg_list)
    neg_df.columns = [f'{col_name}_neg']
    temp = pd.concat((all_df,pos_df,neg_df), axis=1)
    temp[f'{col_name}'] = 0.5 + (temp[f'{col_name}_pos']-temp[f'{col_name}_neg'])/temp[f'{col_name}_all']/2
    temp_list.append(temp)

Date = pd.DataFrame(day_list)
Date.columns = ['Date']
pd.concat(
    (Date,
     temp_list[0],
     temp_list[1],
     temp_list[2],
     temp_list[3]),
     axis=1
     ).to_excel(f'daily_sentiment.xlsx', index=False)

df_daily = pd.concat(
    (Date,
     temp_list[0][temp_list[0].columns[3]],
     temp_list[1][temp_list[1].columns[3]],
     temp_list[2][temp_list[2].columns[3]],
     temp_list[3][temp_list[3].columns[3]]),
     axis=1
     )



df_join = pd.merge(samsung_stock, df_daily, left_on='Date', right_on='Date', how='right')
df_join.to_excel('join.xlsx',index=False)