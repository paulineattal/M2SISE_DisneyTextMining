import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from .side_bar import sidebar
from datetime import datetime as dt
import numpy as np
import sklearn
import nltk
import string
from nltk.stem import WordNetLemmatizer
#pour la tokénisation
from nltk.tokenize import word_tokenize
#stopwords
from nltk.corpus import stopwords
#from io import BytesIO
#import matplotlib.pyplot as plt
#import mpld3
import gensim
from gensim.models import Word2Vec
from gensim import corpora
#CAH à partir de scipy
from scipy.cluster.hierarchy import dendrogram, linkage,fcluster
#import pyLDAvis.gensim_models
#pour transformation en MDT
from sklearn.feature_extraction.text import CountVectorizer

dash.register_page(__name__)

#chargement du fichier
df = pd.read_csv('assets/df_clean_newport.csv',sep=';')

#------------------------------traitement du data frame-----------------------------------------
#-----------------------------------------------------------------------------------------------

min=df.date.min()
max=df.date.max()
df['date']=pd.to_datetime(df['date'])
df.set_index('date',inplace=True)

#-------------------dictionnaires-----------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Création d'un dictionnaire pour le filtre hôtel (dropdown)
hotel_dict=[{'label':html.Div(['Newport Bay Club'],style={'font-size':22}),'value':6},{'label':html.Div(['Art of Marvel'],style={'font-size':22}),'value':5},{'label':html.Div(['Sequoia Lodge'],style={'font-size':22}),'value':4},{'label':html.Div(['Cheyenne'],style={'font-size':22}),'value':3},{'label':html.Div(['Santa Fé'],style={'font-size':22}),'value':2},{'label':html.Div(['Davy Crockett Ranch'],style={'font-size':22}),'value':1}]

#Création d'un dictionnaire pour le filtre notes (dropdown)
notes_dict=[{'label':html.Div(['Toutes notes'],style={'font-size':22}),'value':3},{'label':html.Div(['note >=8'],style={'font-size':22}),'value':2},{'label':html.Div(['5 < note < 8'],style={'font-size':22}),'value':1},{'label':html.Div(['notes <= 5'],style={'font-size':22}),'value':0}]

#--------------fonctions-----------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------

def nettoyage_doc(doc_param):
    #récupérer la liste des ponctuations
    ponctuations = list(string.punctuation)
    #liste des chiffres
    chiffres = list("0123456789")
    #liste de mots spécifiques à retirer
    special=["parc","disneyland","disney","paris","hôtel","lhôtel","😡😡😡😡😡😡","😡😡😡😡😡je"]
    #outil pour procéder à la lemmatisation - attention à charger le cas échéant
    lem = WordNetLemmatizer()
    #liste des mots vides
    mots_vides = stopwords.words("french")

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


def creation_corpus_liste(df,champ):
    df_cloud=df[champ]
    df_cloud=df_cloud.drop(df_cloud.index[df_cloud.isnull()])
    df_cloud=df_cloud.reset_index()
    corpus_liste=[]
    for i in range(df_cloud.shape[0]-1):
        corpus_liste.append(nettoyage_doc(df_cloud.iloc[i,1]))
    return(corpus_liste)

def clusters(corpus):
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
    clust=pd.DataFrame(l,columns = ['Clusters','Fréquence apparition de chaque terme'])
    return clust

#----------------définition des cartes-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

