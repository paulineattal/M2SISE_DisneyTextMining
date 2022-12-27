import dash
from dash import html, dcc, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from gettext import install
from datetime import datetime as dt
from .side_bar import sidebar
from dash import Dash
from dash.dependencies import Input, Output
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import mpld3

dash.register_page(__name__, title='Résumé', order=1)

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

#Définition d'une carte qui créer un titre pour l'application
card_title=dbc.Card([
                    dbc.CardBody([
                            #écriture du texte dans le corps de la carte
                            #html.H2("Disney Booking",className="Card-title",style={'textAlign': 'center','font-size':50}),
                            sidebar()
                            ])
                    ],
                    color="white", #choix de la couleur
                    inverse=False, #pour que le texte soit en blanc (sur fond noir)
                    outline=False, #True enlève la couleur de la carte
                    style={'height':'100%'},
                )


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
    return dbc.Container([
    dbc.Row(
        [
            dbc.Col(card_title,width=2),
            dbc.Col(card_date,width=4),
            dbc.Col(card_filter_hotel,width=3),
            dbc.Col(card_filter_notes,width=3),
            
        ]
    ),
    dbc.Row([],style={'height':'3vh'},),
    dbc.Row(
            [
                dbc.Col(card_moyenne_pourcentage_groupe,width=2),
                dbc.Col(card_sunburst,width=10),
            ],
    ),
],
fluid=True,
)

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
    if decision_hotel==6:
        df_select3=dff[dff.hotel=="Disney's Newport Bay Club"]
        df_select2=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review>=8)]
        df_select1=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review<8) & (dff.grade_review>5)]
        df_select0=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review<=5)]
        if choix_groupe==3: 
            note=round(df_select3.grade_review.mean(),3)
            percentgroup=100
            sun=sungraph(df_select3)
        elif choix_groupe==2:
            note=round(df_select2.grade_review.mean(),3)
            percentgroup=round(len(df_select2)*100/len(df_select3),3)
            sun=sungraph(df_select2)
        elif choix_groupe==1:
            note=round(df_select1.grade_review.mean(),3)
            percentgroup=round(len(df_select1)*100/len(df_select3),3)
            sun=sungraph(df_select1)
        elif choix_groupe==0:
            note=round(df_select0.grade_review.mean(),3)
            percentgroup=round(len(df_select0)*100/len(df_select3),3)
            sun=sungraph(df_select0)
    return note,percentgroup,sun