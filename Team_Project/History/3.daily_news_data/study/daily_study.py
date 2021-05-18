#######################################################################################################################
# Import Packages
#######################################################################################################################
import numpy as np
import pandas as pd
import os
import datetime

#######################################################################################################################
# 연습
#######################################################################################################################
# df = pd.read_excel('Data.xlsx')
# print(df.shape)
# print(df.columns)
# # ['No', 'Code', 'Date', 'Journal', 'Title', 'Text', 'In Charge', 'S',
# #        'Sentiment Dict', 'Polarity', 'Kobert', 'One-Hot']
# print(df['Date'].head())
# print(type(df['Date'][0]))
# # pandas column 날짜 타입으로 변환
# # https://hiio.tistory.com/30
# df['Date'] = pd.to_datetime(df['Date'])
# print(type(df['Date'][0]))
# # 날짜 구하기
# # https://kkumalog.tistory.com/42
# # 0:월 ~ 6:일
# print(df['Date'][0].weekday())
# dt1 = datetime.timedelta(days=1)
# print((df['Date'][0]-dt1).weekday())
# # datetime에서 필요한 요소요소 뽑아내기
# # https://datascienceschool.net/01%20python/02.15%20%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%97%90%EC%84%9C%20%EB%82%A0%EC%A7%9C%EC%99%80%20%EC%8B%9C%EA%B0%84%20%EB%8B%A4%EB%A3%A8%EA%B8%B0.html
# print(df['Date'][0].year)
# print(df['Date'][0].month)
# print(df['Date'][0].day)
# print(df['Date'][0].hour)
# print(df['Date'][0].minute)
# print(df['Date'][0].second)
# # 시작 일시, 끝 일시
# print(df.shape)
# d_init = df['Date'][0]
# d_fin = df['Date'][df.shape[0]-1]
# print(d_init, d_fin)
# # datetime을 str으로
# # https://pythonq.com/so/python/974555
# day1 = (d_init-dt1).strftime('%Y-%m-%d') +' 15:30'
# day2 = d_init.strftime('%Y-%m-%d') +' 15:30'
# print(day1, type(day1))
# print(day2, type(day2))
# # str을 datetime으로
# # https://www.delftstack.com/ko/howto/python/how-to-convert-string-to-datetime/
# day1_1 = datetime.datetime.strptime(day1, '%Y-%m-%d %H:%M')
# day2_1 = datetime.datetime.strptime(day2, '%Y-%m-%d %H:%M')
# print(day1_1)
# print(day2_1)
# # 날짜 범위 조건
# # https://www.delftstack.com/ko/howto/python-pandas/how-to-filter-dataframe-rows-based-on-the-date-in-pandas/
# print(df[df['Date'].between(day1_1,day2_1)])
#######################################################################################################################



#######################################################################################################################
# Import Data
#######################################################################################################################
df = pd.read_excel('Data.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
d_init = df['Date'][0]
d_fin = df['Date'][df.shape[0]-1]

d_init = datetime.datetime.strptime(d_init.strftime('%Y-%m-%d'), '%Y-%m-%d')
d_fin = datetime.datetime.strptime(d_fin.strftime('%Y-%m-%d'), '%Y-%m-%d')
print(d_init, d_fin)

d_1 = datetime.timedelta(days=1)
h_m = datetime.timedelta(hours=8, minutes=30)
h_p = datetime.timedelta(hours=15, minutes=30)
# print((d_now - d_1).weekday())
# print(d_now + d_1)
# print(d_now - h_m)
# print(d_now + h_p)

# print(d_now.weekday())
# print((d_now-2*d_1).weekday())
# 2, 44, 43, ...

# print(df.columns)
# # ['No', 'Code', 'Date', 'Journal', 'Title', 'Text', 'In Charge', 'S',
# #        'Sentiment Dict', 'Polarity', 'Kobert', 'One-Hot', 'Ensemble']
col_list = ['Sentiment Dict', 'Kobert', 'One-Hot', 'Ensemble']
temp_list = []
for col_name in col_list:
    d_now = d_init
    day_list = []
    all_list = []
    pos_list = []
    neg_list = []
    while d_now <= d_fin+d_1:
        # print(d_now)
        if d_now.weekday() == 0:
            d_now_1 = (d_now-2*d_1) - h_m
        else:
            d_now_1 = d_now - h_m
        d_now_2 = d_now + h_p
        all = len(df[df['Date'].between(d_now_1, d_now_2)])
        # print(df[df['Date'].between(d_now_1, d_now_2)])
        # print(df[df['Date'].between(d_now_1, d_now_2)].shape)
        # print(all)
        # print(df[df['Date'].between(d_now_1, d_now_2)])
        # print(df[df['Date'].between(d_now_1, d_now_2)]['Kobert'])
        # print(df[df['Date'].between(d_now_1, d_now_2)]['Kobert'].to_numpy())
        # print(np.sum(df[df['Date'].between(d_now_1, d_now_2)]['Kobert'].to_numpy()))
        pos = np.sum(df[df['Date'].between(d_now_1, d_now_2)][col_name].to_numpy())
        neg = all - pos
        day_list.append(d_now)
        all_list.append(all)
        pos_list.append(pos)
        neg_list.append(neg)
        d_now += d_1

    all_df = pd.DataFrame(all_list)
    all_df.columns = [f'{col_name}_all']
    pos_df = pd.DataFrame(pos_list)
    pos_df.columns = [f'{col_name}_pos']
    neg_df = pd.DataFrame(neg_list)
    neg_df.columns = [f'{col_name}_neg']
    temp = pd.concat((all_df,pos_df,neg_df), axis=1)
    temp[f'{col_name}_ratio'] = 0.5 + (temp[f'{col_name}_pos']-temp[f'{col_name}_neg'])/temp[f'{col_name}_all']/2
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