#Définition de la carte date
card_date=dbc.Card([

                        dbc.CardBody([
                            html.H4("Sélectionner une période entre décembre 2019 et mars 2022",className="Card-text"),
                            dcc.DatePickerRange(
                            id='date-picker-range',
                            min_date_allowed=dt(2019,12,22),
                            max_date_allowed=dt(2022,12,20),
                            start_date=dt(2019,12,22).date(),
                            end_date=dt(2022,12,20).date(),
                            calendar_orientation='horizontal',
                            minimum_nights=15,
                            updatemode='singledate'
                            )  
                            ])
                    ],
                        color="white", #choix de la couleur
                        inverse=False,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
card_filter_hotel=dbc.Card([
                        dbc.CardBody([
                                html.H4("Sélectionner l'hôtel",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='hotel-dropdown',options=hotel_dict,value=6,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

card_filter_notes=dbc.Card([
                        dbc.CardBody([
                                html.H4("Sélectionner le groupe selon les notes",className="Card-text"),
                                #création de la barre de défilement pour sélectionner le groupe
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='notes-dropdown',options=notes_dict,value=3,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

##Définition d'une carte pour les titres non automatiques
card_delai=dbc.Card([
                        dbc.CardBody([
                                html.H4("Délai commentaires",className="Card-text"),
                                html.H4("Pourcentage",className="Card-text"),
                                html.H2(id='pourcentage_delai'),
                                html.P('',style={'height':'1vh'}),
                                html.H4("Moyenne",className="Card-text"),
                                html.H2(id='moyenne_delai')
                            ])
                        ],
                        color="success",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'},
                        #style={'textAlign':'center','height':'100%'},
                        ) 

#Définition d'une carte pour les pays
card_sejour=dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id = 'type_sejour',height=220,width=400)
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'}
                        ) 


#Définition d'une carte pour les clusters sur avis positifs
card_positif=dbc.Card([
                    dbc.CardBody([
                        html.H4("Clusters avis positifs",className="Card-text"),
                        html.Iframe(id = 'clusters_positifs',srcDoc=None,height=520,width=650)
                        ])
                    ],
                    color="info",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    ) 

#Définition d'une carte pour les clusters sur avis négatifs
card_negatif=dbc.Card([
                    dbc.CardBody([
                        html.H4("Clusters avis négatifs",className="Card-text"),
                        html.Iframe(id = 'clusters_negatifs',srcDoc=None,height=520,width=650)
                        ])
                    ],
                    color="danger",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    ) 

#Gestion de l'application avec les différentes cartes
def layout():
    return dbc.Container([
    #on indique le nombre de lignes et de colonnes 
    #permet d'avoir la structure de la page qui sera affichée
    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar()
                ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

            dbc.Col(
                [
                    html.H3('Troisième résumé', style={'textAlign':'center'}),

                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
        ]
    ),
    dbc.Row(
            [
                dbc.Col(card_date,width=5),
                dbc.Col(card_filter_hotel,width=3),
                dbc.Col(card_filter_notes,width=4),
            ],
            justify="end",
        ),
        dbc.Row(
            [   
                dbc.Col(card_delai,width=3),
                dbc.Col(card_sejour,width=5),
            ],
        ),
        dbc.Row([],style={'height':'3vh'},),
        dbc.Row(
            [
                dbc.Col(card_positif, width=6),
                dbc.Col(card_negatif,width=6)
            ],
        ),
    ],
    fluid=True, #pour que l'ensembles des cartes ne soient pas "figées"
)

#-------------------------callbacks------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------

@callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='pourcentage_delai',component_property='children'),
    Output(component_id='moyenne_delai',component_property='children'),
    Output(component_id='type_sejour',component_property='srcDoc'),
    Output(component_id='clusters_positifs',component_property='srcDoc'),
    Output(component_id='clusters_negatifs',component_property='srcDoc'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown',component_property='value'),
    Input(component_id='notes-dropdown',component_property='value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date')
)

def update_output(decision_hotel,choix_groupe,start_date,end_date):
    dff=df.loc[start_date:end_date]
    if choix_groupe==3: 
        df_select=dff[dff.level_hotel==decision_hotel]
    else:
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
    
    percentdelai=round(len(df_select[df_select.delay_comment>=2])*100/df_select.shape[0],3)
    moyennedelai=round(df_select[df_select.delay_comment>=2]['grade_review'].mean(),3)
    d1=df_select.groupby(['traveler_infos'])[['index','Country']].count()*100/df_select.shape[0]
    d2=df_select.groupby(['traveler_infos'])[['grade_review','nuitee']].mean()
    df_sejour=pd.merge(d1,d2,on='traveler_infos')
    var=['index','grade_review']
    sejour=df_sejour[var]
    sejour=sejour.rename(columns={"index": "pourcentages","grade_review":"moyenne"})
    corpusplus=creation_corpus_liste(df_select,'positive_review')
    corpusneg=creation_corpus_liste(df_select,'negative_review')
    cap=clusters(corpusplus)
    can=clusters(corpusneg)
    sejour=round(sejour,3).head(4)
    cap=cap.rename(columns={"index": "clusters"})
    can=can.rename(columns={"index": "clusters"})
    cap = cap.style.set_properties(**{'color': 'white','font-size': '20pt',})
    can = can.style.set_properties(**{'color': 'white','font-size': '20pt',})
    sejour = sejour.style.set_properties(**{'color': 'white','font-size': '20pt',})
    return percentdelai,moyennedelai,sejour.to_html(index=False,header=True),cap.to_html(index=False,header=True),can.to_html(index=False,header=True)