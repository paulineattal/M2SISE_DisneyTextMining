#importations des librairies
from dash import Dash, html,dcc , Output, Input, callback, dash_table, State
import data as d
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

df=pd.DataFrame(d.store_data())

#------------------------------traitement du data frame-----------------------------------------
#-----------------------------------------------------------------------------------------------

#on passe la variable date sous forme de date
df['date']=pd.to_datetime(df['date'])
#on détermine la date la plus ancienne 
min=df.date.min()
#et celle la plus récente
#elles permettront de réactualiser aisément la  sélection dans le calendrier
max=df.date.max()
#on met les dates en index pour la sélection
# car ensuite nous utiliserons le picker range dans les inputs
df.set_index('date',inplace=True)

#-------------------dictionnaires-----------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Création d'un dictionnaire pour le filtre hôtel (dropdown)
hotel_dict=[{'label':html.Div(['Newport Bay Club'],style={'font-size':22}),'value':6},{'label':html.Div(['Art of Marvel'],style={'font-size':22}),'value':5},{'label':html.Div(['Sequoia Lodge'],style={'font-size':22}),'value':4},{'label':html.Div(['Cheyenne'],style={'font-size':22}),'value':3},{'label':html.Div(['Santa Fé'],style={'font-size':22}),'value':2},{'label':html.Div(['Davy Crockett Ranch'],style={'font-size':22}),'value':1}]

#Création d'un dictionnaire pour le filtre notes (dropdown)
notes_dict=[{'label':html.Div(['Toutes notes'],style={'font-size':22}),'value':3},{'label':html.Div(['note >=8'],style={'font-size':22}),'value':2},{'label':html.Div(['5 < note < 8'],style={'font-size':22}),'value':1},{'label':html.Div(['notes <= 5'],style={'font-size':22}),'value':0}]

#Création d'un dictionnaire pour le filtre clusters (dropdown)
clusters_dict=[{'label':html.Div(['Premier cluster'],style={'font-size':22}),'value':0},{'label':html.Div(['Second cluster'],style={'font-size':22}),'value':1},{'label':html.Div(['Troisième cluster'],style={'font-size':22}),'value':2}]

#------------------fonctions pour la traitement des données----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#définition de l'application avec plusieurs pages (use_pages=True)
#utilisation des thèmes BOOSTRAP
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions= True)
#pour que l'application puisse être déployée sur le net
server=app.server

