import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import interfaz
import generarReporte

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Simulador de Ahorros"

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "250px",
    "padding": "20px",
    "background-color": "#343a40",
    "color": "white",
    "overflow-y": "auto"
}

CONTENT_STYLE = {
    "margin-left": "280px",
    "padding": "20px",
    "background-color": "#f8f9fa"
}

# Componentes UI
sidebar = html.Div([
    html.H3("Dashboard", className="text-center mb-4"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Simulador", href="/simulacion", active="exact"),
    ], vertical=True, pills=True, className="mb-4")
], style=SIDEBAR_STYLE)

navbar = dbc.Navbar(
    dbc.Container([
        html.Div(
            "Taller de Simulación - Simulador de Ahorros",
            className="navbar-brand"
        ),
    ]),
    color="dark",
    dark=True,
    sticky="top"
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    navbar,
    content,
    dcc.Store(id="store-resultados"),
    dcc.Store(id="store-file-data"),
    dcc.Download(id="descargar-reporte")
])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/" or pathname == "/simulacion":
        return interfaz.layout()
    return html.Div([
        dbc.Alert(
            "Página no encontrada - 404",
            color="danger",
            className="mt-5"
        )
    ])

# Registrar callbacks
interfaz.register_callbacks(app)
generarReporte.register_callbacks(app)

# Exponer servidor para Gunicorn en producción
server = app.server

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=True)
