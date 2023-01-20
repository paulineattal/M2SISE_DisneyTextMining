#importations des librairies
from dash import Dash, html,dcc , Output, Input, callback, dash_table, State
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from datetime import datetime as dt
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from wordcloud import WordCloud
from gensim import corpora
from io import BytesIO
import gensim 

import dash_bootstrap_components as dbc
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import numpy as np
import gunicorn
import psycopg2
import sklearn
import string
import base64
import mpld3
import nltk

def store_data():
    #importation de la BDD sur Postgrey à partir d'une connexion
    try:
         #créer la connexion à la Base De Données
        conn = psycopg2.connect(
            user = "m139",
            password = "m139",
            host = "db-etu.univ-lyon2.fr",
            port = "5432",
            database = "m139"
        )
    
        #conn.cursor() pour créer un objet curseur Psycopg2. 
        #cette méthode crée un nouvel objet psycopg2.extensions.cursor.
        cur = conn.cursor()
        #sélection des champs à partir des diverses tables : reservation, client, hotel, room, date
        reservation = "SELECT * FROM reservation"
        client = "SELECT * FROM client"
        hotel = "SELECT * FROM hotel"
        room = "SELECT * FROM room"
        date = "SELECT * FROM date"

        #exécuter requête de sélection avec cur.execute()
        cur.execute(reservation)
        #fetchall() pour tout extraire
        reservation = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.execute(client)
        client = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.execute(hotel)
        hotel = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.execute(room)
        room = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        cur.execute(date)
        date = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

        #fermer curseur
        cur.close()
        #fermer page de connexion
        conn.close()
    except (Exception, psycopg2.Error) as error :
        print ("Erreur lors de la connexion à PostgreSQL", error)

    #jointure des tables pour réaliser le dataframe
    hotel_room = hotel.merge(room, on="id_hotel")
    res_client = reservation.merge(client, on="id_client")
    res_client_date = res_client.merge(date, on="id_date")
    df = res_client_date.merge(hotel_room, on="id_room")
    return df.to_dict('records')


#fonction qui renvoi une sunburst en fonction de l'année puis du mois
#et renvoi les indicateurs suivants par mois : nombre de nuitées, moyenne des notes
#avec une échelle de valeurs colorée en fonction de la note moyenne obtenue

def sungraph(df):
    fig = px.sunburst(df, path=['year', 'month_str'], values='nuitee',
                  color='grade_review',
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df['grade_review'], weights=df['nuitee']))
    return(fig)

mots_vides = stopwords.words("french")

#fonction qui nettoie un document
def nettoyage_doc(doc_param, mots_vides):
    #récupérer la liste des ponctuations
    ponctuations = list(string.punctuation)
    #liste des chiffres
    chiffres = list("0123456789")
    #liste de mots spécifiques à retirer
    special=["parc","disneyland","disney","paris","hôtel","lhôtel","😡😡😡😡😡😡","😡😡😡😡😡je","🤣🤣👍👍👍","très","trop","plus","avon","marvel","fait","déjà","donc","après","cest","alors","vraiment","quand","avant","toute","cela","contre","faire","dont","aller","comme","avoir"]
    #outil pour procéder à la lemmatisation - attention de charger le nltk.download('wordnet') le cas échéant
    lem = WordNetLemmatizer()
    #liste des mots vides

    #passage en minuscule
    doc = doc_param.lower()
    #retrait des ponctuations
    doc = "".join([w for w in list(doc) if not w in ponctuations])
    #retirer les chiffres
    doc = "".join([w for w in list(doc) if not w in chiffres])
    #transformer le document en liste de termes par tokénisation
    doc = word_tokenize(doc)
    #lematisation de chaque terme
    doc = [lem.lemmatize(terme) for terme in doc]
    #retirer les stopwords
    doc = [w for w in doc if not w in mots_vides]
    #retirer les mots spécifiques à ces commentaires
    doc = [w for w in doc if not w in special]
    #retirer les termes de moins de 3 caractères
    doc = [w for w in doc if len(w)>3]
    #fin
    return doc

