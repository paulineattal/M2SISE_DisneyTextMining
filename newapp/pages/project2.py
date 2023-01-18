import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime as dt
import numpy as np
import sklearn
import nltk
import string
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
#pour la tokénisation
from nltk.tokenize import word_tokenize
#stopwords
from nltk.corpus import stopwords
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import mpld3
import psycopg2

dash.register_page(__name__,order=2)

try:
    conn = psycopg2.connect(
          user = "m139",
          password = "m139",
          host = "db-etu.univ-lyon2.fr",
          port = "5432",
          database = "m139"
    )
    cur = conn.cursor()
    reservation = "SELECT * FROM reservation"
    client = "SELECT id_client, country, review_title, positive_review, negative_review FROM client"
    hotel = "SELECT * FROM hotel"
    room = "SELECT * FROM room"
    date = "SELECT id_date, date FROM date"

    cur.execute(reservation)
    reservation = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.execute(client)
    client = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.execute(hotel)
    hotel = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.execute(room)
    room = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.execute(date)
    date = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    cur.close()
    conn.close()
except (Exception, psycopg2.Error) as error :
    print ("Erreur lors de la connexion à PostgreSQL", error)

hotel_room = hotel.merge(room, on="id_hotel")
res_client = reservation.merge(client, on="id_client")
res_client_date = res_client.merge(date, on="id_date")
df = res_client_date.merge(hotel_room, on="id_room")

#------------------------------traitement du data frame-----------------------------------------
#-----------------------------------------------------------------------------------------------

df['date']=pd.to_datetime(df['date'])
min=df.date.min()
max=df.date.max()
df.set_index('date',inplace=True)

#-------------------dictionnaires-----------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Création d'un dictionnaire pour le filtre hôtel (dropdown)
hotel_dict=[{'label':html.Div(['Newport Bay Club'],style={'font-size':22}),'value':6},{'label':html.Div(['Art of Marvel'],style={'font-size':22}),'value':5},{'label':html.Div(['Sequoia Lodge'],style={'font-size':22}),'value':4},{'label':html.Div(['Cheyenne'],style={'font-size':22}),'value':3},{'label':html.Div(['Santa Fé'],style={'font-size':22}),'value':2},{'label':html.Div(['Davy Crockett Ranch'],style={'font-size':22}),'value':1}]
#hotel_dict=[{'label':html.Div(['Newport Bay Club'],style={'font-size':22}),'value':'Newport_Bay_Club'},{'label':html.Div(['Art of Marvel'],style={'font-size':22}),'value':'New_York'},{'label':html.Div(['Sequoia Lodge'],style={'font-size':22}),'value':'Sequoia_Lodge'},{'label':html.Div(['Cheyenne'],style={'font-size':22}),'value':'Cheyenne'},{'label':html.Div(['Santa Fé'],style={'font-size':22}),'value':'Santa_Fe'},{'label':html.Div(['Davy Crockett Ranch'],style={'font-size':22}),'value':'Davy_Crockett_Ranch'}]

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
    special=["parc","disneyland","disney","paris","hôtel","lhôtel","😡😡😡😡😡😡","😡😡😡😡😡je","🤣🤣👍👍👍","très","trop","plus","avon","marvel","fait","déjà","donc","après","cest","alors","vraiment","quand","avant","toute","cela","contre","faire","dont","aller","comme","avoir"]
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
        corpus_liste.append(nettoyage_doc(df_cloud.iloc[i,1]))
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
        plt.savefig("./assets/wordpos.png", bbox_inches = 'tight', pad_inches = 0)
        image_path=r'assets/wordpos.png'
    else :
        plt.savefig("./assets/wordneg.png", bbox_inches = 'tight', pad_inches = 0)
        image_path=r'assets/wordneg.png'
    return(image_path)

def count_avis(df,champ):
    df_new=df[champ].reset_index(drop=True)
    l=[]
    for i in range(len(df_new)-1):
        if (df_new[i]=='NaN')==True:
        #if isinstance(df_new[i], float)==True:
            l.append(i)
    return(len(l))

#----------------définition des cartes-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

#Définition de la carte date
card_date=dbc.Card([

                        dbc.CardBody([
                            html.H4("Sélectionner une période",className="Card-text"),
                            dcc.DatePickerRange(
                            id='date-picker-range',
                            min_date_allowed=min,
                            max_date_allowed=max,
                            start_date=min.date(),
                            end_date=max.date(),
                            calendar_orientation='horizontal',
                            minimum_nights=15,
                            updatemode='singledate'
                            )  
                            ])
                    ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
card_filter_hotel=dbc.Card([
                        dbc.CardBody([
                                html.H4("un hôtel",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='hotel-dropdown',options=hotel_dict,value=6,style = {"color":"black"}),  
                                #dcc.Dropdown(id='hotel-dropdown',options=hotel_dict,value='Newport_Bay_Club',style = {"color":"black"}),  
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
                                html.H4("un groupe de clients (notes)",className="Card-text"),
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
card_top_titres=dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id ='top_titres',height=230)
                            ])
                        ],
                        color="danger",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'},
                        ) 

#Définition d'une carte pour les pays
card_top_pays=dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id = 'top_pays',height=230)
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'}
                        ) 

