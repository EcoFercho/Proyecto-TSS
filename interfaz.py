import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import io
import pandas as pd  
import base64

def layout():
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H3("Simulación de Proyecciones de Ahorro", className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Salario Mensual (Bs.):", html_for="salario-mensual", className="fw-bold"),
                        dbc.Input(
                            id="salario-mensual",
                            type="number",
                            value=2750,
                            min=0,
                            step=1,
                            className="mb-3"
                        )
                    ], md=4),
                    
                    dbc.Col([
                        dbc.Label("Meses de Ahorro:", html_for="meses-ahorro", className="fw-bold"),
                        dbc.Input(
                            id="meses-ahorro",
                            type="number",
                            value=120,
                            min=1,
                            step=1,
                            className="mb-3"
                        )
                    ], md=4),
                    
                    dbc.Col([
                        dbc.Label("Tasa Crecimiento Salarial (% anual):", html_for="tasa-crecimiento", className="fw-bold"),
                        dbc.Input(
                            id="tasa-crecimiento",
                            type="number",
                            value=2,
                            min=0,
                            step=0.1,
                            className="mb-3"
                        )
                    ], md=4)
                ], className="mb-4"),
                
                dbc.Accordion([
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Expectativas de Ingresos Futuros:", html_for="expectativas-ingresos"),
                                dcc.Dropdown(
                                    id="expectativas-ingresos",
                                    options=[
                                        {'label': 'Muy optimista', 'value': 0.9},
                                        {'label': 'Optimista', 'value': 0.95},
                                        {'label': 'Neutral', 'value': 1.0},
                                        {'label': 'Pesimista', 'value': 1.05},
                                        {'label': 'Muy pesimista', 'value': 1.1}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Tasa de Interés(Deudas futuras):", html_for="tasa-interes"),
                                dcc.Dropdown(
                                    id="tasa-interes",
                                    options=[
                                        {'label': 'Muy baja', 'value': 0.9},
                                        {'label': 'Baja', 'value': 0.95},
                                        {'label': 'Normal', 'value': 1.0},
                                        {'label': 'Alta', 'value': 1.05},
                                        {'label': 'Muy alta', 'value': 1.1}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Inflación esperada(Social):", html_for="inflacion"),
                                dcc.Dropdown(
                                    id="inflacion",
                                    options=[
                                        {'label': 'Muy baja (<2%)', 'value': 0.95},
                                        {'label': 'Baja (2-4%)', 'value': 1.0},
                                        {'label': 'Moderada (4-6%)', 'value': 1.05},
                                        {'label': 'Alta (6-10%)', 'value': 1.1},
                                        {'label': 'Muy alta (>10%)', 'value': 1.15}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Preferencias Temporales(Gasto):", html_for="preferencias-temporales"),
                                dcc.Dropdown(
                                    id="preferencias-temporales",
                                    options=[
                                        {'label': 'Muy al futuro', 'value': 0.9},
                                        {'label': 'Al futuro', 'value': 0.95},
                                        {'label': 'Balanceado', 'value': 1.0},
                                        {'label': 'Al presente', 'value': 1.1},
                                        {'label': 'Muy al presente', 'value': 1.15}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Educación Financiera:", html_for="educacion-financiera"),
                                dcc.Dropdown(
                                    id="educacion-financiera",
                                    options=[
                                        {'label': 'Muy alta', 'value': 0.9},
                                        {'label': 'Alta', 'value': 0.95},
                                        {'label': 'Media', 'value': 1.0},
                                        {'label': 'Baja', 'value': 1.1},
                                        {'label': 'Muy baja', 'value': 1.15}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Riesgo de Desempleo:", html_for="riesgo-desempleo"),
                                dcc.Dropdown(
                                    id="riesgo-desempleo",
                                    options=[
                                        {'label': 'Muy bajo', 'value': 0.9},
                                        {'label': 'Bajo', 'value': 0.95},
                                        {'label': 'Moderado', 'value': 1.0},
                                        {'label': 'Alto', 'value': 1.1},
                                        {'label': 'Muy alto', 'value': 1.2}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Situación Familiar:", html_for="situacion-familiar"),
                                dcc.Dropdown(
                                    id="situacion-familiar",
                                    options=[
                                        {'label': 'Soltero sin hijos', 'value': 0.9},
                                        {'label': 'Pareja sin hijos', 'value': 1.0},
                                        {'label': 'Pareja con 1 hijo', 'value': 1.1},
                                        {'label': 'Pareja con 2 hijos', 'value': 1.2},
                                        {'label': 'Monoparental', 'value': 1.25},
                                        {'label': 'Pareja con 3+ hijos', 'value': 1.3}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Gastos de Salud:", html_for="gastos-salud"),
                                dcc.Dropdown(
                                    id="gastos-salud",
                                    options=[
                                        {'label': 'Muy bajos', 'value': 0.9},
                                        {'label': 'Bajos', 'value': 0.95},
                                        {'label': 'Promedio', 'value': 1.0},
                                        {'label': 'Altos', 'value': 1.1},
                                        {'label': 'Muy altos', 'value': 1.2}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4),
                            
                            dbc.Col([
                                dbc.Label("Estabilidad Laboral:", html_for="estabilidad-laboral"),
                                dcc.Dropdown(
                                    id="estabilidad-laboral",
                                    options=[
                                        {'label': 'Muy estable', 'value': 0.9},
                                        {'label': 'Estable', 'value': 0.95},
                                        {'label': 'Moderada', 'value': 1.0},
                                        {'label': 'Inestable', 'value': 1.1},
                                        {'label': 'Muy inestable', 'value': 1.2}
                                    ],
                                    value=1.0,
                                    className="mb-4"
                                )
                            ], md=4)
                        ])
                    ], title="Variables que afectan al ahorro", item_id="variables-ahorro")
                ], start_collapsed=True, className="mb-4"),
                
                dbc.Row([
                    dbc.Col(
                        dbc.Button(
                            "Calcular Proyecciones",
                            id="calcular-proyecciones",
                            color="primary",
                            className="w-100"
                        ),
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Generar Reporte PDF",
                            id="generar-reporte",
                            color="success",
                            className="w-100",
                            disabled=True
                        ),
                        width="auto"
                    )
                ], className="g-3 mb-4"),
                
                html.Div(id="reporte-error"),
                
                dbc.Tabs([
                    dbc.Tab(label="Datos de Entrada", tab_id="tab-datos"),
                    dbc.Tab(label="Resumen Numérico", tab_id="tab-resumen"),
                    dbc.Tab(label="Comparación", tab_id="tab-comparacion"),
                    dbc.Tab(label="Evolución", tab_id="tab-evolucion"),
                    dbc.Tab(label="Detalle EDOs", tab_id="tab-edos"),
                ], id="tabs", active_tab="tab-datos", className="mb-4"),
                
                html.Div(id="tabs-content"),
                dcc.Download(id="descargar-reporte"),
                dcc.Store(id="store-resultados"),
                dcc.Store(id="store-file-data")
            ])
        ])
    ])

def register_callbacks(app):
    @app.callback(
        [Output("output-data-upload", "children"),
         Output("store-file-data", "data")],
        Input("upload-data", "contents"),
        State("upload-data", "filename")
    )
    def update_output(contents, filename):
        if not contents:
            return html.Div([
                dbc.Alert(
                    "Suba un archivo Excel con datos de gastos mensuales",
                    color="info",
                    className="mb-3"
                )
            ]), None
        
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            df = pd.read_excel(io.BytesIO(decoded))
            file_data = df.to_json(date_format='iso', orient='split')
            
            table = html.Div([
                dbc.Alert(
                    f"Archivo cargado: {filename}",
                    color="success",
                    className="mb-3"
                ),
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in df.columns],
                    page_size=10,
                    style_table={
                        'overflowX': 'auto',
                        'border': 'thin lightgrey solid',
                        'borderRadius': '5px',
                        'marginBottom': '20px'
                    },
                    style_cell={
                        'fontFamily': 'Arial',
                        'textAlign': 'left',
                        'padding': '10px',
                        'minWidth': '100px',
                        'whiteSpace': 'normal'
                    },
                    style_header={
                        'backgroundColor': '#343a40',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ]
                )
            ])
            return table, file_data
        except Exception as e:
            return dbc.Alert(
                f"Error procesando archivo: {str(e)}",
                color="danger",
                className="mb-3"
            ), None

    @app.callback(
        Output("tabs-content", "children"),
        [Input("tabs", "active_tab"),
         Input("store-resultados", "data")]
    )
    def render_tab_content(active_tab, resultados):
        if active_tab == "tab-datos":
            return dbc.Card([
                dbc.CardBody([
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div([
                            html.I(className="bi bi-cloud-arrow-up me-2"),
                            "Arrastra o selecciona un archivo Excel"
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'marginBottom': '20px'
                        },
                        multiple=False
                    ),
                    html.Div(id="output-data-upload")
                ])
            ])
        
        if not resultados:
            return dbc.Alert(
                "No hay datos disponibles. Por favor calcule las proyecciones primero.",
                color="warning",
                className="my-4"
            )
        
        if active_tab == "tab-resumen":
            datos = resultados["datos_entrada"]
            res = resultados["resultados"]
            
            return dbc.Card([
                dbc.CardBody([
                    html.H4("Resumen de Resultados", className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H5("Datos de Entrada", className="text-center mb-3"),
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    html.Div("Salario Bruto:", className="fw-bold"),
                                    f"Bs. {datos['salario']:,.2f}"
                                ]),
                                dbc.ListGroupItem([
                                    html.Div("Ingreso Neto:", className="fw-bold"),
                                    f"Bs. {datos['ingreso_neto']:,.2f}"
                                ]),
                                dbc.ListGroupItem([
                                    html.Div("Gasto Mensual:", className="fw-bold"),
                                    f"Bs. {datos['gasto']:,.2f}"
                                ]),
                                dbc.ListGroupItem([
                                    html.Div("Ahorro Mensual:", className="fw-bold"),
                                    f"Bs. {datos['ahorro_mensual']:,.2f}"
                                ]),
                                dbc.ListGroupItem([
                                    html.Div("Período:", className="fw-bold"),
                                    f"{datos['meses']} meses"
                                ]),
                                dbc.ListGroupItem([
                                    html.Div("Factor Ajuste:", className="fw-bold"),
                                    f"{datos['factor_ahorro']:.2f}"
                                ])
                            ], flush=True)
                        ], md=4),
                        
                        dbc.Col([
                            html.H5("Fórmula Simple", className="text-center mb-3"),
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    html.Div("0% Interés:", className="fw-bold"),
                                    f"Bs. {res['simple_0']:,.2f}"
                                ], color="primary"),
                                dbc.ListGroupItem([
                                    html.Div("3% Interés:", className="fw-bold"),
                                    f"Bs. {res['simple_3']:,.2f}"
                                ], color="danger"),
                                dbc.ListGroupItem([
                                    html.Div("7% Interés:", className="fw-bold"),
                                    f"Bs. {res['simple_7']:,.2f}"
                                ], color="success")
                            ], flush=True)
                        ], md=4),
                        
                        dbc.Col([
                            html.H5("Modelo EDO", className="text-center mb-3"),
                            dbc.ListGroup([
                                dbc.ListGroupItem([
                                    html.Div("3% Interés:", className="fw-bold"),
                                    f"Bs. {res['edo_3']:,.2f}"
                                ], color="info"),
                                dbc.ListGroupItem([
                                    html.Div("7% Interés:", className="fw-bold"),
                                    f"Bs. {res['edo_7']:,.2f}"
                                ], color="warning")
                            ], flush=True)
                        ], md=4)
                    ])
                ])
            ])
        
        elif active_tab == "tab-comparacion":
            return dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=resultados["graficos"]["comparacion"],
                        config={'displayModeBar': True},
                        className="mb-4"
                    )
                ])
            ])
        
        elif active_tab == "tab-evolucion":
            return dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=resultados["graficos"]["evolucion"],
                        config={'displayModeBar': True},
                        className="mb-4"
                    )
                ])
            ])
        
        elif active_tab == "tab-edos":
            return dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        figure=resultados["graficos"]["detalle"],
                        config={'displayModeBar': True},
                        className="mb-4"
                    )
                ])
            ])

    @app.callback(
        [Output("store-resultados", "data"),
         Output("generar-reporte", "disabled")],
        Input("calcular-proyecciones", "n_clicks"),
        [State("salario-mensual", "value"),
         State("meses-ahorro", "value"),
         State("tasa-crecimiento", "value"),
         State("store-file-data", "data"),
         State("expectativas-ingresos", "value"),
         State("tasa-interes", "value"),
         State("inflacion", "value"),
         State("preferencias-temporales", "value"),
         State("educacion-financiera", "value"),
         State("riesgo-desempleo", "value"),
         State("situacion-familiar", "value"),
         State("gastos-salud", "value"),
         State("estabilidad-laboral", "value")],
        prevent_initial_call=True
    )
    def calcular_resultados(n_clicks, salario, meses, tasa_crecimiento, file_data, 
                          expectativas_ingresos, tasa_interes, inflacion, preferencias_temporales,
                          educacion_financiera, riesgo_desempleo, situacion_familiar, gastos_salud, estabilidad_laboral):
        if not n_clicks:
            raise PreventUpdate
        
        try:
            from algoritmo import calcular_proyecciones
            
            variables_ahorro = {
                'expectativas_ingresos': expectativas_ingresos,
                'tasa_interes': tasa_interes,
                'inflacion': inflacion,
                'preferencias_temporales': preferencias_temporales,
                'educacion_financiera': educacion_financiera,
                'riesgo_desempleo': riesgo_desempleo,
                'situacion_familiar': situacion_familiar,
                'gastos_salud': gastos_salud,
                'estabilidad_laboral': estabilidad_laboral
            }
            
            resultados = calcular_proyecciones(n_clicks, salario, meses, tasa_crecimiento, file_data, variables_ahorro)
            
            if not resultados:
                raise ValueError("No se obtuvieron resultados válidos")
                
            return resultados, False
        
        except Exception as e:
            print(f"Error al calcular resultados: {str(e)}")
            raise PreventUpdate