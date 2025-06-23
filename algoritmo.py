import numpy as np
import pandas as pd
from scipy.integrate import odeint
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constantes
AFP_TASA = 0.1271
C2 = 0.01
R_3 = 0.03 / 12
R_7 = 0.07 / 12

def leer_gastos(file_data):
    if not file_data:
        return 0
    
    try:
        df = pd.read_json(file_data, orient='split')
        if 'Gasto mensual estimado' in df.columns:
            gasto = float(df['Gasto mensual estimado'].sum())
            return gasto if gasto >= 0 else 0
        return 0
    except Exception as e:
        print(f"Error procesando archivo: {str(e)}")
        return 0

def calcular_factor_ahorro(variables):
    """Calcula un factor de ajuste basado en las variables que afectan al ahorro"""
    factor = 1.0
    factor *= variables.get('expectativas_ingresos', 1.0) ** 0.15
    factor *= variables.get('tasa_interes', 1.0) ** 0.1
    factor *= variables.get('inflacion', 1.0) ** 0.2
    factor *= variables.get('preferencias_temporales', 1.0) ** 0.15
    factor *= variables.get('educacion_financiera', 1.0) ** 0.1
    factor *= variables.get('riesgo_desempleo', 1.0) ** 0.1
    factor *= variables.get('situacion_familiar', 1.0) ** 0.1
    factor *= variables.get('gastos_salud', 1.0) ** 0.05
    factor *= variables.get('estabilidad_laboral', 1.0) ** 0.05
    return factor

def construir_modelo(ahorro_mensual, gI, r, factor_ahorro):
    def modelo(A, t):
        ahorro_t = ahorro_mensual * np.exp(gI * t) * (1 / factor_ahorro)
        return ahorro_t + (C2 + r) * A
    return modelo

def resolver_EDO(salario, gasto, tasa_crecimiento, meses, variables_ahorro):
    gI = (tasa_crecimiento / 100) / 12
    I0 = salario * (1 - AFP_TASA)
    
    ahorro_mensual = I0 - gasto
    t = np.linspace(0, meses, meses)
    A0 = 0
    factor_ahorro = calcular_factor_ahorro(variables_ahorro)
    
    A_3 = odeint(construir_modelo(ahorro_mensual, gI, R_3, factor_ahorro), A0, t).flatten()
    A_7 = odeint(construir_modelo(ahorro_mensual, gI, R_7, factor_ahorro), A0, t).flatten()
    
    return t, A_3, A_7, I0, factor_ahorro, ahorro_mensual, gasto

