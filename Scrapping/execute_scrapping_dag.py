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
import scrapping_final as sf

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
    HotelsUrls = {'Newport_Bay_Club' : 'https://www.booking.com/hotel/fr/disney-39-s-newport-bay-club-r.fr.html#tab-reviews', 'Cheyenne' : 'https://www.booking.com/hotel/fr/disney-39-s-cheyenne-r.fr.html#tab-reviews', 'Sequoia_Lodge' : 'https://www.booking.com/hotel/fr/disneys-sequoia-lodge-r.fr.html#tab-reviews', 'New_York' : 'https://www.booking.com/hotel/fr/disney-39-s-new-york-r.fr.html#tab-reviews', 'Davy_Crockett_Ranch' : 'https://www.booking.com/hotel/fr/disneys-davy-crockett-ranch.fr.html#tab-reviews', 'Santa_Fe' : 'https://www.booking.com/hotel/fr/disney-39-s-santa-fe-r.fr.html#tab-reviews'}
    chiffres = list("0123456789")

    for hotel in range(len(HotelsUrls)) : 
        sf.scrapping_hotel(hotel)
    ### Ajouter le code pour insérer le scrapping dans la database


scrapping_task = PythonOperator(
    task_id = 'scrapping',
    python_callable = scrapping,
    dag = dag)