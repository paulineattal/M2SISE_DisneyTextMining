import dash
from dash import dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, order=2)

def layout():
    return dbc.Row([
        dbc.Col([
            dcc.Markdown('# Web Scrapping ', className='mt-3',style={'textAlign': 'center'}),
            dcc.Markdown('### Booking', className='mb-5',style={'textAlign': 'center'}),
            dcc.Markdown('Email', style={'color':'gray'}),
            dcc.Markdown('pauline.attal@univ-lyon2.fr', style={'color':'blue'}),
            dcc.Markdown('christelle.cornu1@univ-lyon2.fr',style={'color':'blue'}),
            dcc.Markdown('t.houde@univ-lyon2.fr', style={'color':'blue'}),
            dcc.Markdown('nawres.dhiflaoui@univ-lyon2.fr',style={'color':'blue'}),
            #dcc.Markdown('Git Hub', style={'color': 'purple'}),
            #dcc.Markdown('[github.com/paulineattal/Disney-Text-Mining/](https://github.com/paulineattal/Disney-Text-Mining)', link_target='_blank'),
        ], 
        width={"size":6,"offset":2},
        )
    ],
    justify='center',
    )