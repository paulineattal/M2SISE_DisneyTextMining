from gettext import install

from datetime import datetime as dt

#importation des librairies
from dash import Dash
import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
#from dash_extensions import Lottie
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
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
#from io import BytesIO
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
import mpld3


#permettra de gérer les cartes que l'on va créer, le style BOOTSTRAP peut être changer
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#pour pouvoir uploader sur le web
server=app.server

#chargement du fichier
df=pd.read_csv('df_clean_newport.csv',sep=';')

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

#fonction que renvoi un pourcentage
def pourcent(x):
    return x/np.sum(x)   

def mean_mark(n,k):
    if k==3:
        note=df[df.level_hotel==n].grade_review.mean()
    else :
        note=df[(df.level_hotel==n) & (df.level_grade_review==k)].grade_review.mean()
    return note

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

def word_cloud(df,champ):
    df_cloud=df[champ]
    df_cloud=df_cloud.drop(df_cloud.index[df_cloud.isnull()])
    df_cloud=df_cloud.reset_index()
    corpus_liste=[]
    for i in range(df_cloud.shape[0]-1):
        corpus_liste.append(nettoyage_doc(df_cloud.iloc[i,1]))
    str_text=[]
    for i in range(len(corpus_liste)):
        str_text.append(' '.join(corpus_liste[i]))
    final_text=' '.join(str_text)
    fig, ax=plt.subplots()
    nuage=WordCloud(background_color="white").generate(final_text) 
    ax.imshow(nuage,interpolation='bilinear')
    ax.axis("off")
    html_matplotlib=mpld3.fig_to_html(fig)
    #plt.show()
    return(html_matplotlib)

def sungraph(df):
    fig = px.sunburst(df, path=['year', 'month_str'], values='nuitee',
                  color='grade_review',
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df['grade_review'], weights=df['nuitee']))
    return(fig)

#----------------définition des cartes-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

