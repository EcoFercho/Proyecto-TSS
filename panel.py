import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import interfaz
import algoritmo

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Simulacion de ahorros"

SIDEBAR_STYLE = {"position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "250px", "padding": "20px", "background-color": "#343a40", "color": "white"}
CONTENT_STYLE = {"margin-left": "260px", "padding": "20px"}

sidebar = html.Div([
    html.H3("Dashboard DashBoard", className="text-center"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Simulador", href="/simulacion", active="exact"),
    ], vertical=True, pills=True)
], style=SIDEBAR_STYLE)

navbar = dbc.Navbar(
    dbc.Container([
        html.Div("Taller de Simulacion de Sistemas - Simulador de Ahorros", className="navbar-brand text-white"),
    ]),
    color="dark", dark=True
)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    navbar,
    content,
    dcc.Store(id="store-resultados")
])

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/simulacion":
        return interfaz.layout()
    return html.Div([html.H3("Página no encontrada")])

interfaz.register_callbacks(app)

@app.callback([
    Output('resultados-texto', 'children'),
    Output('store-resultados', 'data')
], Input('calcular-proyecciones', 'n_clicks'),
State('salario-mensual', 'value'), 
State('meses-ahorro', 'value'),
State('tasa-crecimiento', 'value'),
State('upload-data', 'contents'))
def calcular_proyecciones(n_clicks, salario_mensual, meses_ahorro, tasa_crecimiento, contents):
    return algoritmo.calcular_proyecciones(n_clicks, salario_mensual, meses_ahorro, tasa_crecimiento, contents)

if __name__ == '__main__':
    app.run_server(debug=True)