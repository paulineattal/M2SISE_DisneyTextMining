#importations des librairies
import dash
from dash import Dash, html, dcc, Output, Input, callback, dash_table
import pandas as pd
import plotly.express as px
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
                dbc.Col([
                    dcc.Dropdown(id='data-set', multi=False, value='fichier',options=[{'label':'ouvrir', 'value':'fichier'}]),
                    dcc.Store(id='store-data',storage_type='memory'), 
                ],width=5),
                ])
            #dcc.Store(id='store-data',storage_type='memory'), 
        ],
        fluid=True,
    ),
    #couleurs de la barre de navigation
    dark=True,
    color='secondary'
)

#on met le NavBar dans le layout
#dash.page_container permet d'avoir un nouveau chemin dans le navigateur
#celui-ci est en lien avec les intitulé des différentes pages "enregistrées" (register) 
app.layout = dbc.Container([header, dash.page_container],fluid=False)

@callback(Output('store-data','data'),Input('data-set', 'value'))

def store_data(value):
    if value=='fichier':
        
    #importation de la BDD sur Postgrey à partir d'une connexion
        try:
            #créer la connexion à la Base De Données
            conn = psycopg2.connect(
                user = "m139",
                password = "m139",
                host = "db-etu.univ-lyon2.fr",
                port = "5432",
                database = "m139"
            )
    
            #conn.cursor() pour créer un objet curseur Psycopg2. 
            #cette méthode crée un nouvel objet psycopg2.extensions.cursor.
            cur = conn.cursor()
            #sélection des champs à partir des diverses tables : reservation, client, hotel, room, date
            reservation = "SELECT * FROM reservation"
            client = "SELECT * FROM client"
            hotel = "SELECT * FROM hotel"
            room = "SELECT * FROM room"
            date = "SELECT * FROM date"
    
            #exécuter requête de sélection avec cur.execute()
            cur.execute(reservation)
            #fetchall() pour tout extraire
            reservation = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            cur.execute(client)
            client = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            cur.execute(hotel)
            hotel = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            cur.execute(room)
            room = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
            cur.execute(date)
            date = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

            #fermer curseur
            cur.close()
            #fermer page de connexion
            conn.close()
        except (Exception, psycopg2.Error) as error :
            print ("Erreur lors de la connexion à PostgreSQL", error)

        #jointure des tables pour réaliser le dataframe
        hotel_room = hotel.merge(room, on="id_hotel")
        res_client = reservation.merge(client, on="id_client")
        res_client_date = res_client.merge(date, on="id_date")
        df = res_client_date.merge(hotel_room, on="id_room")
    return(df.to_dict('records'))

if __name__ == '__main__':
    #app.run_server(debug=True)
	app.run_server(debug=True,dev_tools_hot_reload=False)