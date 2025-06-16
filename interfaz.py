import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, Input, Output, State
import dash_table
import base64
import io

def layout():
    return html.Div([
        html.H3("Proyecciones de ahorro"),
        
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
        dbc.Tabs([
            dbc.Tab(label="Ingreso de datos", tab_id="tab-datos"),
            dbc.Tab(label="Calculo de proyecciones", tab_id="tab-calculos"),
            dbc.Tab(label="Comparación", tab_id="tab-comparacion"),
            dbc.Tab(label="Evolución", tab_id="tab-evolucion"),
            dbc.Tab(label="Detalle EDOs", tab_id="tab-edos"),
        ], id="tabs", active_tab="tab-datos"),
        html.Div(id="tabs-content"),
        dcc.Store(id='store-file-data')
    ])

def register_callbacks(app):
    @app.callback(
        [Output('output-data-upload', 'children'),
         Output('store-file-data', 'data')], 
        Input('upload-data', 'contents'), 
        State('upload-data', 'filename')
    )
    def update_output(contents, filename):
        if contents:
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_excel(io.BytesIO(decoded))
                file_data = df.to_json(date_format='iso', orient='split')
                
                table_display = html.Div([
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
                return table_display, file_data
            except Exception as e:
                error_msg = html.Div([f'Error al cargar el archivo: {str(e)}'], style={'color': 'red'})
                return error_msg, None
        
        return html.Div(['Suba un archivo Excel con sus datos de gastos']), None

    @app.callback(
        Output('tabs-content', 'children'), 
        [Input('tabs', 'active_tab')],
        [State('store-resultados', 'data')]
    )
    def update_tabs(active_tab, store_data):
        if not store_data and active_tab != "tab-datos":
            return dbc.Card(dbc.CardBody(
                html.Div([
                    html.H5("⚠️ No hay datos calculados"),
                    html.P("Por favor, primero:"),
                    html.Ol([
                        html.Li("Vaya a la pestaña 'Ingreso de datos'"),
                        html.Li("Cargue un archivo Excel (opcional)"),
                        html.Li("Presione el botón 'Calcular Proyecciones'")
                    ])
                ], style={'text-align': 'center', 'color': '#856404'})
            ), color="warning", outline=True)
        
        if active_tab == "tab-datos":
            return dbc.Card(dbc.CardBody(
                html.Div([
                    dcc.Upload(
                        id='upload-data', 
                        children=html.Div(['Arrastra o ', html.A('selecciona un archivo Excel')]),
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px', 
                            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 
                            'textAlign': 'center', 'margin': '10px 0'
                        }
                    ),
                    html.Div(id='output-data-upload'),
                ])
            ))
        elif active_tab == "tab-calculos":
            if store_data and 'calculos' in store_data:
                return dbc.Card(dbc.CardBody(store_data['calculos']))
            else:
                return dbc.Card(dbc.CardBody("No hay cálculos disponibles"))
        elif active_tab == "tab-comparacion":
            if store_data and 'comparacion' in store_data:
                return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['comparacion'])]))
            else:
                return dbc.Card(dbc.CardBody("No hay datos de comparación disponibles"))
        elif active_tab == "tab-evolucion":
            if store_data and 'evolucion' in store_data:
                return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['evolucion'])]))
            else:
                return dbc.Card(dbc.CardBody("No hay datos de evolución disponibles"))
        elif active_tab == "tab-edos":
            if store_data and 'detalle' in store_data:
                return dbc.Card(dbc.CardBody([dcc.Graph(figure=store_data['detalle'])]))
            else:
                return dbc.Card(dbc.CardBody("No hay datos de detalle disponibles"))