#Définition d'une carte pour le pourcentage de commentaires positifs et négatifs
card_pourcentage_commentaires=dbc.Card([
                        dbc.CardBody([
                                #affichage du pourcentage d'avis positifs
                                html.H4("Pourcentage d'avis positifs",className="Card-text"),
                                #html.P('',style={'height':'0.5vh'}),
                                html.H2(id='pourcentage_avis_positifs'),
                                html.P('',style={'height':'1vh'}),
                                #affichage du pourcentage d'avis négatifs
                                html.H4("Pourcentage d'avis négatifs",className="Card-text"),
                                #html.P('',style={'height':'0.5vh'}),
                                html.H2(id='pourcentage_avis_negatifs'),
                            ])
                        ],
                        color="info",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center','height':'100%'},
                        ) 

#Définition d'une carte pour les commentaires positifs
card_positifs=dbc.Card([
                    dbc.CardBody([
                        html.H4("Avis positifs",className="Card-text"),
                        #affichage word cloud
                        html.Img(id='fig_avis_positifs')
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    #style={'height':'120vh'},
                    ) 

#Définition d'une carte pour les commentaires négatifs
card_negatifs=dbc.Card([
                    dbc.CardBody([
                        html.H4("Avis négatifs",className="Card-text"),
                        html.Img(id='fig_avis_negatifs')
                        ])
                    ],
                    color="light",
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
        dcc.Markdown('# Deuxième résumé', style={'textAlign': 'center'}),
        ]
    ),
    dbc.Row(
            [
                dbc.CardGroup([card_date,card_filter_hotel,card_filter_notes])  
            ],
            justify="end",
        ),
        dbc.Row(
            [   
                dbc.Col(card_top_titres,width=4),
                dbc.Col(card_top_pays,width=4),
                dbc.Col(card_pourcentage_commentaires,width=4)
            ],
        ),
        dbc.Row([],style={'height':'3vh'},),
        dbc.Row(
            [
                dbc.Col(card_positifs, width=6),
                dbc.Col(card_negatifs,width=6)
            ],
        ),
    ],
    fluid=True, #pour que l'ensembles des cartes ne soient pas "figées"
)

#-------------------------callbacks------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------

@callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='top_titres',component_property='srcDoc'),
    Output(component_id='top_pays',component_property='srcDoc'),
    Output(component_id='pourcentage_avis_positifs',component_property='children'),
    Output(component_id='pourcentage_avis_negatifs',component_property='children'),
    Output(component_id='fig_avis_positifs',component_property='src'),
    Output(component_id='fig_avis_negatifs',component_property='src'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown',component_property='value'),
    Input(component_id='notes-dropdown',component_property='value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date')
)

def update_output(decision_hotel,choix_groupe,start_date,end_date):
    autotitres = ['Fabuleux ','Bien ','Passable','Assez médiocre ','Médiocre ']
    dff=df.loc[start_date:end_date]
    if choix_groupe==3:
        df_select=dff[dff.level_hotel==decision_hotel]
    else:
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
    
    if len(df_select)==0:
        percentplus=0
        percentmoins=0
        titres=pd.DataFrame([{'index': 'Néant', 'review_title': 0}])
        pays=pd.DataFrame([{'index':'Néant','country':0}])
        avisplus=r'assets/closed.png'
        avismoins=r'assets/closed.png'
        encoded_image_avisplus = base64.b64encode(open(avisplus, 'rb').read())
        encoded_image_avismoins = base64.b64encode(open(avismoins, 'rb').read())
    else :
        titres=df_select[~df_select.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
        pays=df_select.country.value_counts().reset_index().head(5)
        nplus=count_avis(df_select,'positive_review')
        nmoins=count_avis(df_select,'negative_review')
        percentplus=round((1-nplus/len(df_select))*100,3)
        percentmoins=round((1-nmoins/len(df_select))*100,3)
        avisplus=word_cloud(df_select,'positive_review')
        avismoins=word_cloud(df_select,'negative_review') 
        encoded_image_avisplus = base64.b64encode(open(avisplus, 'rb').read())
        encoded_image_avismoins = base64.b64encode(open(avismoins, 'rb').read())

    titres=titres.rename(columns={"index": "Titres", "review_title": "Effectifs"})
    titres = titres.style.set_properties(**{'color': 'white','font-size': '20pt',})
    pays=pays.rename(columns={"index": "Pays", "country": "Effectifs"})
    pays = pays.style.set_properties(**{'color': 'white','font-size': '20pt',})
    return titres.to_html(index=False,header=False),pays.to_html(index=False,header=False),percentplus,percentmoins,'data:image/png;base64,{}'.format(encoded_image_avisplus.decode()),'data:image/png;base64,{}'.format(encoded_image_avismoins.decode())
    