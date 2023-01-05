from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# scrapping = ... Scrapping fonction to add

with DAG("exe_scrapping", start_date = datetime(2023, 1, 1), schedule_interval = "@daily") as dag:
    
    scrapping_dag = PythonOperator(
        task_id = "new_scrap",
        python_callable = scrapping
    )