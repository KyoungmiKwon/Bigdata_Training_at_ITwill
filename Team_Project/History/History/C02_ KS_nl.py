# 1차 조사 (컴퓨터 박살내기 전)
#######################################################################################################################
# konlpy 패키지 내 형태소 분석 세부 패키지들
#   공식 홈페이지, 각 패키지들의 분석 예시를 볼수 있음
#       https://konlpy-ko.readthedocs.io/ko/v0.4.3/api/konlpy.tag/
#   패키지 별 처리 결과물 예시2 - 조금더 보기 편한듯?
#       https://datascienceschool.net/03%20machine%20learning/03.01.02%20KoNLPy%20%ED%95%9C%EA%B5%AD%EC%96%B4%20%EC%B2%98%EB%A6%AC%20%ED%8C%A8%ED%82%A4%EC%A7%80.html
#   패키지 별 장단점 및 특징
#       https://velog.io/@metterian/%ED%95%9C%EA%B5%AD%EC%96%B4-%ED%98%95%ED%83%9C%EC%86%8C-%EB%B6%84%EC%84%9D%EA%B8%B0POS-%EB%B6%84%EC%84%9D-3%ED%8E%B8.-%ED%98%95%ED%83%9C%EC%86%8C-%EB%B6%84%EC%84%9D%EA%B8%B0-%EB%B9%84%EA%B5%90
#   Mecab이 빠르고 정확도가 괜찮은 편이라는 듯 합니다. 뭔가 사전도 따로 손 볼 수 있다는것 같고...

