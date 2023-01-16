#importations des librairies
import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
import gunicorn
import base64
import io

#définition de l'application
#utilisation des thèmes BOOSTRAP
app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
#pour que l'application puisse être déployée sur le net
server=app.server

#un composant de naviagtion
header = dbc.Navbar(
    #définition du contener qui comportera des pages avec les liens
    dbc.Container(
        [
            dbc.Row([
                dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Nav([
                        dbc.NavLink(page["name"], href=page["path"])
                        for page in dash.page_registry.values()
                        #if not page["path"].startswith("/app")
                    ])
            ])
        ],
        fluid=True,
    ),
    dark=True,
    color='secondary'
)

app.layout = dbc.Container([header, dash.page_container], fluid=False)

if __name__ == '__main__':
    #app.run_server(debug=True)
	app.run_server(debug=True,dev_tools_hot_reload=False)