# Dependencies
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
import pandas as pd
import uuid
import functions as fct
from datetime import datetime, timedelta
#from clean_dag import dag_clean, save_clean_file_task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import json
import ftfy

default_args = {
    'owner' : "Text-Mining_Project",
    # Lancer le DAG chaque jour
    'start_date' : datetime(2023, 1, 22),
    'depends_on_past' : False,
    # Si jamais l'éxecution fail, retenter 1 fois au bout de 5 minutes
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5)
}


class MyDag(DAG):
    def __init__(self, *args, **kwargs):
        conn = psycopg2.connect(user = "m140",password = "m140",host = "db-etu.univ-lyon2.fr",port = "5432",database = "m140")
        try:
            cur = conn.cursor()
            history = "SELECT * FROM historyclean"
            cur.execute(history)
            self.df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        except : 
            print ("Erreur lors de la récupération de la table PostgreSQL")
        super(MyDag, self).__init__(*args, **kwargs)

 
def alimente_dw(**kwargs):

    print("*****************************")
    print(kwargs['execution_date'].date())
    print("*****************************")

    df = kwargs['dag_run'].dag.df

    df['execution_date'] = kwargs['execution_date']
    #### table date #####
    df["id_date"] = df["date"].astype(str)
    df["id_date"] = df["id_date"].str.replace("-","")
    champs_date = ["month_str","month_num","year","date", "id_date"]
    df_date = df[champs_date].copy()
    df_date.drop_duplicates(keep='first', inplace=True)
    df_date.reset_index(drop=True, inplace=True)

    #### table client ####
    champs_client = ["country", "nuitee", "traveler_infos", "review_title", "positive_review", "negative_review", "usefulness_review", "delay_comment"]
    df_client = df[champs_client].copy()
    df_client.rename(columns={'country': 'country'}, inplace=True)
    df_client['id_client'] = df_client.apply(lambda _: uuid.uuid4(), axis=1)

    #### table hotel ####
    champs_hotel = ["hotel", "level_hotel"]
    df_hotel = df[champs_hotel].copy()
    df_hotel.drop_duplicates(keep='first', inplace=True)
    df_hotel.dropna(inplace=True)
    df_hotel['id_hotel'] = df_hotel.apply(lambda _: uuid.uuid4(), axis=1)
    df_hotel.reset_index(drop=True, inplace=True)

    #### table room ####
    champs_chambre = ["room_type", "hotel"]
    df_room = df[champs_chambre].copy()
    df_room.drop_duplicates(keep='first', inplace=True)
    df_room.reset_index(drop=True, inplace=True)
    #merge pour avoir id_hotel
    df_room=df_room.merge(df_hotel, on='hotel')
    df_room['id_room'] = df_room.apply(lambda _: uuid.uuid4(), axis=1)
    df_room.drop(columns=['hotel', 'level_hotel'], inplace=True)

    #### table res ####
    champs_res=["grade_review", "level_grade_review", "id_date", "room_type"]
    df_res = df[champs_res].copy()
    df_res.reset_index(drop=True, inplace=True)
    #merge pour avoir tous les id
    df_res['id_reservation'] = df_res.apply(lambda _: uuid.uuid4(), axis=1)
    df_res = pd.merge(df_res, df_room[["id_room", "room_type"]], how="left", on = ["room_type"])
    df_res.drop_duplicates(subset=['id_reservation'], inplace=True)
    df_res.reset_index(drop=True, inplace=True)
    df_res.drop(columns=['room_type'], inplace=True)
    df_res = pd.concat([df_res, df_client['id_client']], axis=1) 

    #### alimenter DW ####
    conn = psycopg2.connect(
          user = "m139",
          password = "m139",
          host = "db-etu.univ-lyon2.fr",
          port = "5432",
          database = "m139"
    )
    fct.insert_values(conn, df_date, 'date')
    fct.insert_values(conn, df_hotel, 'hotel')
    fct.insert_values(conn, df_room, 'room')
    fct.insert_values(conn, df_client, 'client')
    fct.insert_values(conn, df_res, 'reservation')



with MyDag( 'dag_dw' ,default_args = default_args, schedule_interval = '0 6 * * *') as dag_dw:

    # Tâche Airflow    

    alimente_dw_task = PythonOperator(
        task_id = 'alimente_dw',
        provide_context=True,
        python_callable = alimente_dw,
        dag = dag_dw)

#trigger_dag2 = TriggerDagRunOperator(task_id='trigger_dag2', trigger_dag_id='dag_dw', dag=dag_clean)


#save_clean_file_task.set_upstream(trigger_dag2)
#t_last.set_downstream(create_table_date_task)

alimente_dw_task