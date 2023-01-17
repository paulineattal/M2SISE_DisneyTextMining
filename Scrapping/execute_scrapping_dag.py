from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

# Propriétés du DAG

default_args = {
    'owner' : "Text-Mining_Project",
    
    # Lancer le DAG chaque jour
    'start_date' : datetime(2023, 1, 1),
    'depends_on_past' : False,

    # Si jamais l'éxecution fail, retenter 1 fois au bout de 5 minutes
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5)
}

dag = DAG(
    'scrapping',
    default_args = default_args,

    # Executer tous les jours à minuit
    schedule_interval = '0 0 * * *' # on peut le modifier par timedelta(hours=1) si on veut faire des tests chaque heure
)


def scrapping():

    conn = psycopg2.connect(
        user = "m139",
        password = "m139",
        host = "db-etu.univ-lyon2.fr",
        port = "5432",
        database = "m139"
    )

    cur = conn.cursor()

    ### Ajouter le code pour récupérer la database pour chaque hotel

    ### Ajouter le code du scrapping

    ### Ajouter le code pour insérer le scrapping dans la database


scrapping_task = PythonOperator(
    task_id = 'scrapping',
    python_callable = scrapping,
    dag = dag)