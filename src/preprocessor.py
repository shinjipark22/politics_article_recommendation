import re
import os
import pandas as pd

class NewsPreprocessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        """
        [본문 전처리]
        LLM이 읽기 좋게 문맥(.,?!)은 남기고
        방송 태그([앵커]), 기자 이메일, 특수 기호 등 노이즈만 제거
        """
        if not isinstance(text, str):
            return ""

        # 1. 이메일 제거 (본문 중간/끝에 있는 이메일)
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)

        # 2. 방송/기사 메타데이터 제거 (대괄호, 괄호, 꺾쇠)
        # 예: [앵커], [리포트], (서울=연합뉴스), <저작권자...>
        text = re.sub(r'\[.*?\]', '', text) # [ ... ] 제거
        text = re.sub(r'\(.*?\)', '', text) # ( ... ) 제거
        text = re.sub(r'\<.*?\>', '', text) # < ... > 제거

        # 3. 특수문자 기호 제거 (인터뷰 기호 등)
        # 예: ▶, ▷, ※, -, =, + 등 제거
        # LLM 문맥 파악을 위해 . , ? ! " ' % ~ 는 살림
        text = re.sub(r'[^가-힣a-zA-Z0-9\s\.\,\?\!\'\"\%~]', ' ', text)

        # 4. "기자 = " 패턴 제거 (뉴스 도입부에 많음)
        # 예: "홍길동 기자 =" -> 제거
        text = re.sub(r'[가-힣]{2,4}\s*(기자|특파원|논설위원)\s*=', '', text)

        # 5. 다중 공백을 하나로 줄이고 앞뒤 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def clean_reporter(self, text):
        """
        [기자명 전처리]
        '김동성 기자 estar@etnews.com' -> '김동성' 으로 추출
        그래프 노드 통일성을 위해 이름만 남김
        """
        if not isinstance(text, str):
            return ""

        # 1. 이메일 제거
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)

        # 2. 직함 및 불필요한 단어 제거 리스트
        remove_words = ['기자', '특파원', '논설위원', '인턴기자', '선임기자', '드리머', 'PD', '앵커']
        for word in remove_words:
            text = text.replace(word, '')

        # 3. 한글과 영문 이름만 남기고 나머지(특수문자, 숫자) 제거
        text = re.sub(r'[^가-힣a-zA-Z]', ' ', text)

        # 4. 공백 제거 (이름은 붙여쓰기)
        text = text.replace(' ', '').strip()
        
        return text

def preprocess_daily_news(target_date):
    """
    [Airflow 연동 함수]
    1. data/raw 폴더에서 원본 CSV를 읽어옴
    2. 전처리 수행
    3. data/processed 폴더에 결과 저장
    """
    # 프로젝트 루트 경로 찾기
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    
    # [수정된 부분] 폴더 경로를 raw와 processed로 분리
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    
    # processed 폴더가 없으면 생성 (에러 방지)
    os.makedirs(processed_dir, exist_ok=True)

    # 파일 경로 설정 
    input_file = os.path.join(raw_dir, f'naver_politics_{target_date}.csv')
    output_file = os.path.join(processed_dir, f'naver_politics_{target_date}.csv')

    if not os.path.exists(input_file):
        print(f"[Skip] 원본 파일이 없습니다: {input_file}")
        return

    print(f"[Start] 데이터 전처리 시작: {input_file}")

    # 데이터 로드
    df = pd.read_csv(input_file)
    preprocessor = NewsPreprocessor()

    # 1. 본문 전처리
    if '본문' in df.columns:
        print(" - 본문 정제 중...")
        df['본문_전처리'] = df['본문'].fillna('').apply(preprocessor.clean_text)

    # 2. 기자명 전처리
    if '기자명' in df.columns:
        print(" - 기자명 정규화 중...")
        df['기자명_전처리'] = df['기자명'].fillna('').apply(preprocessor.clean_reporter)

    # 3. 저장 (processed 폴더에 저장)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[Done] 전처리 완료 및 저장: {output_file}")
