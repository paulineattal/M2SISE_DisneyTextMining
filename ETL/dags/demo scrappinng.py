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
from functions import HotelsUrls
import psycopg2.extras as extras

path = '/Users/titouanhoude/Documents/GitHub/Disney-Text-Mining/fichiers/'

def scrapping():
    print("Scrapping Init")
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


scrapping()