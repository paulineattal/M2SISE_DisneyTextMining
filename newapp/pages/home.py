#importation des librairies pour page d'accueil
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

#path='/' pour que ce soit la page d'accueil
#order =0 : en première position dans la barre de navigation
dash.register_page(__name__, path='/', order=0)

#le layout constitue la trame de la page
layout = html.Div([
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
            html.Img(src='assets/castle.jpg')
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
                    #correspondent aux tirets
                    html.Ul([
                        html.Li('La moyenne des notes'),
                        html.Li('Le pourcentage du groupe sélectionné'),
                        html.Li('Un graphique avec, par mois et année,'),
                        html.Li('le nombre de nuit et la moyenne des notes')
                    ])
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
])
