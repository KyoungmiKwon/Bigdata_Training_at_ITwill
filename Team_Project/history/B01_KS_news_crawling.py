#######################################################################################################################
# 기사 크롤링 코드 (KS ver.)
#######################################################################################################################
# 네이버 증권 페이지(https://finance.naver.com/) - 종목 - 뉴스,공시
# 종목번호 {'삼성전자':'005930', 'LG전자':'066570', 'JYP Ent.':'035900', '와이지엔터테인먼트':'122870'}
# 종목간 기사수가 차이가 심함.
# 04/12(월) 기준 기사 페이지 수 [1160,357,17,20]
#######################################################################################################################
# import
#######################################################################################################################
import requests
from bs4 import BeautifulSoup
import pandas as pd

#######################################################################################################################
# 기사 페이지 주소
# 종목 번호 리스트 l / 기사 페이지수 k
# 종목별로 k값의 차이가 매우 큼.
# 눈에 보이는 페이지 이후에도 페이지가 시스템상으로는 존재하나 마지막쪽의 기사가 반복됨.
# 크롤링하는 날에 딱 그 페이지수에 맞추거나 조금 넉넉하게 잡고 받은뒤 중복되는 기사 제거하는 과정이 필요할 듯.
########################################################################################################################
arts = []
url1 = 'https://finance.naver.com'
# for l in ['005930','066570','035900','122870']:
for l in ['122870']:
    n = 0
    for k in range(1,31):
    # for k in [20]:
        try:
            url2 = f'/item/news_news.nhn?code={l}&page={k}&sm=title_entity_id.basic&clusterId='
            url  = url1+url2
            response = requests.get(url)
            html = response.text.strip()
            soup = BeautifulSoup(html,'html5lib')

#######################################################################################################################
# 메인 기사 i
# 한 페이지에 메인 기사 10개가 있으나 번호들이 조금 이상하게 번호가 있어서 20까지로 설정
# 번호가 넘어가면 에러가 생길까봐 try 구문을 사용.
#######################################################################################################################
            for i in range(1,20):
                try:
                    news_t = soup.select(f'body > div > table.type5 > tbody > tr:nth-of-type({i}) > td.title > a')
                    news_d = soup.select(f'body > div > table.type5 > tbody > tr:nth-of-type({i}) > td.date')
                    art_title = news_t[0].text.strip()
                    art_url   = url1 + news_t[0].get('href')
                    art_date  = news_d[0].text.strip()

                    art_response = requests.get(art_url)
                    art_html = art_response.text.strip()
                    art_soup = BeautifulSoup(art_html, 'html5lib')

                    art_main = art_soup.select('#news_read')
                    for tag in art_main[0].find_all('a'):
                        tag.string.replace_with('')
                    art_main = art_main[0].text.replace('관련뉴스해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.','').strip()

                    art = [art_title, art_url, art_date, art_main]
                    arts.append(art)

                    n += 1
                except:
                    pass

#######################################################################################################################
# 연관 기사들 j
# 한 페이지에 연관기사가 고정적으로 있는 것이 아니기에 try 구문을 사용.
#######################################################################################################################
            try:
                news_t = soup.select('tr.relation_lst td.title > a')
                news_d = soup.select('tr.relation_lst td.date')
                for j in range(0,20):
                    art_title = news_t[j].text.strip()
                    art_url   = url1 + news_t[j].get('href')
                    art_date  = news_d[j].text.strip()

                    art_response = requests.get(art_url)
                    art_html = art_response.text.strip()
                    art_soup = BeautifulSoup(art_html, 'html5lib')

                    art_main = art_soup.select('#news_read')
                    for tag in art_main[0].find_all('a'):
                        tag.string.replace_with('')
                    art_main = art_main[0].text.replace('관련뉴스해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.', '').strip()

                    art = [art_title, art_url, art_date, art_main]
                    arts.append(art)

                    n += 1
            except:
                pass
            print(f'종목번호 : {l}, {k} 페이지, {n} 번째 기사')
        except:
            pass

arts = pd.DataFrame(arts, columns=['art_title', 'art_url', 'art_date', 'art_main'])
# print(arts.iloc[0])
arts.drop_duplicates().to_csv("yg_test.csv", mode='w')
arts.drop_duplicates().to_excel("yg_test.xlsx")
# 중복행 제거 : .drop_duplicates()                    (https://www.delftstack.com/ko/howto/python-pandas/drop-duplicates-pandas/)
# csv로 저장 : .to_csv('파일명', mode='w')            (https://buttercoconut.xyz/74/)
# excel로 저장 : .to_excel('파일명')                  (https://hogni.tistory.com/19)