def word_cloud(df,champ):
    #réinitialiser l'index des données
    df_cloud=df[champ].reset_index(drop=True)
    l=[]
    #recherche des indices où il n'y a pas de commentaires (en lien avec champ)
    for i in range(len(df_cloud)-1):
        if isinstance(df_cloud[i], float)==True:
            l.append(i)
    #supprime les lignes sans commentaires
    df_cloud=df_cloud.drop(df_cloud.index[l])
    df_cloud=df_cloud.reset_index()
    #nettoyage du corpus
    corpus_liste=[]
    for i in range(df_cloud.shape[0]-1):
        corpus_liste.append(nettoyage_doc(df_cloud.iloc[i,1], mots_vides))
    #texte final comprenant une seule ligne avec tous les mots issus des commentaires "nettoyés"
    str_text=[]
    for i in range(len(corpus_liste)):
        str_text.append(' '.join(corpus_liste[i]))
    final_text=' '.join(str_text)
    #création du nuage de ces mots
    nuage=WordCloud(background_color="white").generate(final_text) 
    plt.figure(figsize=(5, 5))
    #affichage des données sous forme d'images
    plt.imshow(nuage,interpolation='bilinear')
    #sans axes
    plt.axis("off")
    #marges
    plt.margins(0,0)
    #retour du nuage de mots correspondant à la sélection du champ
    if champ=='positive_review':
        #sauvegarde du word cloud sous forme de figure
        plt.savefig("./assets/wordpos.png", bbox_inches = 'tight', pad_inches = 0)
        #création d'un chemin pour accéder à la figure
        image_path=r'assets/wordpos.png'
    else :
        plt.savefig("./assets/wordneg.png", bbox_inches = 'tight', pad_inches = 0)
        image_path=r'assets/wordneg.png'
    return(image_path)

def count_avis(df,champ):
    df_new=df[champ].reset_index(drop=True)
    l=[]
    #recherche des indices où il y n'y a pas de "valeurs"
    #et stockage dans une liste
    for i in range(len(df_new)-1):
        if (df_new[i]=='NaN')==True:
        #if isinstance(df_new[i], float)==True:
            l.append(i)
    #longueur de la liste
    return(len(l))

#fonction qui crée un 
def creation_corpus_liste(df,champ):
    df_corpus=df[champ].reset_index(drop=True)
    l=[]
    for i in range(len(df_corpus)-1):
        if isinstance(df_corpus[i], float)==True:
            l.append(i)
    #création d'un dataframe ne comportant pas de ligne vide 
    #pour la colonne commentaire selon le champ (positif ou négatif)
    df_corpus=df_corpus.drop(df_corpus.index[l])
    df_corpus=df_corpus.reset_index()
    #nettoyage de chaque ligne de commentaires non vide
    corpus_liste=[]
    for i in range(df_corpus.shape[0]-1):
        corpus_liste.append(nettoyage_doc(df_corpus.iloc[i,1], mots_vides))
    #création de corpus nettoyer
    return(corpus_liste)

    #fonction qui récupère le pourcentage pour chaque mot (quatre en tout) pour un cluster
def completer(i,k,clust,final_clusters):
    if k==0 :
        j=0
    if k==2 :
        j=1
    if k==4 :
        j=2
    if k==6 :
        j=3
    numero=clust[i].split()[k]
    final_clusters.loc[j,'numéro cluster']=i
    final_clusters.loc[j,'pourcentages']=numero[0:5]
    final_clusters.loc[j,'mots']=numero[7:len(numero)-1]

def clusters(corpus,i,couleur):
    # Création d'un dictionnaire avec le nombre de fois où chaque mots apparaît
    dictionary = corpora.Dictionary(corpus)
    #Filtrer les mots (non)fréquents
    dictionary.filter_extremes(no_below=10, keep_n=600)
    # Création du corpus
    corpusdict = [dictionary.doc2bow(text) for text in corpus]
    # Définition du modèle LDA
    ldamodel = gensim.models.ldamodel.LdaModel(corpusdict, num_topics = 3,id2word=dictionary, passes=15)
    #data frame des trois sujets (clusters) issus du modèle avec les 4 mots les plus fréquents
    topics = ldamodel.print_topics(num_words=4)
    l=[]
    for topic in topics:
        l.append(topic)
    #création du dataframe comportant les mots et les fréquences de chacun dans ce cluster
    clusters=pd.DataFrame(l,columns = ['Clusters','Fréquence apparition de chaque terme'])
    #split de la colonne comportant les informations mots et fréquences
    clust=clusters['Fréquence apparition de chaque terme'].map(str)
    #création du dataframe avec une colonne pour le numéro de cluster, 
    #une colonne pour les mots et une pour les fréquences d'apparition
    final_clusters = pd.DataFrame(columns=['numéro cluster','mots','pourcentages'], index = range(4))
    #remplit le dataframe pour chaque mot du cluster
    completer(i,0,clust,final_clusters)
    completer(i,2,clust,final_clusters)
    completer(i,4,clust,final_clusters)
    completer(i,6,clust,final_clusters)
    #recodage du numéro de cluster en type 'entier'
    final_clusters['numéro cluster'] = final_clusters['numéro cluster'].astype('int')
    #er le pourcentage en float
    final_clusters['pourcentages'] = pd.to_numeric(final_clusters['pourcentages'], downcast="float")
    if couleur=='positive_review' :
        #bar plot des mots et de leur fréquence dans le cluster
        fig = px.bar(final_clusters, x="mots", y="pourcentages")  
    else :
        fig = px.bar(final_clusters, x="mots", y="pourcentages",color_discrete_sequence=['red'])  
    return fig