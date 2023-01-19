# Dependencies
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import functions as fct
import json
from time import strptime
import locale
#from dag_dw import dag_dw

path = '/Users/titouanhoude/Documents/GitHub/Disney-Text-Mining/fichiers/'

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
            history = "SELECT * FROM history"
            cur.execute(history)
            self.df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        except : 
            print ("Erreur lors de la récupération de la table PostgreSQL")
        super(MyDag, self).__init__(*args, **kwargs)


def recodage_type_float(**kwargs):
    df = kwargs['dag_run'].dag.df
    for i in ['grade_review']:
        df[i] = df[i].str.replace(",",".")
        df[i] = pd.to_numeric(df[i], downcast="float")
    # print(df.dtypes)

    df = df.to_json(orient="records", force_ascii=False)
    
    kwargs['ti'].xcom_push(key='df_float', value=df)

def ajout_levels(**kwargs):

    df = kwargs['ti'].xcom_pull(key='df_float', task_ids='recodage_type_float')
    df = pd.read_json(df)
    print(df.dtypes)

    conditionlist_note = [
    (df['grade_review'] >= 8) ,
    (df['grade_review'] > 5) & (df['grade_review'] <8),
    (df['grade_review'] <= 5)]
    choicelist_note = [2,1,0]
    df['level_grade_review'] = np.select(conditionlist_note, choicelist_note, default='Not Specified')
    print('test')
    conditionlist_hotel = [
    (df['hotel'] == "Newport_Bay_Club"),
    (df['hotel'] == "New_York"),
    (df['hotel'] == "Sequoia_Lodge"),
    (df['hotel'] == "Cheyenne"),
    (df['hotel'] == "Santa_Fe"),
    (df['hotel'] == "Davy_Crockett_Ranch")
    ]
    choicelist_hotel = [6,5,4,3,2,1]
    df['level_hotel'] = np.select(conditionlist_hotel, choicelist_hotel, default='Not Specified')
    print('good')
    
    df = df.to_json(orient="records", force_ascii=False)
    
    kwargs['ti'].xcom_push(key='df_level', value=df)

def recodage_type_int(**kwargs):    
    df = kwargs['ti'].xcom_pull(key='df_level',task_ids='ajout_levels')
    df = pd.read_json(df)

    df['level_hotel'] = df['level_hotel'].astype(int)
    df['level_grade_review'] = df['level_grade_review'].astype(int)
  
    df = df.to_json(orient="records", force_ascii=False)

    kwargs['ti'].xcom_push(key='df_int', value=df) 


def clean_date_ajout(**kwargs):
    df = kwargs['ti'].xcom_pull(key='df_int', task_ids='recodage_type_int')
    df = pd.read_json(df)
    df_moisreview=df['date_review'].map(str)
    for i in range(df.shape[0]):
        df_moisreview[i]=df_moisreview[i].split()[4]
    df_moisreservation=df['reservation_date'].map(str)
    for i in range(df.shape[0]):
        df_moisreservation[i]=df_moisreservation[i].split()[0].lower()
        df_anneereservation=df['reservation_date'].map(str)
    for i in range(df.shape[0]):
        df_anneereservation[i]=df_anneereservation[i].split()[1]

    locale.setlocale(locale.LC_TIME,'')

    list_mois_num = [strptime(moisreservation,'%B').tm_mon for moisreservation in df_moisreservation]
    list_mois_com = [strptime(moisreview,'%B').tm_mon for moisreview in df_moisreview]
    delai = [com - num if com-num>-1 else 12+(com-num) for com, num in zip(list_mois_com, list_mois_num)]

    d = {'month_str': df_moisreservation, 'month_num': list_mois_num, 'year' : df_anneereservation,  'delay_comment': delai}
    df_date = pd.DataFrame(data=d)
    df = pd.concat([df,df_date], join = 'outer', axis = 1)
    print(df)
    print(df.dtypes)

    df = df.to_json(orient="records", force_ascii=False)

    kwargs['ti'].xcom_push(key='df_clean_date', value=df) 


def add_date(**kwargs) :
    df = kwargs['ti'].xcom_pull(key='df_clean_date', task_ids='clean_date_ajout')
    df = pd.read_json(df)

    df = df.drop_duplicates(keep='first')
    df.drop(df[(df.delay_comment >3)].index , inplace=True)
    df=df.reset_index(drop=True)
    df_date=df['date_review'].map(str)
    for i in range(df.shape[0]):
        pos=df_date[i].find('le')
        #extraction
        df_date[i] = df_date[i][pos+2:] 
    df['date_review']=df_date
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month_num, day=1))
    
    df = df.to_json(orient="records", force_ascii=False)

    kwargs['ti'].xcom_push(key='df_add_date', value=df) 

def save_clean_file(**kwargs):
    df = kwargs['ti'].xcom_pull(key='df_add_date', task_ids='add_date')
    df = pd.read_json(df)
    try:
        conn = psycopg2.connect(
            user = "m140",
            password = "m140",
            host = "db-etu.univ-lyon2.fr",
            port = "5432",
            database = "m140"
        )

        sql_create_historyclean = '''CREATE TABLE IF NOT EXISTS historyclean(
                Names TEXT,
                Country TEXT,
                room_type TEXT,
                nuitee INT,
                reservation_date TEXT,
                traveler_infos TEXT,
                date_review TEXT,
                review_title TEXT,
                grade_review TEXT,
                positive_review TEXT,
                negative_review TEXT,
                usefulness_review INT,
                UniqueID TEXT,
                hotel TEXT,
                level_grade_review INT,
                level_hotel INT,
                month_str TEXT, 
                month_num INT,
                year INT,
                delay_comment INT,
                date DATE)
                ; '''

        fct.execute_req(conn, sql_create_historyclean)
        fct.insert_values(conn, df, 'historyclean')

    except : 
        print ("Erreur lors de la récupération de la table PostgreSQL")
        df.to_csv(str(path)+"df_clean.csv", sep=';', index=False, encoding="utf-8-sig")



with MyDag( 'clean_dag',default_args = default_args, schedule_interval = '0 0 * * *') as dag_clean:
    
    recodage_type_float_task = PythonOperator(
        task_id = 'recodage_type_float',
        python_callable = recodage_type_float,
        provide_context=True,
        dag = dag_clean)

    ajout_levels_task = PythonOperator(
        task_id = 'ajout_levels',
        python_callable = ajout_levels,
        provide_context=True,
        dag = dag_clean)

    recodage_type_int_task = PythonOperator(
        task_id = 'recodage_type_int',
        python_callable = recodage_type_int,
        dag = dag_clean)

    clean_date_ajout_task = PythonOperator(
        task_id = 'clean_date_ajout',
        python_callable = clean_date_ajout,
        dag = dag_clean)

    add_date_task = PythonOperator(
        task_id = 'add_date',
        python_callable = add_date,
        dag = dag_clean)

    save_clean_file_task = PythonOperator(
        task_id = 'save_clean_file',
        python_callable = save_clean_file,
        dag = dag_clean)

    last_task = TriggerDagRunOperator(
        dag=dag_clean,
        task_id='last',
        trigger_dag_id = 'dag_dw'
    )
# Tâche Airflow    

recodage_type_float_task.set_downstream(ajout_levels_task)
ajout_levels_task.set_downstream(recodage_type_int_task)
recodage_type_int_task.set_downstream(clean_date_ajout_task)
clean_date_ajout_task.set_downstream(add_date_task)
add_date_task.set_downstream(save_clean_file_task)
save_clean_file_task.set_downstream(last_task)
