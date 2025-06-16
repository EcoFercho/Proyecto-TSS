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

def leer_gastos(contents):
    if contents:
        decoded = base64.b64decode(contents.split(',')[1])
        df = pd.read_excel(io.BytesIO(decoded))
        if 'Gasto mensual estimado' in df.columns:
            return int(df['Gasto mensual estimado'].sum())
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
    c1 = ((gasto * 100) / I0) / 100
    A0 = 0
    t = np.linspace(0, meses, meses)

    A_3 = odeint(construir_modelo(salario, c1, gI, R_3), A0, t)
    A_7 = odeint(construir_modelo(salario, c1, gI, R_7), A0, t)
    return t, A_3.flatten(), A_7.flatten(), I0

def calcular_proyecciones(n_clicks, salario, meses, tasa_crecimiento, contents):
    if not n_clicks:
        return "", {}

    gasto = leer_gastos(contents)
    t, A_3, A_7, I0 = resolver_EDO(salario, gasto, tasa_crecimiento, meses)
    saldo_simple = (I0 - gasto) * meses
    saldo_3 = (I0 - gasto) * (((1 + R_3)**meses - 1) / R_3)
    saldo_7 = (I0 - gasto) * (((1 + R_7)**meses - 1) / R_7)

    fig1 = go.Figure([
        go.Bar(x=["0% Simple", "3% Simple", "7% Simple"], y=[saldo_simple, saldo_3, saldo_7], name="Cálculo Simple"),
        go.Bar(x=["3% EDO", "7% EDO"], y=[A_3[-1], A_7[-1]], name="Modelo EDO")
    ])
    fig1.update_layout(title="Comparación de Ahorros", barmode='group')

    fig2 = go.Figure([
        go.Scatter(x=t, y=(I0 - gasto) * t, name="0% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=(I0 - gasto) * (((1 + R_3)**t - 1) / R_3), name="3% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=(I0 - gasto) * (((1 + R_7)**t - 1) / R_7), name="7% Simple", line=dict(dash="dash")),
        go.Scatter(x=t, y=A_3, name="3% EDO"),
        go.Scatter(x=t, y=A_7, name="7% EDO")
    ])
    fig2.update_layout(title="Evolución del Ahorro")

    fig3 = make_subplots(rows=1, cols=2, subplot_titles=("3% Interés", "7% Interés"))
    fig3.add_trace(go.Scatter(x=t, y=A_3, name="EDO 3%"), row=1, col=1)
    fig3.add_trace(go.Scatter(x=t, y=(I0 - gasto) * (((1 + R_3)**t - 1) / R_3), name="Simple 3%", line=dict(dash='dot')), row=1, col=1)
    fig3.add_trace(go.Scatter(x=t, y=A_7, name="EDO 7%"), row=1, col=2)
    fig3.add_trace(go.Scatter(x=t, y=(I0 - gasto) * (((1 + R_7)**t - 1) / R_7), name="Simple 7%", line=dict(dash='dot')), row=1, col=2)

    resumen = [
        html.H6("DATOS INGRESADOS", style={'font-weight': 'bold'}),
        html.P(f"Salario neto: Bs. {I0:,.2f}"),
        html.P(f"Gasto mensual: Bs. {gasto:,.2f}"),
        html.P(f"Saldo neto: Bs. {I0 - gasto:,.2f}"),
        html.H6("CALCULO CON FORMULA VALOR FUTURO", style={'font-weight': 'bold'}),
        html.P(f"Ecenario 1 intres 0%: Bs. {round(saldo_simple):,}"),
        html.P(f"Ecenario 2 intres 3%: Bs. {round(saldo_3):,}"),
        html.P(f"Ecenario 3 intres 7%: Bs. {round(saldo_7):,}"),
        html.H6("CALCULO CON ECUACIONES DIFERENCIALES", style={'font-weight': 'bold'}),
        html.P(f"Ecenario 1 EDO intres 3%: Bs. {round(A_3[-1]):,}"),
        html.P(f"Ecenario 2 EDO intres 7%: Bs. {round(A_7[-1]):,}")
    ]

    return resumen, {"comparacion": fig1, "evolucion": fig2, "detalle": fig3}
