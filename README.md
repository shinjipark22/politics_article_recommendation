# 📰 정치·사회적 편향을 고려한 그래프 기반 다관점 뉴스 추천 시스템
### (Graph-based Multi-perspective News Recommendation System considering Political & Social Bias)

Apache Airflow를 사용하여 네이버 뉴스 '정치' 섹션의 기사들을 매일 자동으로 수집하고, 분석 가능한 데이터(CSV)로 저장하는 데이터 파이프라인 프로젝트입니다. 
추후 그래프 기반 뉴스 추천 시스템 확장을 위해 핵심 로직이 모듈화(`src`)되어 있습니다.

---

## 📌 주요 기능 (Key Features)

* **자동화된 파이프라인**: Airflow DAG를 통해 매일 자정(`@daily`)에 자동으로 크롤링이 수행됩니다.
* **상세 데이터 수집**: 단순 제목/링크뿐만 아니라 **본문(Content), 기자명, 언론사, 기사 작성/수정 시간, 뉴스 ID** 등 상세 정보를 수집합니다.
* **데이터 정제**: 뉴스 본문 내의 불필요한 HTML 태그, 광고 스크립트, 공백 등을 제거하여 분석하기 좋은 형태로 가공합니다.
* **모듈화된 구조**: 스케줄링(`dags`)과 핵심 로직(`src`)을 분리하여 유지보수성과 확장성을 높였습니다.
* **과거 데이터 수집 (Backfill)**: `catchup=True`로 기본 설정이 되어있으며, **2025년 8월 1일**부터 현재까지 누락된 데이터를 자동으로 수집합니다. 만약 과거 데이터를 다운받고싶지 않다면 `catchup=False`로 바꿔주세요.
* **CSV 저장 및 최적화**: 수집된 데이터는 `data/processed`에 저장되며, 용량 관리를 위해 전처리된 텍스트로 기존 컬럼을 덮어쓰고 엑셀 깨짐 방지(`utf-8-sig`) 처리를 수행합니다.

---

## 📂 프로젝트 구조 (Project Structure)

```bash
politics_article_recommendation_project/
├── dags/
│   └── politics_news_dag.py  # Airflow DAG 정의 (스케줄링 담당)
├── src/                      # [Core] 핵심 로직 모듈
│   ├── news_crawler.py       # 네이버 뉴스 상세 크롤링 로직
│   ├── preprocessor.py       # 텍스트 전처리 및 정제 유틸리티
│   └── graph/                # (예정) 그래프 임베딩 및 모델링 폴더
├── data/                     # 수집된 CSV 파일 저장소 (raw/processed)
├── requirements.txt          # 의존성 패키지 목록
├── .gitignore                # Git 제외 설정 (데이터 파일 및 Airflow DB 포함)
└── README.md                 # 프로젝트 설명서
```

## 🤝 커밋 컨벤션 (Commit Convention)

협업 시 변경 사항을 명확히 파악하기 위해 아래의 머리말을 사용하여 커밋 메시지를 작성합니다.

* **`[FEAT]`**: 새로운 기능 추가 (예: 새로운 데이터 로더, 모델 구조 변경)
* **`[EXPERIMENTS]`**: 모델 학습 실험 및 하이퍼파라미터 튜닝 관련 변경
* **`[FIX]`**: 버그 수정
* **`[DOCS]`**: 문서 수정 (README, 주석 등)
* **`[REFACTOR]`**: 코드 리팩토링 (기능 변경 없는 구조 수정)
* **`[CHORE]`**: 패키지 매니저 설정, 환경 변수 등 단순 설정 변경
---

## 🛠️ 데이터 전처리 상세 (Data Preprocessing)

수집된 원본 뉴스 데이터를 LLM 분석 및 그래프 데이터베이스 구축에 최적화된 형태로 가공하기 위해 `src/preprocessor.py`를 통해 다음과 같은 정밀 전처리를 수행합니다.

