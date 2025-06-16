import pandas as pd
import base64
import io
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html

def calcular_proyecciones(n_clicks, salario_mensual, meses_ahorro, tasa_crecimiento, file_data):
    if not n_clicks:
        return None, {}

    afp_tasa = 0.1271
    salario_neto_inicial = int(salario_mensual * (1 - afp_tasa))
    gasto_mensual = 0

    if file_data:
        try:
            df = pd.read_json(file_data, orient='split')
            if 'Gasto mensual estimado' in df.columns:
                gasto_mensual = int(df['Gasto mensual estimado'].sum())
        except Exception as e:
            print(f"Error procesando archivo: {e}")

    I0 = salario_mensual * (1 - afp_tasa)
    c0 = 0
    c1 = ((gasto_mensual * 100) / I0) / 100 if I0 > 0 else 0
    c2 = 0.01
    gI = (tasa_crecimiento / 100) / 12

    r_3 = 0.03 / 12
    r_7 = 0.07 / 12

    t = np.linspace(0, meses_ahorro, meses_ahorro)
    A0 = 0

    def modelo(r):
        def ode(A, t):
            salario_bruto_t = salario_mensual * np.exp(gI * t)
            I_t = salario_bruto_t * (1 - afp_tasa)
            return (1 - c1) * I_t - c0 + (c2 + r) * A
        return ode

    A_3 = odeint(modelo(r_3), A0, t)
    A_7 = odeint(modelo(r_7), A0, t)

    saldo_simple = (salario_neto_inicial - gasto_mensual) * meses_ahorro
    saldo_bajo_rendimiento = (salario_neto_inicial - gasto_mensual) * (((1 + r_3)**meses_ahorro - 1) / r_3) if r_3 > 0 else saldo_simple
    saldo_moderado = (salario_neto_inicial - gasto_mensual) * (((1 + r_7)**meses_ahorro - 1) / r_7) if r_7 > 0 else saldo_simple

    fig_comparacion = go.Figure()
    fig_comparacion.add_trace(go.Bar(
        x=["0% Simple", "3% Simple", "7% Simple"], 
        y=[saldo_simple, saldo_bajo_rendimiento, saldo_moderado], 
        name="Cálculo Simple", 
        marker_color="royalblue"
    ))
    fig_comparacion.add_trace(go.Bar(
        x=["3% EDO", "7% EDO"], 
        y=[A_3[-1][0], A_7[-1][0]], 
        name="Modelo Diferencial", 
        marker_color="firebrick"
    ))
    fig_comparacion.update_layout(
        title="Comparación de Ahorros", 
        xaxis_title="Escenario", 
        yaxis_title="Ahorro Acumulado (Bs.)", 
        barmode='group'
    )

    fig_evolucion = go.Figure()
    fig_evolucion.add_trace(go.Scatter(
        x=t, y=(salario_neto_inicial - gasto_mensual) * t, 
        mode='lines', name='0% Simple', 
        line=dict(color='green', dash='dash')
    ))
    fig_evolucion.add_trace(go.Scatter(
        x=t, y=(salario_neto_inicial - gasto_mensual) * (((1 + r_3)**t) - 1) / r_3, 
        mode='lines', name='3% Simple', 
        line=dict(color='blue', dash='dash')
    ))
    fig_evolucion.add_trace(go.Scatter(
        x=t, y=(salario_neto_inicial - gasto_mensual) * (((1 + r_7)**t) - 1) / r_7, 
        mode='lines', name='7% Simple', 
        line=dict(color='orange', dash='dash')
    ))
    fig_evolucion.add_trace(go.Scatter(
        x=t, y=A_3.flatten(), name="3% EDO", 
        line=dict(color='royalblue')
    ))
    fig_evolucion.add_trace(go.Scatter(
        x=t, y=A_7.flatten(), name="7% EDO", 
        line=dict(color='firebrick')
    ))
    fig_evolucion.update_layout(
        title="Evolución del Ahorro", 
        xaxis_title="Meses", 
        yaxis_title="Ahorro Acumulado (Bs.)"
    )

    fig_detalle = make_subplots(rows=1, cols=2, subplot_titles=("3% Interés", "7% Interés"))
    fig_detalle.add_trace(go.Scatter(x=t, y=A_3.flatten(), name="EDO 3%"), row=1, col=1)
    fig_detalle.add_trace(go.Scatter(
        x=t, y=(salario_neto_inicial - gasto_mensual) * (((1 + r_3)**t) - 1) / r_3, 
        name="Simple 3%", line=dict(dash='dot')
    ), row=1, col=1)
    fig_detalle.add_trace(go.Scatter(x=t, y=A_7.flatten(), name="EDO 7%"), row=1, col=2)
    fig_detalle.add_trace(go.Scatter(
        x=t, y=(salario_neto_inicial - gasto_mensual) * (((1 + r_7)**t) - 1) / r_7, 
        name="Simple 7%", line=dict(dash='dot')
    ), row=1, col=2)
    fig_detalle.update_layout(title="Detalle Modelos", showlegend=True)

    texto = [
        html.H6("CALCULO DE INGRESOS EN BASE AL SALARIO MENSUAL", style={'font-weight': 'bold'}),
        html.P(f"Salario mensual neto = Bs. {salario_neto_inicial:,.2f}"),
        html.P(f"Gasto total estimado = Bs. {gasto_mensual:,.2f}"),
        html.P(f"Saldo restante = Bs. {salario_neto_inicial - gasto_mensual:,.2f}"),
        html.H6(f"PERSPECTIVA DE CRECIMIENTO DE AHORRO A {meses_ahorro} MESES", style={'font-weight': 'bold'}),
        html.H6("CALCULO CON OPERACIONES", style={'font-weight': 'bold'}),
        html.P("Escenario 1: Ahorro Simple (0% interés)"),
        html.P(f"Ahorro = Bs. {round(saldo_simple):,}"),
        html.P("Escenario 2: Ahorro Simple (3% interés)"),
        html.P(f"Ahorro = Bs. {round(saldo_bajo_rendimiento):,}"),
        html.P("Escenario 3: Ahorro Simple (7% interés)"),
        html.P(f"Ahorro = Bs. {round(saldo_moderado):,}"),
        html.H5("CALCULO CON ECUACIONES DIFERENCIALES", style={'font-weight': 'bold'}),
        html.P("Escenario 1: Ahorro con modelo diferencial (3% interés)"),
        html.P(f"Ahorro = Bs. {round(A_3[-1][0]):,}"),
        html.P("Escenario 2: Ahorro con modelo diferencial (7% interés)"),
        html.P(f"Ahorro = Bs. {round(A_7[-1][0]):,}")
    ]
    
    resultados = {
        "calculos": texto,
        "comparacion": fig_comparacion, 
        "evolucion": fig_evolucion, 
        "detalle": fig_detalle
    }
    
    return texto, resultados