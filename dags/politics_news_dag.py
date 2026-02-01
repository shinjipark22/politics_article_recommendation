import sys
import os
from airflow import DAG 
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.news_crawler import crawl_naver_politics_by_date
# 기본 설정
default_args = {
    'owner': 'shinji',
    'depends_on_past': False,
    'start_date' : datetime(2026, 1, 26), # 수집 시작 날짜
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5) # 재시도 텀
}

# DAG 정의
with DAG(
    'politics_news_daily', # DAG ID
    default_args=default_args,
    description='매일 네이버 정치 뉴스를 수집하는 파이프라인',
    schedule_interval='@daily',
    catchup=True,
    tags=['politics', 'naver', 'project']
) as dag:

    crawling_task = PythonOperator(
        task_id='daily_crawl_task',

        # 실행할 파이썬 함수
        python_callable=crawl_naver_politics_by_date,

        # 날짜 전달
        op_kwargs={'target_date': '{{ ds_nodash }}'},
    )

    # 작업 순서
    crawling_task
