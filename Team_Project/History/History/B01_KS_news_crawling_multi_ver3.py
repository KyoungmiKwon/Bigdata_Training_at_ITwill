#######################################################################################################################
# 기사 크롤링 병렬화 코드 (KS ver.1)
#######################################################################################################################
# 네이버 증권 페이지(https://finance.naver.com/) - 종목 - 뉴스,공시
# 종목번호 {'삼성전자':'005930', 'LG전자':'066570', 'JYP Ent.':'035900', '와이지엔터테인먼트':'122870'}
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
#######################################################################################################################
def bs(url):
    response = requests.get(url)
    html = response.text.strip()
    soup = BeautifulSoup(html, 'html5lib')
    return soup

def crawl(l,m,n,result):
    ''' 종목 번호 l / 기사 시작 페이지-1 m'''
    arts = []
    url1 = 'https://finance.naver.com'
    try:
        m2=m
        while m < m2 + n:
            url2 = f'/item/news_news.nhn?code={l}&page={m+1}&sm=title_entity_id.basic&clusterId='
            url = url1 + url2
            news_list=bs(url)
            news_t = news_list.select(f'.title > a')
            news_i = news_list.select(f'.info')
            news_d = news_list.select(f'.date')
            for i in range(len(news_t)):
                try:
                    art_d = news_d[i].text.strip()
                    art_i = news_i[i].text.strip()
                    art_t = news_t[i].text.strip()
                    art_u = url1 + news_t[i].get('href')

                    news_content = bs(art_u)
                    art_m = news_content.select('#news_read')[0]
                    for tag in art_m.find_all('a'):
                        tag.string.replace_with('')
                    art_m = art_m.text.replace('관련뉴스해당 언론사에서 선정하며 언론사 페이지(아웃링크)로 이동해 볼 수 있습니다.', '').strip()

                    art = [l, art_d, art_i, art_t, art_u, art_m]
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
#    lg,jyp,yg
#     item_nums = ['066570','035900','122870']
#     pages_limit = [358, 17, 20]
#     pages_size = 20
#     file_name="210414_lg,jyp,yg"
#    samsung
    item_nums = ['005930']
    pages_limit = [1163]
    pages_size = 75
    file_name="210414_sam"

    pages = []
    for i in pages_limit:
        pages.append([j * pages_size for j in range(int(np.ceil(i / pages_size)))])
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

        arts = pd.DataFrame(arts, columns=['code','date', 'journal', 'title', 'url', 'text'])
        arts.drop_duplicates(subset=['title'],ignore_index=True).to_excel(file_name+".xlsx", index=False)
#######################################################################################################################
