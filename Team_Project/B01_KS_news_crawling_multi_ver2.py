#######################################################################################################################
# 기사 크롤링 병렬화 코드 (KS ver.1)
#######################################################################################################################
# 네이버 증권 페이지(https://finance.naver.com/) - 종목 - 뉴스,공시
# 종목번호 {'삼성전자':'005930', 'LG전자':'066570', 'JYP Ent.':'035900', '와이지엔터테인먼트':'122870'}
# 종목간 기사수가 차이가 심함.
# 04/12(월) 기준 기사 페이지 수 [1160,357,17,20]
#######################################################################################################################
# import
#######################################################################################################################
import os
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import multiprocessing



#######################################################################################################################
# crawling 함수
########################################################################################################################
def crawl(l,m,n,result):
    ''' 종목 번호 l / 기사 시작 페이지-1 m'''
    arts = []
    url1 = 'https://finance.naver.com'
    try:
        m2=m
        while m < m2 + n:
            url2 = f'/item/news_news.nhn?code={l}&page={m+1}&sm=title_entity_id.basic&clusterId='
            url = url1 + url2
            response = requests.get(url)
            html = response.text.strip()
            soup = BeautifulSoup(html, 'html5lib')

            for i in range(1, 20):
                try:
                    news_t = soup.select(f'body > div > table.type5 > tbody > tr:nth-of-type({i}) > td.title > a')
                    news_d = soup.select(f'body > div > table.type5 > tbody > tr:nth-of-type({i}) > td.date')
                    art_title = news_t[0].text.strip()
                    art_url = url1 + news_t[0].get('href')
                    art_date = news_d[0].text.strip()

                    art_response = requests.get(art_url)
                    art_html = art_response.text.strip()
                    art_soup = BeautifulSoup(art_html, 'html5lib')

                    art_main = art_soup.select('#news_read')
                    for tag in art_main[0].find_all('a'):
                        tag.string.replace_with('')
                    art_main = art_main[0].text.replace('관련뉴스해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.', '').strip()

                    art = [l,art_title, art_url, art_date, art_main]
                    arts.append(art)
                except:
                    pass

            try:
                news_t = soup.select('tr.relation_lst td.title > a')
                news_d = soup.select('tr.relation_lst td.date')
                for j in range(0, 20):
                    art_title = news_t[j].text.strip()
                    art_url = url1 + news_t[j].get('href')
                    art_date = news_d[j].text.strip()

                    art_response = requests.get(art_url)
                    art_html = art_response.text.strip()
                    art_soup = BeautifulSoup(art_html, 'html5lib')

                    art_main = art_soup.select('#news_read')
                    for tag in art_main[0].find_all('a'):
                        tag.string.replace_with('')
                    art_main = art_main[0].text.replace('관련뉴스해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.', '').strip()

                    art = [l,art_title, art_url, art_date, art_main]
                    arts.append(art)
            except:
                pass
            m += 1
            print(f'{os.getpid()}번 프로세스 진행률')
            prog = int((m - m2) / n * 30)
            print(f'    {m2+1}|{prog*"*"+(30-prog)*"-"}|{m2+n}')
    except:
        pass
    result.append(arts)
    return None



#######################################################################################################################
# 본문
#######################################################################################################################
if __name__ == '__main__':
#   real
    # item_nums = ['005930','066570','035900','122870']
    # pages_limit = [1163, 358, 17, 20]
    # pages_size = 20
    # file_name = "210414"
#   test1
#     item_nums = ['122870']
#     pages_limit = [20]
#     pages_size = 5
#     file_name = "210414"
#   test2
    item_nums = ['066570','035900','122870']
    pages_limit = [358, 17, 20]
    pages_size = 20
    file_name="210414_lg,jyp,yg"

    pages = []
    for i in pages_limit:
        pages.append([j * pages_size for j in range(int(np.ceil(i / pages_size)))])
    print(pages)
#   중간부터 시작한다 할때 위의 for구문을 코멘트 처리하고 아래와같이 pages 리스트를 주면 된다.
#   예를들어 101 페이지부터 200 페이지까지 10페이지 단위로 쪼개서 가져오고 싶다면...
#   pages = [[100,110,120,130,140,150,160,170,180,190]]
#   여러 사람이 구간을 나눠서 하기 위한 이유도 있지만
#   한번에 너무 많은 작업을 쪼개 넣을 경우 에러가 남
#######################################################################################################################
    with multiprocessing.Manager() as manager:
        result = manager.list()

        processes=[]
        for item_num, page_tot in zip(item_nums, pages):
            for page_starts in page_tot:
                p = multiprocessing.Process(target=crawl, args=(item_num,page_starts,pages_size,result))
                p.start()
                processes.append(p)
        for process in processes:
            process.join()

        arts = []
        for i in result:
            arts.extend(i)

        arts = pd.DataFrame(arts, columns=['art_code','art_title', 'art_url', 'art_date', 'art_main'])
# 받는 속도가 느려서 멀티 프로세싱(병렬화) 방법을 강구해 보았음.
# 짜고 돌려보니 기분상 더 빨라진 기분이 듬.
# https://docs.python.org/ko/3.7/library/multiprocessing.html?highlight=manager#module-multiprocessing.managers
        arts.drop_duplicates(subset=['art_title'],ignore_index=True).to_excel(file_name+".xlsx", index=False)
# 같은 내용이라도 저장할때 엑셀이 용량이 훨씬 적음. 거의 1/4
# 뇌피셜이지만 아무래도 문자 인코딩의 차이일 것 같음
#######################################################################################################################