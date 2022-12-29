import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', order=0)

layout = html.Div([
    dcc.Markdown('# Web Scraping', style={'textAlign':'center'}),
    dcc.Markdown('Booking', style={'textAlign': 'center'}),

    dcc.Markdown('### Summary', style={'textAlign': 'center'}),
    html.Hr(),
    dcc.Markdown('Projet du Master SISE concernant le web scrapping de booking. \n'
                 'Lorsque vous cliquer sur projets : vous aurez un premier résumé du fichier et un accès à deux applications. \n'
                 'vous devez resélectionner vos choix pour chaque partie',
                 style={'textAlign': 'center', 'white-space': 'pre'}),

    dcc.Markdown('### Description applications', style={'textAlign': 'center'}),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            #dcc.Markdown('Résumé', style={'textAlign': 'center'})
            html.Img(src='assets/castle.jpg')
            ],width=2), 
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('App 1', style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Trois champs peuvent être modifiés \n'
                                'Dates, Hôtel, groupe selon la note',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    html.Ul([
                        html.Li('Les dates vont de décembre 2019 à mars 2022'),
                        html.Li('Actuellement, seul hôtel pouvant être sélectionné : Newport Bay Club'),
                        html.Li('Trois groupes proposés selon les notes'),
                        html.Li('Ensemble de KPI et de graphique évoluant selon ces champs ')
                    ])
                ], width=5)
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Markdown('App 2',
                                style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Trois champs peuvent être modifiés \n'
                                'Dates, Hôtel, groupe selon la note',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    html.Ul([
                        html.Li('Les dates vont de décembre 2019 à mars 2022'),
                        html.Li('Actuellement, seul hôtel pouvant être sélectionné : Newport Bay Club'),
                        html.Li('Trois groupes proposés selon les notes'),
                        html.Li('Ensemble de KPI et de graphique évoluant selon ces champs ')
                    ])
                ], width=5)
            ], justify='center'),

            dbc.Row([
                dbc.Col([
                    dcc.Markdown('App 3',
                                style={'textAlign': 'center'})
                ], width=2),
                dbc.Col([
                    dcc.Markdown('Trois champs peuvent être modifiés \n'
                                'Dates, Hôtel, groupe selon la note',
                                style={'white-space': 'pre'},
                                className='ms-3'),
                    html.Ul([
                        html.Li('Les dates vont de décembre 2019 à mars 2022'),
                        html.Li('Actuellement, seul hôtel pouvant être sélectionné : Newport Bay Club'),
                        html.Li('Trois groupes proposés selon les notes'),
                        html.Li('Ensemble de KPI et de graphique évoluant selon ces champs ')
                    ])
                ], width=5)
            ], justify='center'),
        ],width=10),
    ])
])