#   ☆★☆ khaiii - 카카오에서 만든것 ☆★☆
#       https://banana-media-lab.tistory.com/entry/colab%EC%97%90%EC%84%9C-khaiii-%ED%98%95%EB%B6%84%EC%84%9D%EA%B8%B0-%EC%84%A4%EC%B9%98%ED%95%B4%EC%84%9C-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0
#   간단한 사용법 참고 페이지
#       https://jeongwookie.github.io/2019/11/17/191117-khaiii-korean-tokenizer/
#   ☆★☆ 한국어 전처리 아주친절한 설명 - khaiii 사용 ☆★☆
#       http://aidev.co.kr/nlp/9480
#       ☆★☆ https://colab.research.google.com/drive/1FfhWsP9izQcuVl06P30r5cCxELA1ciVE?usp=sharing
#   khaiii 윈도우에서 사용할 꼼수
#       https://corytips.tistory.com/185?category=658851
#       https://corytips.tistory.com/186?category=658851
#       https://corytips.tistory.com/187?category=658851
#       https://corytips.tistory.com/188?category=658851
#   전반적인 설명
#       https://wikidocs.net/92961
#   ☆★☆ 형태소 품사 태그표 ☆★☆
#       http://kkma.snu.ac.kr/documents/?doc=postag
#######################################################################################################################
# 2차 조사 (컴퓨터 박살낸 후)
#######################################################################################################################
#   1. NLP(Natural Language Processing, 자연어처리)란?
#       텍스트에서 의미있는 정보를 분석, 추출하고 이해하는 일련의 기술집합입니다.
#       https://konlpy-ko.readthedocs.io/ko/v0.4.3/start/
#
#   2. 형태소 분석 및 품사 태깅
#       형태소 분석 이란 형태소를 비롯하여, 어근, 접두사/접미사, 품사(POS, part-of-speech) 등 다양한 언어적 속성의 구조를 파악하는 것입니다.
#       가. 품사 태깅:
#           1) 형태소의 뜻과 문맥을 고려하여 그것에 마크업을 하는 일
#               가방에 들어가신다 -> 가방/NNG + 에/JKM + 들어가/VV + 시/EPH + ㄴ다/EFN
#           2) 한국어 품사 태그 비교표
#               가) 간단한 예시까지 포함된 한눈에 보기 어려운 표 (구글 시트)
#                   https://docs.google.com/spreadsheets/d/1OGAjUvalBuX-oZvZ_-9tEfYD2gQe7hTGsgUpiiBSXI8/edit#gid=0
#               나) 예시는 없으나 한눈에 들어오는 표 (페이지)
#                   http://kkma.snu.ac.kr/documents/?doc=postag
#               다) 일단 페이지 참조는 붙여놨지만 패키지마다 조금씩 태그 분류들이 다른것으로 보임. 사용할 패키지에 따라 다시 확인할 필요성.
#       나. 품사 태깅 클래스 간 비교
#           1) 로딩 시간: 사전 로딩을 포함하여 클래스를 로딩하는 시간.
#               (KoNLPy의 클래스간 비교, khaiii는 KoNLPy에 의존성이 없어 여기에 자료가 없음.)
#               Kkma: 5.6988 secs
#               Komoran: 5.4866 secs
#               Hannanum: 0.6591 secs
#               Twitter: 1.4870 secs
#               Mecab: 0.0007 secs
#           2) 실행시간: 10만 문자의 문서를 대상으로 각 클래스의 pos 메소드를 실행하는데 소요되는 시간.
#               (KoNLPy의 클래스간 비교, khaiii는 KoNLPy에 의존성이 없어 여기에 자료가 없음.)
#               Kkma: 35.7163 secs
#               Komoran: 25.6008 secs
#               Hannanum: 8.8251 secs
#               Twitter: 2.4714 secs
#               Mecab: 0.2838 secs
#           3) khaiii를 포함한 시간, 성능 비교 페이지 (https://iostream.tistory.com/144)
#               가) 속도 : mecab -> khaiii
#               나) 안띄어쓰기, 자소분리, 오탈자의 문제 시 패키지마다 성능 차이가 남.
#                   (신문기사라 큰 문제 없을 것으로 예상)
#           4) 그 외
#               가) KoBERT   : 구글의 BERT + sk텔레콤
#               나) KoGPT-2  : 아마존웹서비스(aws) + sk텔레콤, 하지만 우리의 용도와는 조금 다른 용도로 쓰이는 듯 하다.
#                   오픈소스 공개(2020년도 기사, https://www.aitimes.kr/news/articleView.html?idxno=16213)
#           5) 결론
#               KoNLPy에서는 Mecab이 가장 좋다고 하며, 몇몇 페이지에서 khaiii가 가장 성능이 좋다는 이야기들이 있다.
#               mecab과 khaiii 모두 뉴스 기사 카테고리 분류하는 경우 95%의 성능을 보인다고 함 (https://lsjsj92.tistory.com/410)
#       다. 사전
#           사전은 대부분 말뭉치 를 이용해 구축되었으며 형태소 분석 및 품사 태깅 를 하는데 사용됩니다.
#           이게 중요 할 수도 있는 이유는 연예 기사에 연예인, 그룹명, 엔터명 같은 고유명사의 형태소 분석 및 품사 태깅에 문제가 생길수 있기 때문
#           위 검색 결과 mecab 혹은 khaiii를 사용하는 것이 가장 좋아보이므로 해당 패키지들에 대해 알아보았습니다.
#               mecab   (https://bitbucket.org/eunjeon/mecab-ko-dic/src/ce04f82ab0083fb24e4e542e69d9e88a672c3325/final/user-dic/?at=master)
#               khaiii  (https://hanshuginn.blogspot.com/2019/02/khaiii.html)
#               참고     (https://yoonchanheee.wordpress.com/2020/07/09/preprocessing-%EB%B3%B5%ED%95%A9-%EB%AA%85%EC%82%AC-%EC%B6%94%EC%B6%9C-%ED%98%95%ED%83%9C%EC%86%8C-%EB%B6%84%EC%84%9D%EA%B8%B0-%EC%82%AC%EC%9A%A9%EC%9E%90-%EC%82%AC%EC%A0%84-%EB%93%B1%EB%A1%9D/)
#######################################################################################################################
# mecab과 khaiii 설치 및 간단한 한 문장으로 하는 테스트는 수행 해보았음.
# 1차 조사때 한국어 전처리 프로세스 전반에 대해 작성된 colab문서가 있는데 그 순서를 따라가면 무리 없이 진행 가능할 것으로 보임.
# (https://colab.research.google.com/drive/1FfhWsP9izQcuVl06P30r5cCxELA1ciVE?usp=sharing#scrollTo=8nIXezslMdDC)
#   문장분리          kss                 굳이 문장을 분리할 필요가 있을까요?
#   띄어쓰기          PyKoSpacing         뉴스기사인데 필요할까요?
#   맞춤법검사        hanspell            뉴스기사라도 이건 필요할지도.
#   반복되는 문자     soynlp              뉴스기사인데 필요할까요?
#   외래어            ???                 뉴스기사라도 이건 필요할지도.
#   형태소 쪼개기     mecab or khaiii
#   주요 품사만 남기기
#   동사 원형으로 복원
#   불용어 제거
# 솔직히 저 colab파일이 너무 잘 만들어놔서 데이터 불러오는 것까지만 잘하면 그냥 그대로 써도 될 정도로 보입니다.