import base64
import io
import numpy as np
import pandas as pd
from scipy.integrate import odeint
from dash import html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

AFP_TASA = 0.1271
C2 = 0.01
R_3 = 0.03 / 12
R_7 = 0.07 / 12

def leer_gastos(file_data):
    if file_data:
        try:
            df = pd.read_json(file_data, orient='split')
            if 'Gasto mensual estimado' in df.columns:
                gasto_mensual = int(df['Gasto mensual estimado'].sum())
                return gasto_mensual
            else:
                print("Columna 'Gasto mensual estimado' no encontrada")
                return 0
        except Exception as e:
            print(f"Error procesando archivo: {e}")
            return 0
    else:
        return 0

def construir_modelo(salario, c1, gI, r):
    def modelo(A, t):
        salario_bruto_t = salario * np.exp(gI * t)
        I_t = salario_bruto_t * (1 - AFP_TASA)
        return (1 - c1) * I_t + (C2 + r) * A
    return modelo

def resolver_EDO(salario, gasto, tasa_crecimiento, meses):
    gI = (tasa_crecimiento / 100) / 12
    c0 = 0
    I0 = salario * (1 - AFP_TASA)
    
    if gasto is None:
        gasto = 0
    
    if gasto >= I0:
        print(f"Advertencia: Gastos ({gasto}) >= Ingresos netos ({I0})")
        gasto = I0 * 0.8
    
    c1 = gasto / I0
    A0 = 0
    t = np.linspace(0, meses, meses)

    A_3 = odeint(construir_modelo(salario, c1, gI, R_3), A0, t)
    A_7 = odeint(construir_modelo(salario, c1, gI, R_7), A0, t)
    return t, A_3.flatten(), A_7.flatten(), I0

def calcular_proyecciones(n_clicks, salario, meses, tasa_crecimiento, file_data):
    if not n_clicks:
        return "", {}

    if not salario or salario <= 0:
        return "Error: Salario debe ser mayor a 0", {}
    
    if not meses or meses <= 0:
        return "Error: Meses debe ser mayor a 0", {}
    
    if tasa_crecimiento is None:
        tasa_crecimiento = 0

    gasto = leer_gastos(file_data)
    t, A_3, A_7, I0 = resolver_EDO(salario, gasto, tasa_crecimiento, meses)
    
    ahorro_mensual = I0 - gasto
    if ahorro_mensual <= 0:
        return "Error: No hay ahorro disponible (gastos >= ingresos)", {}
    
    saldo_simple = ahorro_mensual * meses
    saldo_3 = ahorro_mensual * (((1 + R_3)**meses - 1) / R_3)
    saldo_7 = ahorro_mensual * (((1 + R_7)**meses - 1) / R_7)

    fig1 = go.Figure([
        go.Bar(x=["0% Simple", "3% Simple", "7% Simple"], 
               y=[saldo_simple, saldo_3, saldo_7], 
               name="Cálculo Simple"),
        go.Bar(x=["3% EDO", "7% EDO"], 
               y=[A_3[-1], A_7[-1]], 
               name="Modelo EDO")
    ])
    fig1.update_layout(title="Comparación de Ahorros", barmode='group')

    fig2 = go.Figure([
        go.Scatter(x=t, y=ahorro_mensual * t, 
                  name="0% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=ahorro_mensual * (((1 + R_3)**t - 1) / R_3), 
                  name="3% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=ahorro_mensual * (((1 + R_7)**t - 1) / R_7), 
                  name="7% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=A_3, name="3% EDO"),
        go.Scatter(x=t, y=A_7, name="7% EDO")
    ])
    fig2.update_layout(title="Evolución del Ahorro")

    fig3 = make_subplots(rows=1, cols=2, subplot_titles=("3% Interés", "7% Interés"))
    fig3.add_trace(go.Scatter(x=t, y=A_3, name="EDO 3%"), row=1, col=1)
    fig3.add_trace(go.Scatter(x=t, y=ahorro_mensual * (((1 + R_3)**t - 1) / R_3), 
                             name="Simple 3%", line=dict(dash='dot')), row=1, col=1)
    fig3.add_trace(go.Scatter(x=t, y=A_7, name="EDO 7%"), row=1, col=2)
    fig3.add_trace(go.Scatter(x=t, y=ahorro_mensual * (((1 + R_7)**t - 1) / R_7), 
                             name="Simple 7%", line=dict(dash='dot')), row=1, col=2)

    resumen = [
        html.H6("DATOS INGRESADOS", style={'font-weight': 'bold'}),
        html.P(f"Salario bruto: Bs. {salario:,.2f}"),
        html.P(f"Salario neto: Bs. {I0:,.2f}"),
        html.P(f"Gasto mensual: Bs. {gasto:,.2f}"),
        html.P(f"Saldo neto (ahorro): Bs. {ahorro_mensual:,.2f}"),
        html.Hr(),
        html.H6("CÁLCULO CON FÓRMULA VALOR FUTURO", style={'font-weight': 'bold'}),
        html.P(f"Escenario 1 interés 0%: Bs. {round(saldo_simple):,}"),
        html.P(f"Escenario 2 interés 3%: Bs. {round(saldo_3):,}"),
        html.P(f"Escenario 3 interés 7%: Bs. {round(saldo_7):,}"),
        html.Hr(),
        html.H6("CÁLCULO CON ECUACIONES DIFERENCIALES", style={'font-weight': 'bold'}),
        html.P(f"Escenario 1 EDO interés 3%: Bs. {round(A_3[-1]):,}"),
        html.P(f"Escenario 2 EDO interés 7%: Bs. {round(A_7[-1]):,}")
    ]

    resultados = {
        "calculos": resumen,
        "comparacion": fig1, 
        "evolucion": fig2, 
        "detalle": fig3
    }
    
    return resumen, resultados