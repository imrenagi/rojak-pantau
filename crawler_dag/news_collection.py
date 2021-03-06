from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable


default_args = {
    'owner': 'imre',
    'depends_on_past': True,
    'start_date': datetime(2018, 8, 13),
    'email': ['imre.nagi2812@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('news_collection_v1', default_args=default_args)

# t1, t2 and t3 are examples of tasks created by instantiating operators
detik_collection = BashOperator(
    task_id='detiknews_collection',
    bash_command="""
        cd %s/crawler_dag/crawler/rojak_pantau/spiders && scrapy crawl pilpres_2019_detiknewscom
    """ % (Variable.get('etl_dags_folder')),
    dag=dag)

kompascom_collection = BashOperator(
    task_id='kompascom_collection',
    bash_command="""
        cd %s/crawler_dag/crawler/rojak_pantau/spiders && scrapy crawl pilpres_2019_kompascom
    """ % (Variable.get('etl_dags_folder')),
    dag=dag)

republikacoid_collection = BashOperator(
    task_id='republikacoid_collection',
    bash_command="""
        cd %s/crawler_dag/crawler/rojak_pantau/spiders && scrapy crawl pilpres_2019_republikacoid
    """ % (Variable.get('etl_dags_folder')),
    dag=dag)

tribunnews_collection = BashOperator(
    task_id='tribunnews_collection',
    bash_command="""
        cd %s/crawler_dag/crawler/rojak_pantau/spiders && scrapy crawl pilpres_2019_tribunnewscom
    """ % (Variable.get('etl_dags_folder')),
    dag=dag)

pikiran_rakyat_collection = BashOperator(
    task_id='pikiran_rakyat_collection',
    bash_command="""
        cd %s/crawler_dag/crawler/rojak_pantau/spiders && scrapy crawl pilpres_2019_pikiranrakyat
    """ % (Variable.get('etl_dags_folder')),
    dag=dag)

detik_collection.set_downstream(kompascom_collection)
kompascom_collection.set_downstream(republikacoid_collection)
republikacoid_collection.set_downstream(tribunnews_collection)
tribunnews_collection.set_downstream(pikiran_rakyat_collection)