def calcular_proyecciones(n_clicks, salario, meses, tasa_crecimiento, file_data, variables_ahorro):
    if not n_clicks or not salario or not meses:
        return None
    
    try:
        salario = float(salario)
        meses = int(meses)
        tasa_crecimiento = float(tasa_crecimiento) if tasa_crecimiento else 0.0
        
        vars_ahorro = {
            'expectativas_ingresos': variables_ahorro.get('expectativas_ingresos', 1.0),
            'tasa_interes': variables_ahorro.get('tasa_interes', 1.0),
            'inflacion': variables_ahorro.get('inflacion', 1.0),
            'preferencias_temporales': variables_ahorro.get('preferencias_temporales', 1.0),
            'educacion_financiera': variables_ahorro.get('educacion_financiera', 1.0),
            'riesgo_desempleo': variables_ahorro.get('riesgo_desempleo', 1.0),
            'situacion_familiar': variables_ahorro.get('situacion_familiar', 1.0),
            'gastos_salud': variables_ahorro.get('gastos_salud', 1.0),
            'estabilidad_laboral': variables_ahorro.get('estabilidad_laboral', 1.0)
        }
        
        gasto = leer_gastos(file_data)
        t, A_3, A_7, I0, factor_ahorro, ahorro_mensual, gasto = resolver_EDO(salario, gasto, tasa_crecimiento, meses, vars_ahorro)
        
        if ahorro_mensual < 0:
            A_3[-1] = -1
            A_7[-1] = -1
        
        saldo_simple = ahorro_mensual * meses
        saldo_3 = ahorro_mensual * (((1 + R_3)**meses - 1) / R_3)
        saldo_7 = ahorro_mensual * (((1 + R_7)**meses - 1) / R_7)

        fig1 = go.Figure([
            go.Bar(
                x=["0% Simple", "3% Simple", "7% Simple"], 
                y=[saldo_simple, saldo_3, saldo_7],
                name="Fórmula Simple",
                marker_color=["#1100AD", "#1100AD", "#1100AD"]
            ),
            go.Bar(
                x=["3% EDO", "7% EDO"], 
                y=[A_3[-1], A_7[-1]],
                name="Modelo EDO",
                marker_color=["#BB0A37", "#BB0A37"]
            )
        ])
        fig1.update_layout(
            title="Comparación de Métodos de Cálculo",
            barmode='group',
            template="plotly_white"
        )

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=t, y=ahorro_mensual * t,
            name="0% Simple",
            line=dict(dash="dot", color="#636EFA")
        ))
        fig2.add_trace(go.Scatter(
            x=t, y=ahorro_mensual * (((1 + R_3)**t - 1) / R_3),
            name="3% Simple",
            line=dict(dash="dot", color="#EF553B")
        ))
        fig2.add_trace(go.Scatter(
            x=t, y=ahorro_mensual * (((1 + R_7)**t - 1) / R_7),
            name="7% Simple",
            line=dict(dash="dot", color="#00CC96")
        ))
        fig2.add_trace(go.Scatter(
            x=t, y=A_3,
            name="3% EDO",
            line=dict(color="#AB63FA")
        ))
        fig2.add_trace(go.Scatter(
            x=t, y=A_7,
            name="7% EDO",
            line=dict(color="#FFA15A")
        ))
        fig2.update_layout(
            title="Evolución Temporal del Ahorro",
            xaxis_title="Meses",
            yaxis_title="Monto Acumulado (Bs)",
            template="plotly_white"
        )

        fig3 = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Modelo con 3% de interés", "Modelo con 7% de interés")
        )
        fig3.add_trace(go.Scatter(
            x=t, y=A_3,
            name="EDO 3%",
            line=dict(color="#AB63FA")
        ), row=1, col=1)
        fig3.add_trace(go.Scatter(
            x=t, y=ahorro_mensual * (((1 + R_3)**t - 1) / R_3),
            name="Simple 3%",
            line=dict(dash='dot', color="#EF553B")
        ), row=1, col=1)
        fig3.add_trace(go.Scatter(
            x=t, y=A_7,
            name="EDO 7%",
            line=dict(color="#FFA15A")
        ), row=1, col=2)
        fig3.add_trace(go.Scatter(
            x=t, y=ahorro_mensual * (((1 + R_7)**t - 1) / R_7),
            name="Simple 7%",
            line=dict(dash='dot', color="#00CC96")
        ), row=1, col=2)
        fig3.update_layout(
            title_text="Comparación Detallada: Modelo EDO vs Fórmula Simple",
            template="plotly_white",
            showlegend=False
        )
        fig3.update_xaxes(title_text="Meses")
        fig3.update_yaxes(title_text="Monto Acumulado (Bs)")

        return {
            "datos_entrada": {
                "salario": salario,
                "meses": meses,
                "tasa_crecimiento": tasa_crecimiento,
                "gasto": gasto,
                "ahorro_mensual": ahorro_mensual,
                "ingreso_neto": I0,
                "factor_ahorro": factor_ahorro,
                "variables_ahorro": vars_ahorro
            },
            "resultados": {
                "simple_0": saldo_simple,
                "simple_3": saldo_3,
                "simple_7": saldo_7,
                "edo_3": A_3[-1],
                "edo_7": A_7[-1]
            },
            "graficos": {
                "comparacion": fig1,
                "evolucion": fig2,
                "detalle": fig3
            }
        }
    except Exception as e:
        print(f"Error calculando proyecciones: {str(e)}")
        return None