app.layout = dbc.Container([
    html.Div([

    # Create Multipage on App
    dcc.Tabs([
        # Start Page 1
        dcc.Tab(label='Home', children=[

                dcc.Markdown('# Web Scraping', style={'textAlign':'center'}),
    dcc.Markdown('Booking', style={'textAlign': 'center'}),

    dcc.Markdown('### Résumé', style={'textAlign': 'center'}),
    #pour insérer un espace
    html.Hr(),
    dcc.Markdown('Projet du Master SISE concernant le web scrapping de booking. \n'
                 'Pour chaque projet (Projet 1, Projet 2, Projet 3), trois champs peuvent être modifiés :\n'
                 "la période, l'hôtel, le groupe de clients selon la note attribuée (clients promoteurs, passifs, détracteurs).\n"
                 'et le cluster (numéro 1, 2 ou 3) pour le dernier projet uniquement\n'
                 'vous devez resélectionner vos choix pour chaque projet',
                 style={'textAlign': 'center', 'white-space': 'pre'}),

    dcc.Markdown('### Description applications', style={'textAlign': 'center'}),
    html.Hr(),
    #division de la page deux colonnes avec une image à droite et le texte à gauche
    dbc.Row([
        dbc.Col([
            #insertion de l'image dans cette colonne
            html.Img(src='assets/castle.png')
            ],width=2), 
        #la seconde colonne est divisée en plusieurs lignes
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('Projet 1', style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Renvoi un premier résumé comprenant',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    #création d'une liste (qui correspond aux différents items) 
                    html.Ul([
                        #texte dans le première liste
                        html.Li('La moyenne des notes'),
                        html.Li('Le pourcentage du groupe sélectionné'),
                        html.Li('Un graphique avec, par mois et année,'),
                        html.Li('le nombre de nuit et la moyenne des notes')
                    ])
                #largeur de la colonne
                ], width=5)
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Markdown('Projet 2',
                                style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Renvoi un second résumé comprenant \n',
                                'une première analyse des textes avec',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    html.Ul([
                        html.Li('Le TOP 3 des  titres les plus donnés parmi des titres non automatiques'),
                        html.Li('Le TOP 5 des pays les plus représentés'),
                        html.Li("Les pourcentages d'avis positifs et négatifs"),
                        html.Li("Les nuages de mots des avis positifs et négatifs")
                    ])
                ], width=5)
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Markdown('Projet 3',
                                style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Renvoi un troisième résumé comprenant \n'
                                'une seconde analyse des textes avec',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    html.Ul([
                        html.Li('Le pourcentage de commentaires postés avec un délai de deux ou trois mois'),
                        html.Li('La moyenne des notes pour des commentaires postés avec un délai de deux ou trois mois'),
                        html.Li('Des clusters pour les avis positifs et néagtifs'),
                    ])
                ], width=5)
            ], justify='center'),
        ],width=10),
    ])

        # Close Page 1
        ]),
        # Start Page 2
        dcc.Tab(label='Analyse 1', children=[
            html.Div([

                #Définition de la carte date

# A echanger page 2                
dbc.Card([

                        dbc.CardBody([
                            html.H4("Sélectionner une période",className="Card-text"),
                            dcc.DatePickerRange(
                            id='date-picker-range2',
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
                    ),

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
dbc.Card([
                        dbc.CardBody([
                                html.H4("un hôtel",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='hotel-dropdown2',options=hotel_dict,value=6,style = {"color":"black"}),    
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

dbc.Card([
                        dbc.CardBody([
                                html.H4("un groupe de clients (notes)",className="Card-text"),
                                #création de la barre de défilement pour sélectionner le groupe
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='notes-dropdown2',options=notes_dict,value=3,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

##Définition d'une carte pour les titres non automatiques
dbc.Card([
                        dbc.CardBody([
                                #Iframe permettra de stocker et d'afficher ensuite le dataframe
                                #il intègre un fichier web dans un autre
                                html.Iframe(id ='top_titres',height=230)
                            ])
                        ],
                        color="danger",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'},
                        ),

#Définition d'une carte pour les pays (provenance des internautes)
dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id = 'top_pays',height=230)
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'}
                        ),

#Définition d'une carte pour le pourcentage de commentaires positifs et négatifs
dbc.Card([
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
                        ),

#Définition d'une carte pour les commentaires positifs
dbc.Card([
                    dbc.CardBody([
                        html.H4("Avis positifs",className="Card-text"),
                        #affichage word cloud sous forme d'image
                        html.Img(id='fig_avis_positifs')
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    #style={'height':'120vh'},
                    ), 

#Définition d'une carte pour les commentaires négatifs
dbc.Card([
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

             

                

            ])
        # Close Page 2
        ]),
                # Start Page 3
        dcc.Tab(label='Analyse 2', children=[
            html.Div([

                #Définition de la carte date

# A echanger page 3                
dbc.Card([

                        dbc.CardBody([
                            html.H4("Sélectionner une période",className="Card-text"),
                            #composant PickerRange pour les dates
                            dcc.DatePickerRange(
                            #définition de l'id de l'input
                            id='date-picker-range',
                            #dates minimales et maximales acceptées
                            min_date_allowed=min,
                            max_date_allowed=max,
                            #dates minimale et maximales sélectionnées par défaut
                            start_date=min.date(),
                            end_date=max.date(),
                            #orientation du calendrier lors de la sélection des dates
                            calendar_orientation='horizontal',
                            #un minimun de 15 jours entre les dates start et end
                            minimum_nights=15,
                            updatemode='singledate' #paramètre pour prendre en compte une seule modification de date ) la fois
                            #commencer par la date "start"
                            )  
                            ])
                    ],
                        color="secondary", #choix de la couleur (gris foncé)
                        inverse=True, #le texte est donc écrit en blanc sur fond gris foncé
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'}, #pour harmoniser la hauteur des cartes d'une même ligne
                        className="w-75", #élément qui a une largeur égale à 75% de celle de son parent
                    ),

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
dbc.Card([
                        dbc.CardBody([
                            html.H4("un hôtel",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='hotel-dropdown',options=hotel_dict,value=6,style = {"color":"black"}),
                                #sélection de l'hôtel New Port Bay Club par défaut (value=6)
                            ]),
                        ],       
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                        ),

dbc.Card([
                        dbc.CardBody([
                                html.H4("un groupe de clients (notes)",className="Card-text"),
                                #création de la barre de défilement pour sélectionner le groupe (par défaut tous (value=3))
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='notes-dropdown',options=notes_dict,value=3,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

#Définition d'une carte pour la variable moyenne des notes et le pourcentage du groupe
dbc.Card([
                        dbc.CardBody([
                                #Texte statique
                                html.H4("Moyenne notes",className="Card-text"),
                                #créer un espace entre le texte et l'indicateur
                                html.P('',style={'height':'0.5vh'}),
                                #affichage de l'output moyenne notes
                                html.H2(id='moyenne_note'),
                                html.P('',style={'height':'2vh'}),
                                html.H4("Pourcentage du groupe sélectionné",className="Card-text"),
                                #créer un espace entre le texte et l'indicateur
                                html.P('',style={'height':'0.5vh'},),
                                #affichage de l'output pourcentage groupe
                                html.H2(id='pourcentage_groupe')
                            ]),
                        ],
                        color="success",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center','height':'100%'},
                        ),

#Définition d'une carte pour le diagramme sunburst de fréquentation et notes
dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='fig_sunburst',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'height':'100%'},
                    )


            ])
        # Close Page 3
        ]),
                # Start Page 4
        dcc.Tab(label='Analyse 3', children=[
            html.Div([

                #Définition de la carte date
dbc.Card([

                        dbc.CardBody([
                            html.H4("Sélectionner une période",className="Card-text"),
                            dcc.DatePickerRange(
                            id='date-picker-range3',
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
                    ),

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
dbc.Card([
                        dbc.CardBody([
                                html.H4("un hôtel",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='hotel-dropdown3',options=hotel_dict,value=6,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

#Définition d'une carte pour le groupe de clients en fonction des notes
dbc.Card([
                        dbc.CardBody([
                                html.H4("un groupe de clients",className="Card-text"),
                                #création de la barre de défilement pour sélectionner le groupe
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='notes-dropdown3',options=notes_dict,value=3,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
dbc.Card([
                        dbc.CardBody([
                                html.H4("un cluster",className="Card-text"),
                                #création de la barre de défilement pour sélectionner l'hôtel
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='clusters-dropdown',options=clusters_dict,value=0,style = {"color":"black"}),  
                            ]),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    ),

#Définition d'une carte pour le pourcentage de délai et la moyenne des notes de cette catégorie
dbc.Card([
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
                        ),

#Définition d'une carte pour les types de séjours (famille, couple, etc)
dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id = 'type_sejour',height=220,width=400)
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'}
                        ), 

#Définition d'une carte pour les clusters sur avis positifs
dbc.Card([
                    dbc.CardBody([
                        html.H4("Clusters avis positifs",className="Card-text"),
                        dcc.Graph(id='clusters_positifs',figure={})
                        ])
                    ],
                    color="info",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    ),

#Définition d'une carte pour les clusters sur avis négatifs
dbc.Card([
                    dbc.CardBody([
                        html.H4("Clusters avis négatifs",className="Card-text"),
                        dcc.Graph(id='clusters_negatifs',figure={})
                        ])
                    ],
                    color="danger",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    )


            ])
        # Close Page 4
        ]),
                # Start Page 5
        dcc.Tab(label='Contact', children=[
            html.Div([

            dbc.Col([
            #Pour écrire le texte en Markdown avec margin top 3 (mt-3) entre le texte et la barre de navgation
            #texte centrer, écriture "Large" (#)
            dcc.Markdown('# Web Scrapping ', className='mt-3',style={'textAlign': 'center'}),
            #mb-5 : margin bottom 5
            dcc.Markdown('### Booking', className='mb-5',style={'textAlign': 'center'}),
            dcc.Markdown('Email', style={'color':'gray'}),
            dcc.Markdown('pauline.attal@univ-lyon2.fr', style={'color':'blue'}),
            dcc.Markdown('christelle.cornu1@univ-lyon2.fr',style={'color':'blue'}),
            dcc.Markdown('nawres.dhiflaoui@univ-lyon2.fr',style={'color':'blue'}),
            dcc.Markdown('t.houde@univ-lyon2.fr', style={'color':'blue'}),
            dcc.Markdown('Git Hub', style={'color': 'purple'}),
            #lien pour se connecter directement au Git Hub en cliquant sur le lien
            dcc.Markdown('[github.com/paulineattal/Disney-Text-Mining/](https://github.com/paulineattal/Disney-Text-Mining)', link_target='_blank'),
        ], 
        #largeur de l'espace pour le texte et offset:2 pour pousser la colonne plus à droite
        width={"size":6,"offset":2},
        )

                

            ])
        # Close Page 5
        ])
    # Close Tabs
    ])
])

# Dbc Container
])

# Page 1 callback
@app.callback(
    #les différentes sorties qui seront répercutées dans les cartes 
    #lors du return de la fonction update_output
    Output(component_id='moyenne_note',component_property='children'),
    Output(component_id='pourcentage_groupe',component_property='children'),
    Output(component_id='fig_sunburst',component_property='figure'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown',component_property='value'),
    Input(component_id='notes-dropdown',component_property='value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date')
)

#fonction qui retourne l'ensemble des outputs en fonction des inputs sélectionnés
def update_page1(decision_hotel,choix_groupe,start_date,end_date):
    #sélection d'une partie du data frame selon les dates de début et fin sélectionnées
    dff=df.loc[start_date:end_date]
    #sélection du dataframe sur l'hôtel et/ou le groupe selon la note attribuée
    if choix_groupe==3: #pas de sélection sur le groupe par rapport à la note attribuée
        df_select=dff[dff.level_hotel==decision_hotel] 
        #cas où l'hôtel est fermé sur cette période
        if len(df_select)==0:
            percentgroup=0
            note=0
            #aucune figure
            sun = {}
        else:
            percentgroup=100
            note=round(df_select.grade_review.mean(),3)
            sun=d.sungraph(df_select)
    else :
        #sélection de l'hôtel et du groupe en fonction de la note
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
        df_all=dff[(dff.level_hotel==decision_hotel)]
        #gestion éventuelle du cas où il n'y aurait personne dans l'hôtel sur la période donnée
    
        if len(df_all)==0:
            percentgroup=0
            note=0
            sun={}
        #calcul du pourcentage nombre de personne ayant fréquenté l'hôtel sur la période 
        #et ayant mis une note dans la fourchette choisie
        #par rapport au nombre de personnes présentes dans cet hôtel sur la même période
        else :
        #Les résultats sont arrondis au millième
            percentgroup=round(len(df_select)*100/len(df_all),3)
            note=round(df_select.grade_review.mean(),3)
            sun=d.sungraph(df_select)
    return note,percentgroup,sun

# Callback page 2
@app.callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='top_titres',component_property='srcDoc'),
    Output(component_id='top_pays',component_property='srcDoc'),
    Output(component_id='pourcentage_avis_positifs',component_property='children'),
    Output(component_id='pourcentage_avis_negatifs',component_property='children'),
    Output(component_id='fig_avis_positifs',component_property='src'),
    Output(component_id='fig_avis_negatifs',component_property='src'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown2',component_property='value'),
    Input(component_id='notes-dropdown2',component_property='value'),
    Input('date-picker-range2','start_date'),
    Input('date-picker-range2','end_date')
)

def update_page2(decision_hotel,choix_groupe,start_date,end_date):
    #listes des titres automatisés que nous supprimerons pour choisir le TOP 3 des titres
    autotitres = ['Fabuleux ','Bien ','Passable','Assez médiocre ','Médiocre ']
    #sélection d'une partie du data frame selon les dates de début et fin sélectionnées
    dff=df.loc[start_date:end_date]
    if choix_groupe==3:
        #sélection de tous les avis de l'hôtel sur la période choisie
        df_select=dff[dff.level_hotel==decision_hotel]
    else:
        #sélection de tous les avis d'un groupe choisi sur la période choisie
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
    #cas où l'hôtel est fermé sur cette période
    if len(df_select)==0:
        percentplus=0
        percentmoins=0
        titres=pd.DataFrame([{'index': 'Néant', 'review_title': 0}])
        pays=pd.DataFrame([{'index':'Néant','country':0}])
        #image hôtel fermé
        avisplus=r'assets/closed.png'
        avismoins=r'assets/closed.png'
        #encodage pour l'image et (open(...,'rb').read()) pour lire l'image
        encoded_image_avisplus = base64.b64encode(open(avisplus, 'rb').read())
        encoded_image_avismoins = base64.b64encode(open(avismoins, 'rb').read())
    else :
        #sélection des 3 titres les plus apposés
        titres=df_select[~df_select.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
        #sélection des 5 nationalités les plus représentées
        pays=df_select.country.value_counts().reset_index().head(5)
        #nombre de commentaires positifs
        nplus=d.count_avis(df_select,'positive_review')
        nmoins=d.count_avis(df_select,'negative_review')
        #pourcentage de commentaires positifs
        percentplus=round((1-nplus/len(df_select))*100,3)
        percentmoins=round((1-nmoins/len(df_select))*100,3)
        #recupération des chemins pour accéder aux images word cloud
        avisplus=d.word_cloud(df_select,'positive_review')
        avismoins=d.word_cloud(df_select,'negative_review') 
        #encodage et affichage
        encoded_image_avisplus = base64.b64encode(open(avisplus, 'rb').read())
        encoded_image_avismoins = base64.b64encode(open(avismoins, 'rb').read())
    #gestion de l'affichage des tableaux
    #renomage des colonnes
    titres=titres.rename(columns={"index": "Titres", "review_title": "Effectifs"})
    #style du tableau : couleur du texte des cellules en blanc et taille de ce texte
    titres = titres.style.set_properties(**{'color': 'white','font-size': '20pt',})
    pays=pays.rename(columns={"index": "Pays", "country": "Effectifs"})
    pays = pays.style.set_properties(**{'color': 'white','font-size': '20pt',})
    return titres.to_html(index=False,header=False),pays.to_html(index=False,header=False),percentplus,percentmoins,'data:image/png;base64,{}'.format(encoded_image_avisplus.decode()),'data:image/png;base64,{}'.format(encoded_image_avismoins.decode())

# Callback Page 3        
@app.callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='pourcentage_delai',component_property='children'),
    Output(component_id='moyenne_delai',component_property='children'),
    Output(component_id='type_sejour',component_property='srcDoc'),
    Output(component_id='clusters_positifs',component_property='figure'),
    Output(component_id='clusters_negatifs',component_property='figure'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown3',component_property='value'),
    Input(component_id='notes-dropdown3',component_property='value'),
    Input(component_id='clusters-dropdown',component_property='value'),
    Input('date-picker-range3','start_date'),
    Input('date-picker-range3','end_date')
)

def update_page3(decision_hotel,choix_groupe,choix_cluster,start_date,end_date):
    dff=df.loc[start_date:end_date]
    if choix_groupe==3: 
        df_select=dff[dff.level_hotel==decision_hotel]
    else:
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
    
    if len(df_select)==0 :
        percentdelai=0
        moyennedelai=0
        sejour=pd.DataFrame([{'id_client': 'Néant', 'grade_review': 0}])
        #absence de figure (barplot) pour les clusters
        cap={}
        can={}
    else :
        #pourcentage de commentaires dont le délai est supérieur ou égal à 2 mois
        percentdelai=round(len(df_select[df_select.delay_comment>=2])*100/len(df_select),3)
        #moyenne de ces commentaires
        moyennedelai=round(df_select[df_select.delay_comment>=2]['grade_review'].mean(),3)

        #pourcentage par type de séjours (en famille, groupe, couple, individuel) dans un data frame
        #le pourcentage est stocké dans la colonne id_client
        d1=df_select.groupby(['traveler_infos'])[['id_client','country']].count()*100/len(df_select)
        #moyenne des notes par type de séjour dans un dataframe 
        #la moyenne est stockée dans la colonne grade review
        d2=df_select.groupby(['traveler_infos'])[['grade_review','nuitee']].mean()
        #regroupement des deux dataframes selon le type de séjour
        df_sejour=pd.merge(d1,d2,on='traveler_infos')
        #sélection des colonnes où il y a les pourcentages et les moyennes
        var=['id_client','grade_review']
        #réduction du dataframe "mergé" en un dataframe comporatnt uniquement les informations nécessaires
        sejour=df_sejour[var]
        #création du corpus liste avec les commentaires positifs puis négatifs
        corpusplus=d.creation_corpus_liste(df_select,'positive_review')
        corpusneg=d.creation_corpus_liste(df_select,'negative_review')
        #création du barplot des mots selon le choix du cluster à partir des corpus précédents
        cap=d.clusters(corpusplus,choix_cluster,'positive_review')
        can=d.clusters(corpusneg,choix_cluster,'negative_review')
    #renommage des colonnes
    sejour=sejour.rename(columns={"id_client": "pourcentages","grade_review":"moyenne"})
    #gestion du style du tableau
    sejour = sejour.style.set_properties(**{'color': 'white','font-size': '20pt',})
    #affichage des nombres dans le tableau avec une précision au millième
    sejour=sejour.format(precision=3)
    
    return percentdelai,moyennedelai,sejour.to_html(index=False,header=True),cap,can

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)