# Dependencies
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import functions as fct
from time import strptime
import locale

path = 'C:/Users/pauli/Documents/M2/Text Mining/projet/Disney-Text-Mining/ETL/dags'

#La classe MyDag hérite de la classe DAG d'Airflow
class Clean :
    def __init__(self):
        self.conn = psycopg2.connect(user = "m140",password = "m140",host = "db-etu.univ-lyon2.fr",port = "5432",database = "m140")
        try:
            cur = self.conn.cursor()
            #Récupération des données de la table "historyclean" qui ont été scrapé à la meme date que l'execution du dag
            history = "SELECT * FROM history WHERE execution_date = %s"
            date = datetime.date.today()
            cur.execute(history, (date))
            self.df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        except : 
            print ("Erreur lors de la récupération de la table PostgreSQL")

    #Fonction qui recode le champs "grade_review" en float
    def recodage_type_float(self):
        #Récupérer le DF issus de la BDD
        df = self.df
        for i in ['grade_review']:
            df[i] = df[i].str.replace(",",".")
            df[i] = pd.to_numeric(df[i], downcast="float")
        #Push le DF pour la fonction de nettoyage suivante
        self.df=df

    #Fonction qui 
    def ajout_levels(self):
        #Pull le DF issus de la fonction de nettoyage précédente 
        df = self.df

        conditionlist_note = [
        (df['grade_review'] >= 8) ,
        (df['grade_review'] > 5) & (df['grade_review'] <8),
        (df['grade_review'] <= 5)]
        choicelist_note = [2,1,0]
        df['level_grade_review'] = np.select(conditionlist_note, choicelist_note, default='Not Specified')
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
        #Push le DF pour la fonction de nettoyage suivante
        self.df=df

    #Fonction qui recode les champs ["level_hotel", "level_grade_review"] en int
    def recodage_type_int(self):    
        #Pull le DF issus de la fonction de nettoyage précédente 
        df = self.df
        #application de la fonction astype()
        df['level_hotel'] = df['level_hotel'].astype(int)
        df['level_grade_review'] = df['level_grade_review'].astype(int)
        #Push le DF pour la fonction de nettoyage suivante
        self.df=df

    #fonction qui ajoute des information sur la date et sur le delais entre la reservation et la date du commentaire
    def clean_date_ajout(self):
        #Pull le DF issus de la fonction de nettoyage précédente 
        df = self.df
        #extrait du mois du commentaire
        df_moisreview=df['date_review'].map(str)
        for i in range(df.shape[0]):
            df_moisreview[i]=df_moisreview[i].split()[4]
        #extrait du moi de la reservation
        df_moisreservation=df['reservation_date'].map(str)
        for i in range(df.shape[0]):
            df_moisreservation[i]=df_moisreservation[i].split()[0].lower()
            df_anneereservation=df['reservation_date'].map(str)
        #extrait de l'année de reservation 
        for i in range(df.shape[0]):
            df_anneereservation[i]=df_anneereservation[i].split()[1]

        #ajout de toutes ces informations au DataFrame
        locale.setlocale(locale.LC_TIME,'')
        list_mois_num = [strptime(moisreservation,'%B').tm_mon for moisreservation in df_moisreservation]
        list_mois_com = [strptime(moisreview,'%B').tm_mon for moisreview in df_moisreview]
        delai = [com - num if com-num>-1 else 12+(com-num) for com, num in zip(list_mois_com, list_mois_num)]
        d = {'month_str': df_moisreservation, 'month_num': list_mois_num, 'year' : df_anneereservation,  'delay_comment': delai}
        df_date = pd.DataFrame(data=d)
        df = pd.concat([df,df_date], join = 'outer', axis = 1)
        #Push le DF pour la fonction de nettoyage suivante
        self.df=df

    #Fonction qui ajoute la date au bon format
    def add_date(self) :
        #Pull le DF issus de la fonction de nettoyage précédente 
        df = self.df
        #petite préparation 
        df = df.drop_duplicates(keep='first')
        df.drop(df[(df.delay_comment >3)].index , inplace=True)
        df=df.reset_index(drop=True)
        #transformer le champs "date_review" au bon type
        df_date=df['date_review'].map(str)
        for i in range(df.shape[0]):
            pos=df_date[i].find('le')
            #extraction
            df_date[i] = df_date[i][pos+2:] 
        df['date_review']=df_date
        #ajouter un champs date de commentaire
        df["date"] = pd.to_datetime(dict(year=df.year, month=df.month_num, day=1))
        #Push le DF pour la fonction de nettoyage suivante
        self.df=df

    #Fonction qui sauvegarde le DF clean la table "historyclean" de la BDD 
    def save_clean_file(self):
        #Pull de DF issus de la fonction de nettoyage précédente
        df = self.df
        try:
            #requete SQL de creation de la table "historyclean"
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
            #executer la requete de creation de la table "historyclean"
            fct.execute_req(self.conn, sql_create_historyclean)
            #Inserer le DF clean dans la table "historyclean"
            fct.insert_values(self.conn, df, 'historyclean')
        except : 
            print ("Erreur lors de la récupération de la table PostgreSQL")
            df.to_csv(str(path)+"df_clean.csv", sep=';', index=False, encoding="utf-8-sig")

    #Fonction qui execute toutes les fonctions 
    def main(self):
        self.recodage_type_float()
        self.ajout_levels()
        self.recodage_type_int()
        self.clean_date_ajout()
        self.add_date()
        self.save_clean_file()

# Exécution de la méthode principale
Clean().main()
