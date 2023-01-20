#importations des librairies
import dash
from dash import Dash, html,dcc , Output, Input, callback, dash_table, State
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
import psycopg2
import gunicorn
import base64
import io

#définition de l'application avec plusieurs pages (use_pages=True)
#utilisation des thèmes BOOSTRAP
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
#pour que l'application puisse être déployée sur le net
server=app.server

#création d'un composant de navigation
header = dbc.Navbar(
    #définition du contener qui comportera des pages avec les liens
    dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Nav([
                        #pourchaque page, on créer un lien
                        dbc.NavLink(page["name"], href=page["path"])
                        for page in dash.page_registry.values()
                    ])
                ],width=10), 
        ]),
        ],
        fluid=True,
    ),
    #couleurs de la barre de navigation
    dark=True,
    color='secondary'
)

app.layout = dbc.Container([header, dash.page_container], fluid=False)

if __name__ == '__main__':
	app.run_server(debug=True,dev_tools_hot_reload=False)