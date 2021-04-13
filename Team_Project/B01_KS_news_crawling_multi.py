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
import multiprocessing

#######################################################################################################################
# crawling 함수
########################################################################################################################
def crawl(l,k, result):
    ''' 종목 번호 l / 기사 페이지 k'''
    arts = []
    url1 = 'https://finance.naver.com'
    try:
        url2 = f'/item/news_news.nhn?code={l}&page={k}&sm=title_entity_id.basic&clusterId='
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

                art = [art_title, art_url, art_date, art_main]
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

                art = [art_title, art_url, art_date, art_main]
                arts.append(art)
        except:
            pass
    except:
        pass
    result.append(arts)
    return None

# item_nums = ['005930','066570','035900','122870']
# pages = [1159, 358, 17, 20]
# 와이지엔터테인먼트 기준으로 테스팅.
item_nums = ['122870']
pages = [20]

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        result = manager.list()

        processes=[]
        for item_num, page_tot in zip(item_nums, pages):
            for page in range(page_tot):
                p = multiprocessing.Process(target=crawl, args=(item_num,(page+1),result))
                p.start()
                processes.append(p)
        for process in processes:
            process.join()

        arts = []
        for i in result:
            arts.extend(i)

        arts = pd.DataFrame(arts, columns=['art_title', 'art_url', 'art_date', 'art_main'])
# 받는 속도가 느려서 멀티 프로세싱(병렬화) 방법을 강구해 보았음.
# 짜고 돌려보니 기분상 더 빨라진 기분이 듬.
# https://docs.python.org/ko/3.7/library/multiprocessing.html?highlight=manager#module-multiprocessing.managers
        arts.drop_duplicates().to_csv("yg_test.csv", mode='w')
        arts.drop_duplicates().to_excel("yg_test.xlsx")