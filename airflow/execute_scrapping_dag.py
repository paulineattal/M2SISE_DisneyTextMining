# Dependencies
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import io
import numpy as np
import pandas as pd
import functions as fct
import psycopg2.extras as extras

# Propriétés du DAG
path = '/Users/titouanhoude/Documents/GitHub/Disney-Text-Mining/fichiers/'

def scrapping():

    try:
        conn = psycopg2.connect(
            user = "m140",
            password = "m140",
            host = "db-etu.univ-lyon2.fr",
            port = "5432",
            database = "m140"
        )

        cur = conn.cursor()

        try:
            history = "SELECT * FROM history"
            cur.execute(history)
            history = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

        except: 
                sql_create_history = '''CREATE TABLE IF NOT EXISTS history(
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
                hotel TEXT
                ); '''

                fct.execute_req(conn, sql_create_history)


        cur.close()
        conn.close()
    except (Exception, psycopg2.Error) as error :
        print ("Erreur lors de la connexion à PostgreSQL", error)


    ### Ajouter le code du scrapping
    HotelsUrls = {'Newport_Bay_Club' : 'https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews', 'Cheyenne' : 'https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews', 'Sequoia_Lodge' : 'https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews', 'New_York' : 'https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews', 'Davy_Crockett_Ranch' : 'https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews', 'Santa_Fe' : 'https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews'}
    chiffres = list("0123456789")

    for hotel in range(len(HotelsUrls)) : 
        df = fct.scrapping_hotel(hotel, history)

        try:
            new_df = pd.concat([new_df, df], ignore_index=True)
        except:
            new_df = df

        # Enregistrer le fichier
        try:
            new_df.to_csv(path+'scrapping_total.csv', index = False, sep=';', encoding='utf-8')
        except : 
            pass

    fct.insert_values(conn, new_df, 'history')

default_args = {
    'owner' : "Text-Mining_Project",
    
    # Lancer le DAG chaque jour
    'start_date' : datetime(2023, 1, 17),
    'depends_on_past' : False,

    # Si jamais l'éxecution fail, retenter 1 fois au bout de 5 minutes
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5)
}

with DAG('scrapping', default_args = default_args, schedule_interval = '0 0 * * *') as dag: 
    scrapping_task = PythonOperator(
        task_id = 'scrapping',
        python_callable = scrapping,
        dag = dag)
