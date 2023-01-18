# Dependencies
from airflow import DAG
from airflow.operators.python import PythonOperator
import psycopg2
import pandas as pd
import uuid
import functions as fct


default_args = {
    'owner' : "Text-Mining_Project",
    # Lancer le DAG chaque jour
    'start_date' : datetime(2023, 1, 17),
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

 
def create_table_date(**kwargs):
    df = kwargs['dag_run'].dag.df

    df["id_date"] = df["date"].astype(str)
    df["id_date"] = df["id_date"].str.replace("-","")
    champs_date = ["month_str","month_num","year","date", "id_date"]
    df_date = df[champs_date].copy()
    df_date.drop_duplicates(keep='first', inplace=True)
    df_date.reset_index(drop=True, inplace=True)

    kwargs['dag_run'].dag.df_date = df_date



def create_table_client(**kwargs):
    df = kwargs['dag_run'].dag.df

    champs_client = ["Country", "nuitee", "traveler_infos", "review_title", "positive_review", "negative_review", "usefulness_review", "delay_comment"]
    df_client = df[champs_client].copy()
    df_client.rename(columns={'Country': 'country'}, inplace=True)
    df_client['id_client'] = df_client.apply(lambda _: uuid.uuid4(), axis=1)

    kwargs['dag_run'].dag.df_client = df_client
    

def create_table_hotel(**kwargs):
    df = kwargs['dag_run'].dag.df

    champs_hotel = ["hotel", "level_hotel"]
    df_hotel = df[champs_hotel].copy()
    df_hotel.drop_duplicates(keep='first', inplace=True)
    df_hotel.dropna(inplace=True)
    df_hotel['id_hotel'] = df_hotel.apply(lambda _: uuid.uuid4(), axis=1)
    df_hotel.reset_index(drop=True, inplace=True)
    
    kwargs['dag_run'].dag.df_hotel = df_hotel


def create_table_chambre(**kwargs):
    df = kwargs['dag_run'].dag.df
    df_hotel = kwargs['dag_run'].dag.df_hotel

    champs_chambre = ["room_type", "hotel"]
    df_room = df[champs_chambre].copy()
    df_room.drop_duplicates(keep='first', inplace=True)
    df_room.reset_index(drop=True, inplace=True)

    #merge pour avoir id_hotel
    df_room=df_room.merge(df_hotel, on='hotel')
    df_room['id_room'] = df_room.apply(lambda _: uuid.uuid4(), axis=1)
    df_room.drop(columns=['hotel', 'level_hotel'], inplace=True)

    kwargs['dag_run'].dag.df_room = df_room


def create_table_reservation(**kwargs):
    df = kwargs['dag_run'].dag.df
    df_hotel = kwargs['dag_run'].dag.df_hotel
    df_client = kwargs['dag_run'].dag.df_client
    df_room = kwargs['dag_run'].dag.df_room

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

    kwargs['dag_run'].dag.df_res = df_res
    




def alimente_dw(**kwargs):
    conn = psycopg2.connect(
          user = "m139",
          password = "m139",
          host = "db-etu.univ-lyon2.fr",
          port = "5432",
          database = "m139"
    )
    
    date = kwargs['dag_run'].dag.df_date
    hotel = kwargs['dag_run'].dag.df_hotel
    room = kwargs['dag_run'].dag.df_room
    client = kwargs['dag_run'].dag.df_client
    reservation = kwargs['dag_run'].dag.df_res

   fct.insert_values(conn, date, 'date')
   fct.insert_values(conn, hotel, 'hotel')
   fct.insert_values(conn, room, 'room')
   fct.insert_values(conn, client, 'client')
   fct.insert_values(conn, reservation, 'reservation')


dag = MyDAG(
    'dw',
    default_args = default_args,
    # Executer tous les jours à minuit
    schedule_interval = '0 0 * * *' # on peut le modifier par timedelta(hours=1) si on veut faire des tests chaque heure
)



# Tâche Airflow    
create_table_date_task = PythonOperator(
    task_id = 'create_table_date',
    python_callable = create_table_date,
    dag = dag)

create_table_client_task = PythonOperator(
    task_id = 'create_table_client',
    python_callable = create_table_client,
    dag = dag)

create_table_hotel_task = PythonOperator(
    task_id = 'create_table_hotel',
    python_callable = create_table_hotel,
    dag = dag)

create_table_chambre_task = PythonOperator(
    task_id = 'create_table_chambre',
    python_callable = create_table_chambre,
    dag = dag)

create_table_reservation_task = PythonOperator(
    task_id = 'create_table_reservation',
    python_callable = create_table_reservation,
    dag = dag)

alimente_dw_task = PythonOperator(
    task_id = 'alimente_dw',
    python_callable = alimente_dw,
    dag = dag)

create_table_date_task >> create_table_client_task >> create_table_hotel_task >> create_table_chambre_task >> create_table_reservation_task >> alimente_dw

clean_dag.set_upstream(dw_dag)