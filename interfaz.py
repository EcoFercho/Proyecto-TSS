import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_table
import base64
import io

def layout():
    return html.Div([
        html.H3("Proyecciones de ahorro"),
        dcc.Upload(id='upload-data', children=html.Div(['Arrastra o ', html.A('selecciona un archivo Excel')]),
                   style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
                          'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'}),
        html.Div(id='output-data-upload'),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Label('Salario Mensual (Bs.):', style={'font-weight': 'bold'}),
                    dcc.Input(id='salario-mensual', type='number', value=2362, step=1, style={'width': '100%'})
                ], width=4),
                dbc.Col([
                    html.Label('Meses de Ahorro:', style={'font-weight': 'bold'}),
                    dcc.Input(id='meses-ahorro', type='number', value=120, step=1, style={'width': '100%'})
                ], width=4),
                dbc.Col([
                    html.Label('Tasa de Crecimiento Salarial (% anual):', style={'font-weight': 'bold'}),
                    dcc.Input(id='tasa-crecimiento', type='number', value=2, step=0.1, style={'width': '100%'})
                ], width=4)
            ], className="g-2 align-items-end"),
            dbc.Button("Calcular Proyecciones", id='calcular-proyecciones', color="primary", className="mt-3")
        ]),
        html.Div(id='resultados-texto', className="mt-4"),
        dbc.Tabs([
            dbc.Tab(label="Comparación", tab_id="tab-comparacion"),
            dbc.Tab(label="Evolución", tab_id="tab-evolucion"),
            dbc.Tab(label="Detalle EDOs", tab_id="tab-edos"),
        ], id="tabs", active_tab="tab-comparacion"),
        html.Div(id="tabs-content")
    ])

def register_callbacks(app):
    @app.callback(Output('output-data-upload', 'children'), Input('upload-data', 'contents'), State('upload-data', 'filename'))
    def update_output(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_excel(io.BytesIO(decoded))
            return html.Div([
                html.H5(f"Archivo cargado: {filename}"),
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    page_size=10,
                    style_table={
                        'overflowX': 'auto',
                        'overflowY': 'auto',
                        'maxHeight': '400px',
                        'border': 'thin lightgrey solid'
                    },
                    style_cell={
                        'textAlign': 'right',
                        'padding': '10px',
                        'minWidth': '120px', 'width': '120px', 'maxWidth': '180px',
                        'whiteSpace': 'normal',
                        'fontFamily': 'Arial',
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    }
                )
            ])
        return html.Div(['Suba un archivo Excel con sus datos de gastos'])

    @app.callback(Output('tabs-content', 'children'), Input('tabs', 'active_tab'), State('store-resultados', 'data'))
    def update_tabs(active_tab, store_data):
        if not store_data:
            return html.Div("Primero calcule proyecciones.")

        if active_tab == "tab-comparacion":
            return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['comparacion'])]))
        elif active_tab == "tab-evolucion":
            return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['evolucion'])]))
        elif active_tab == "tab-edos":
            return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['detalle'])]))