### 1. 텍스트 정제 및 노이즈 제거 (Noise Removal)
* **메타데이터 및 방송 태그 제거**: 본문 내 포함된 `[앵커]`, `[리포트]`, `(서울=연합뉴스)`, `<저작권자...>` 등 기사 맥락과 무관한 방송용 태그와 출처 표기를 정규표현식으로 완벽히 제거합니다.
* **이메일 및 기자 패턴 정제**: 본문 중간이나 끝에 삽입된 기자의 이메일 주소와 도입부의 뉴스 작성자 패턴을 제거합니다.
* **문맥 보존형 기호 정제**: LLM이 문맥을 정확히 파악할 수 있도록 문장 부호(`.`, `,`, `?`, `!`)와 인용구, 수치(`%`) 등은 남기고 분석에 불필요한 특수 기호만 선택적으로 제거합니다.


### 2. 기자명 정규화 (Reporter Name Normalization)
* **그래프 노드 통일성 확보**: 그래프 데이터베이스 구축 시 인물 노드의 중복을 방지하기 위해 직함을 제거하고 순수 성명만 추출하여 정규화합니다.

---

## 🤝 협업 가이드 (Contribution Guide)

팀 프로젝트의 효율적인 코드 관리와 로직 개발을 위해 아래 규칙을 준수합니다.

### 1. 이슈 및 브랜치 전략 (Issue & Branch Strategy)
본 프로젝트는 **"1 Issue - 1 Branch"** 원칙을 따릅니다.
* **작업 시작**: GitHub **Issues**에서 새로운 이슈를 생성하고 작업 내용을 할당받습니다.
* **브랜치 생성**: 생성된 이슈 번호와 본인 초성을 조합하여 브랜치를 생성합니다.
    * **형식**: `본인이름초성-기능명` (예: `psj-graph-embedding`)
* **브랜치 설명**: 생성된 브랜치의 작업 내용은 반드시 해당 GitHub Issue에 상세히 기록합니다.
* **워크플로우**: `main` 최신화(`pull`) → 브랜치 생성 → 작업 후 `push` → `Pull Request(PR)` 생성 및 이슈 번호 연결 → 팀장 승인 후 `Merge`



### 2. 데이터 관리 및 보안
* **데이터 파일 (`data/`)**: 크롤링된 데이터는 개인 로컬 환경에서 관리하며, **GitHub에는 업로드하지 않습니다.** (각 팀원은 8월 1일치부터 데이터를 각자 수집해야 합니다.)
* **환경 변수**: API Key 등 민감한 정보는 별도 파일을 통해 관리하며 절대 커밋하지 않습니다.

---

## 🛠️ 설치 및 실행 방법 (Installation & Usage)

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv airflow_env
source airflow_env/bin/activate

# 필수 패키지 설치
pip install -r requirements.txt --constraint "[https://raw.githubusercontent.com/apache/airflow/constraints-2.10.2/constraints-3.12.txt](https://raw.githubusercontent.com/apache/airflow/constraints-2.10.2/constraints-3.12.txt)"
```

### 2. Airflow 실행
```bash
# 현재 폴더를 Airflow 홈으로 설정
export AIRFLOW_HOME=$(pwd)

# Airflow 독립 실행모드 가동
airflow standalone
```

---

## 📊 수집 데이터 명세 (Data Schema)

| 컬럼명 | 설명 | 예시 |
| :--- | :--- | :--- |
| **news_id** | 뉴스 고유 ID | `052-0002308619` |
| **작성일시** | 기사 최초 발행 시간 | `2026-01-31 23:39:51` |
| **수정일시** | 기사 최종 수정 시간 | `2026-02-01 01:10:05` |
| **언론사** | 발행 언론사 명칭 | `YTN` |
| **기자명** | 작성 기자 성함 (정규화 완료) | `홍선기` |
| **제목** | 뉴스 기사 제목 | `조문 정국 마무리 수순...다시 떠오르는 여야 갈등` |
| **본문** | 기사 내용 (전처리 완료) | `고 이해찬 전 총리의 추모 기간 동안...` |
| **이미지URL** | 대표 이미지 주소 | `https://imgnews.pstatic.net/...` |
| **원문링크** | 언론사 공식 홈페이지 링크 | `https://www.ytn.co.kr/...` |
| **네이버링크** | 네이버 뉴스 페이지 링크 | `https://n.news.naver.com/...` |

---

## 👨‍💻 작성자 (Author)

* **Shinji Park** (shinjipark22)