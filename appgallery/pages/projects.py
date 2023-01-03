import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from .side_bar import sidebar
from datetime import datetime as dt
import numpy as np
import psycopg2

dash.register_page(__name__, title='App1', order=1)

# try:
#     conn = psycopg2.connect(
#           user = "m139",
#           password = "m139",
#           host = "db-etu.univ-lyon2.fr",
#           port = "5432",
#           database = "m139"
#     )
#     cur = conn.cursor()
#     reservation = "SELECT * FROM reservation"
#     client = "SELECT * FROM client"
#     hotel = "SELECT * FROM hotel"
#     room = "SELECT * FROM room"
#     date = "SELECT * FROM date"

#     cur.execute(reservation)
#     reservation = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
#     cur.execute(client)
#     client = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
#     cur.execute(hotel)
#     hotel = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
#     cur.execute(room)
#     room = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
#     cur.execute(date)
#     date = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

#     cur.close()
#     conn.close()
# except (Exception, psycopg2.Error) as error :
#     print ("Erreur lors de la connexion à PostgreSQL", error)


# hotel_room = hotel.merge(room, on="id_hotel")
# res_client = reservation.merge(client, on="id_client")
# res_client_date = res_client.merge(date, on="id_date")
# df = res_client_date.merge(hotel_room, on="id_room")

# conditionlist_hotel = [
#     (df['hotel'] == "Disney's Newport Bay Club"),
#     (df['hotel'] == "New_York")
#     (df['hotel'] == "Sequoia_Lodge")
#     (df['hotel'] == "Cheyenne")
#     (df['hotel'] == "Santa_Fe")
#     (df['hotel'] == "Davy_Crockett_Ranch")
#     ]
# choicelist_hotel = [6,5,4,3,2,1]
# df['level_hotel'] = np.select(conditionlist_hotel, choicelist_hotel, default='Not Specified')

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
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

#Définition d'une carte pour filtrer selon l'hôtel et le groupe (notes)
card_filter_hotel=dbc.Card([
                        dbc.CardBody([
                            html.H4("l'hôtel",className="Card-text"),
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
                                html.H4("le groupe selon les notes",className="Card-text"),
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

#Définition d'une carte pour la variable moyenne des notes et le pourcentage du groupe
card_moyenne_pourcentage_groupe=dbc.Card([
                        dbc.CardBody([
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
                        #affichage du diagramme circulaire âge (output) 
                        #en fonction du genre (input)
                        dcc.Graph(id='fig_sunburst',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'height':'100%'},
                    ) 

def layout():
    #return html.Div([
    return dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar()
                ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

            dbc.Col(
                [
                    html.H3('Premier résumé', style={'textAlign':'center'}),

                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
        ]
    ),
    dbc.Row(
        [
            #dbc.Col(card_date,width=5),
            #dbc.Col(card_filter_hotel,width=4),
            #dbc.Col(card_filter_notes,width=3),
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
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='moyenne_note',component_property='children'),
    Output(component_id='pourcentage_groupe',component_property='children'),
    Output(component_id='fig_sunburst',component_property='figure'),
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
        percentgroup=100
    else :
        df_select=dff[(dff.level_hotel==decision_hotel) & (dff.level_grade_review==choix_groupe)]
        df_all=dff[(dff.level_hotel==decision_hotel)]
        percentgroup=round(len(df_select)*100/len(df_all),3)
    note=round(df_select.grade_review.mean(),3)
    sun=sungraph(df_select)
    return note,percentgroup,sun