#Définition d'une carte qui créer un titre pour l'application
card_title=dbc.Card([
                    dbc.CardBody([
                            #écriture du texte dans le corps de la carte
                            html.H2("Disney Booking",className="Card-title",style={'textAlign': 'center','font-size':50}),
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
                            html.H4("Selectionner une période entre décembre 2019 et mars 2022",className="Card-text"),
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
                                html.H4("Selectionner l'hôtel",className="Card-text"),
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
                                html.H4("Selectionner le groupe selon les notes",className="Card-text"),
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

##Définition d'une carte pour les titres non automatiques
card_top_titres=dbc.Card([
                        dbc.CardBody([
                                html.Iframe(id ='top_titres',height=230)
                                #html.H4("Top 3 : titres",className="Card-text"),
                                #créer un espace entre le texte et l'indicateur
                                #html.P('',style={'height':'1vh'},),
                                #affichage de l'output fun_o_no_succes en fonction du genre
                                #html.H2(id='top_titre')
                            ])
                        ],
                        color="danger",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'},
                        #style={'textAlign':'center','height':'100%'},
                        ) 

#Définition d'une carte pour les pays
card_top_pays=dbc.Card([
                        dbc.CardBody([
                                #html.H4("Top 5 : pays",className="Card-text"),
                                #affichage des pays sous forme de data frame
                                html.Iframe(id = 'top_pays',height=230)
                                #html.Iframe(id = 'top_pays',height=250,width=300)
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center'}
                        #style={'textAlign':'center','height':'100%'}
                        ) 

#Définition d'une carte pour le pourcentage de commentaires positifs et négatifs
card_pourcentage_commentaires=dbc.Card([
                        dbc.CardBody([
                                #affichage du pourcentage d'avis positifs
                                html.H4("Pourcentage d'avis positifs",className="Card-text"),
                                html.P('',style={'height':'0.5vh'}),
                                html.H2(id='pourcentage_avis_positifs'),
                                html.P('',style={'height':'2vh'}),
                                #affichage du pourcentage d'avis négatifs
                                html.H4("Pourcentage d'avis négatifs",className="Card-text"),
                                html.P('',style={'height':'0.5vh'}),
                                html.H2(id='pourcentage_avis_negatifs'),
                            ])
                        ],
                        color="info",
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

#Définition d'une carte pour les commentaires positifs
card_positifs=dbc.Card([
                    dbc.CardBody([
                        html.H4("Avis positifs",className="Card-text"),
                        #affichage word cloud
                        #dcc.Graph(id='fig_avis_positifs',figure={})
                        html.Iframe(id = 'fig_avis_positifs',srcDoc=None,height=520,width=650)
                        #html.Iframe(id = 'fig_avis_positifs',srcDoc=None,style={'width':'100%','height':'500px'})
                        #srcDoc=None pour positionner le graphique que l'on va construire
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
                        #affichage du diagramme en barres de la variable date (output) 
                        #en fonction du genre (input)
                        #dcc.Graph(id='scatter_chart',figure={})
                        html.Iframe(id = 'fig_avis_negatifs',srcDoc=None,height=520,width=650)
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    style={'textAlign':'center'}
                    #style={'height':'120vh'},
                    ) 

#Gestion de l'application avec les différentes cartes
app.layout = dbc.Container(
    #on indique le nombre de lignes et de colonnes 
    #permet d'avoir la structure de la page qui sera affichée
    [   dbc.Row(
            [
                dbc.Col(card_title),
                dbc.Col(card_date),
                dbc.Col(card_filter_hotel),
                dbc.Col(card_filter_notes),
            ],
            justify="end",
        ),
        dbc.Row(
            [   
                dbc.Col(card_moyenne_pourcentage_groupe),
                dbc.Col(card_top_titres),
                dbc.Col(card_top_pays),
                dbc.Col(card_pourcentage_commentaires)
            ],
        ),
        dbc.Row([],style={'height':'3vh'},),
        dbc.Row(
            [
                dbc.Col(card_sunburst,width=4),
                dbc.Col(card_positifs, width=4),
                dbc.Col(card_negatifs,width=4)
            ],
        ),
    ],
    fluid=True, #pour que l'ensembles des cartes ne soient pas "figées"
)

#-------------------------callbacks------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='moyenne_note',component_property='children'),
    Output(component_id='pourcentage_groupe',component_property='children'),
    Output(component_id='top_titres',component_property='srcDoc'),
    Output(component_id='top_pays',component_property='srcDoc'),
    Output(component_id='pourcentage_avis_positifs',component_property='children'),
    Output(component_id='pourcentage_avis_negatifs',component_property='children'),
    Output(component_id='fig_sunburst',component_property='figure'),
    Output(component_id='fig_avis_positifs',component_property='srcDoc'),
    Output(component_id='fig_avis_negatifs',component_property='srcDoc'),
    #les variables qui feront évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='hotel-dropdown',component_property='value'),
    Input(component_id='notes-dropdown',component_property='value'),
    Input('date-picker-range','start_date'),
    Input('date-picker-range','end_date')
)

def update_output(decision_hotel,choix_groupe,start_date,end_date):
    autotitres = ['Fabuleux ','Bien ','Passable','Assez médiocre ','Médiocre ']
    dff=df.loc[start_date:end_date]
    if decision_hotel==6:
        df_select3=dff[dff.hotel=="Disney's Newport Bay Club"]
        df_select2=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review>=8)]
        df_select1=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review<8) & (dff.grade_review>5)]
        df_select0=dff[(dff.hotel=="Disney's Newport Bay Club") & (dff.grade_review<=5)]
        if choix_groupe==3: 
            note=round(df_select3.grade_review.mean(),3)
            percentgroup=100
            titres=df_select3[~df_select3.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
            pays=df_select3.Country.value_counts().reset_index().head(5)
            percentplus=round((1-df_select3.positive_review.isnull().sum()/len(df_select3))*100,3)
            percentmoins=round((1-df_select3.negative_review.isnull().sum()/len(df_select3))*100,3)
            avisplus=word_cloud(df_select3,'positive_review')
            avismoins=word_cloud(df_select3,'negative_review')
            sun=sungraph(df_select3)
        elif choix_groupe==2:
            note=round(df_select2.grade_review.mean(),3)
            percentgroup=round(len(df_select2)*100/len(df_select3),3)
            titres=df_select2[~df_select2.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
            pays=df_select2.Country.value_counts().reset_index().head(5)
            percentplus=round((1-df_select2.positive_review.isnull().sum()/len(df_select2))*100,3)
            percentmoins=round((1-df_select2.negative_review.isnull().sum()/len(df_select2))*100,3)
            avisplus=word_cloud(df_select2,'positive_review')
            avismoins=word_cloud(df_select2,'negative_review')
            sun=sungraph(df_select2)
        elif choix_groupe==1:
            note=round(df_select1.grade_review.mean(),3)
            percentgroup=round(len(df_select1)*100/len(df_select3),3)
            titres=df_select1[~df_select1.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
            pays=df_select1.Country.value_counts().reset_index().head(5)
            percentplus=round((1-df_select1.positive_review.isnull().sum()/len(df_select1))*100,3)
            percentmoins=round((1-df_select1.negative_review.isnull().sum()/len(df_select1))*100,3)
            avisplus=word_cloud(df_select1,'positive_review')
            avismoins=word_cloud(df_select1,'negative_review')
            sun=sungraph(df_select1)
        elif choix_groupe==0:
            note=round(df_select0.grade_review.mean(),3)
            percentgroup=round(len(df_select0)*100/len(df_select3),3)
            titres=df_select0[~df_select0.review_title.isin(autotitres)].review_title.value_counts().reset_index().head(3)
            pays=df_select0.Country.value_counts().reset_index().head(5)
            percentplus=round((1-df_select0.positive_review.isnull().sum()/len(df_select0))*100,3)
            percentmoins=round((1-df_select0.negative_review.isnull().sum()/len(df_select0))*100,3)
            avisplus=word_cloud(df_select0,'positive_review')
            avismoins=word_cloud(df_select0,'negative_review')
            sun=sungraph(df_select0)
        titres=titres.rename(columns={"index": "Titres", "review_title": "Effectifs"})
        titres = titres.style.set_properties(**{'color': 'white','font-size': '20pt',})
        pays=pays.rename(columns={"index": "Pays", "Country": "Effectifs"})
        pays = pays.style.set_properties(**{'color': 'white','font-size': '20pt',})
    return note,percentgroup,titres.to_html(index=False,header=False),pays.to_html(index=False,header=False),percentplus,percentmoins,sun,avisplus,avismoins


if __name__ == "__main__":
    app.run_server(debug=True)