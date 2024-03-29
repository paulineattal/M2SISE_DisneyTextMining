#importation des librairies
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime as dt
import numpy as np
import psycopg2
from .data import store_data

#Le titre de cette page sera project1 dans la barre de naviation (nom du fichier.py)
#en seconde position dans la barre de naviation car order =1
dash.register_page(__name__, order=1)

df=pd.DataFrame(store_data())

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

#------------------fonctions pour la traitement des données----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#fonction qui renvoi une sunburst en fonction de l'année puis du mois
#et renvoi les indicateurs suivants par mois : nombre de nuitées, moyenne des notes
#avec une échelle de valeurs colorée en fonction de la note moyenne obtenue
def sungraph(df):
    fig = px.sunburst(df, path=['year', 'month_str'], values='nuitee',
                  color='grade_review',
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df['grade_review'], weights=df['nuitee']))
    return(fig)

#Définition de la carte date
card_date=dbc.Card([

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
                    )

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
card_filter_hotel=dbc.Card([
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
                        )

card_filter_notes=dbc.Card([
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
                    )

#Définition d'une carte pour la variable moyenne des notes et le pourcentage du groupe
card_moyenne_pourcentage_groupe=dbc.Card([
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
                        )  

#Définition d'une carte pour le diagramme sunburst de fréquentation et notes
card_sunburst=dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='fig_sunburst',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'height':'100%'},
                    ) 

#rendu de cette page avec l'architecture des différentes cartes qui la compose
def layout():
    #return html.Div([
    return dbc.Container([
    dbc.Row(
        [
        dcc.Markdown('# Premier résumé', style={'textAlign': 'center'}),
        ]
    ),
    dbc.Row(
        [
            #regroupement des différentes cartes sans espaces entre elles
            dbc.CardGroup([card_date,card_filter_hotel,card_filter_notes])
        ]
    ),
    dbc.Row([],style={'height':'2vh'},),
    dbc.Row(
            [
                dbc.Col(card_moyenne_pourcentage_groupe,width=2),
                dbc.Col(card_sunburst,width=10),
            ],
    ),
])

#-------------------------callbacks------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------

@callback(
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
def update_output(decision_hotel,choix_groupe,start_date,end_date):
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
            sun=sungraph(df_select)
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
            sun=sungraph(df_select)
    return note,percentgroup,sun