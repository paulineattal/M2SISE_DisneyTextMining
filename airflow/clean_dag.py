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


def clean_date_ajout(**kwargs):
    dag = kwargs['dag_run']

    df_moisreview=dag.df['date_review'].map(str)
    for i in range(dag.df.shape[0]):
        df_moisreview[i]=df_moisreview[i].split()[4]
    df_moisreservation=dag.df['reservation_date'].map(str)
    for i in range(dag.df.shape[0]):
        df_moisreservation[i]=df_moisreservation[i].split()[0].lower()
        df_anneereservation=dag.df['reservation_date'].map(str)
    for i in range(dag.df.shape[0]):
        df_anneereservation[i]=df_anneereservation[i].split()[1]
        from time import strptime
    import locale
    locale.setlocale(locale.LC_TIME,'')

    list_mois_num = [strptime(moisreservation,'%B').tm_mon for moisreservation in df_moisreservation]
    list_mois_com = [strptime(moisreview,'%B').tm_mon for moisreview in df_moisreview]
    delai = [com - num if com-num>-1 else 12+(com-num) for com, num in zip(list_mois_com, list_mois_num)]

    d = {'month_str': df_moisreservation, 'month_num': list_mois_num, 'year' : df_anneereservation,  'delay_comment': delai}
    df_date = pd.DataFrame(data=d)
    dag.df = pd.concat([dag.df,df_date], join = 'outer', axis = 1)
    print(dag.df)
    print(dag.df.dtypes)
    #kwargs['dag_run'].dag.df = df

    

def ajout_levels(**kwargs):
    dag = kwargs['dag_run']
    print(dag.df.dtypes)
    conditionlist_note = [
    (dag.df['grade_review'] >= 8) ,
    (dag.df['grade_review'] > 5) & (dag.df['grade_review'] <8),
    (dag.df['grade_review'] <= 5)]
    choicelist_note = [2,1,0]
    dag.df['level_grade_review'] = np.select(conditionlist_note, choicelist_note, default='Not Specified')
    print('test')
    conditionlist_hotel = [
    (dag.df['hotel'] == "Newport_Bay_Club"),
    (dag.df['hotel'] == "New_York"),
    (dag.df['hotel'] == "Sequoia_Lodge"),
    (dag.df['hotel'] == "Cheyenne"),
    (dag.df['hotel'] == "Santa_Fe"),
    (dag.df['hotel'] == "Davy_Crockett_Ranch")
    ]
    choicelist_hotel = [6,5,4,3,2,1]
    dag.df['level_hotel'] = np.select(conditionlist_hotel, choicelist_hotel, default='Not Specified')
    print('good')
    #kwargs['dag_run'].dag.df = df


def recodage_type_float(**kwargs):
    dag = kwargs['dag_run']
    for i in ['grade_review']:
        dag.df[i] = dag.df[i].str.replace(",",".")
        dag.df[i] = pd.to_numeric(df[i], downcast="float")
    #kwargs['dag_run'].conf['df'] = df


def recodage_type_int(**kwargs):
    dag = kwargs['dag_run']
    for i in ['level_hotel', 'level_grade_review']:
        dag.df[i] = dag.df[i].astype(int)    
    #kwargs['dag_run'].dag.df = df



def add_date(**kwargs) :
    df = kwargs['dag_run'].dag.df
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
    df_clean = df.copy()

    kwargs['dag_run'].dag.df_clean = df_clean

def save_clean_file(**kwargs):
    df_clean = kwargs['dag_run'].dag.df_clean

    try:
        conn = psycopg2.connect(
            user = "m140",
            password = "m140",
            host = "db-etu.univ-lyon2.fr",
            port = "5432",
            database = "m140"
        )

        sql_create_historyclean = '''CREATE TABLE IF NOT EXISTS historyclean(
                Names TEXT
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
                date DATE,
                ); '''

        fct.execute_req(conn, sql_create_historyclean)
        fct.insert_values(conn, df_clean, 'historyclean')

    except : 
        print ("Erreur lors de la récupération de la table PostgreSQL")
        df_clean.to_csv(str(path)+"df_clean.csv", sep=';', index=False, encoding="utf-8-sig")



with MyDag( 'clean_dag',default_args = default_args, schedule_interval = '0 0 * * *') as dag_clean:
    
    clean_date_ajout_task = PythonOperator(
        task_id = 'clean_date_ajout',
        python_callable = clean_date_ajout,
        dag = dag_clean)

    ajout_levels_task = PythonOperator(
        task_id = 'ajout_levels',
        python_callable = ajout_levels,
        dag = dag_clean)

    recodage_type_float_task = PythonOperator(
        task_id = 'recodage_type_float',
        python_callable = recodage_type_float,
        dag = dag_clean)

    recodage_type_int_task = PythonOperator(
        task_id = 'recodage_type_int',
        python_callable = recodage_type_int,
        dag = dag_clean)

    add_date_task = PythonOperator(
        task_id = 'add_date',
        python_callable = add_date,
        dag = dag_clean)

    save_clean_file_task = PythonOperator(
        task_id = 'save_clean_file',
        python_callable = save_clean_file,
        dag = dag_clean)

    t_last = TriggerDagRunOperator(
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
save_clean_file_task.set_downstream(t_last)
