import io
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from dash import dcc, Input, Output, State
import dash_bootstrap_components as dbc
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO

def generar_grafico_comparativo(resultados):
    """Genera gráfico comparativo de resultados, solo si los valores son no negativos"""
    plt.close('all') 
    fig = None  
    try:
        montos = [
            resultados['resultados']['simple_0'],
            resultados['resultados']['simple_3'],
            resultados['resultados']['simple_7'],
            resultados['resultados']['edo_3'],
            resultados['resultados']['edo_7']
        ]
        if any(m < 0 for m in montos):
            print("No se puede generar gráfico comparativo: valores negativos detectados")
            return None
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        metodos = ['Simple 0%', 'Simple 3%', 'Simple 7%', 'EDO 3%', 'EDO 7%']
        colors = ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6']
        bars = ax.bar(metodos, montos, color=colors)
        
        ax.set_title('Comparación de Montos Finales por Método', pad=20)
        ax.set_ylabel('Monto Final (Bs)')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'Bs. {height:,.2f}',
                    ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generando gráfico comparativo: {str(e)}")
        return None
    finally:
        if fig is not None:
            plt.close(fig)

def generar_grafico_evolucion_simple(resultados):
    """Genera gráfico de evolución para fórmulas simples, solo si los valores son no negativos"""
    plt.close('all')
    fig = None 
    try:
        montos = [
            resultados['resultados']['simple_0'],
            resultados['resultados']['simple_3'],
            resultados['resultados']['simple_7'],
            resultados['resultados']['edo_3'],
            resultados['resultados']['edo_7']
        ]
        if any(m < 0 for m in montos):
            print("No se puede generar gráfico evolución simple: valores negativos detectados")
            return None
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        meses = np.arange(0, resultados['datos_entrada']['meses'] + 1)
        pmt = resultados['datos_entrada']['ahorro_mensual'] / resultados['datos_entrada']['factor_ahorro']
        
        def calcular_serie_uniforme(t, r):
            if r == 0:
                return pmt * t
            r_mensual = r / 12
            return pmt * ((1 + r_mensual)**t - 1) / r_mensual
        
        simple_0 = [calcular_serie_uniforme(t, 0.0) for t in meses]
        simple_3 = [calcular_serie_uniforme(t, 0.03) for t in meses]
        simple_7 = [calcular_serie_uniforme(t, 0.07) for t in meses]
        
        ax.plot(meses, simple_0, label='Simple 0%', linestyle='--', color='#3498db', linewidth=2)
        ax.plot(meses, simple_3, label='Simple 3%', linestyle='--', color='#2ecc71', linewidth=2)
        ax.plot(meses, simple_7, label='Simple 7%', linestyle='--', color='#f1c40f', linewidth=2)
        
        ax.set_title('Evolución Temporal - Fórmulas Simples', pad=20)
        ax.set_xlabel('Meses')
        ax.set_ylabel('Monto Acumulado (Bs)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.annotate(f'Final 0%: Bs. {resultados["resultados"]["simple_0"]:,.2f}',
                    xy=(meses[-1], simple_0[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    fontsize=9)
        ax.annotate(f'Final 3%: Bs. {resultados["resultados"]["simple_3"]:,.2f}',
                    xy=(meses[-1], simple_3[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    fontsize=9)
        ax.annotate(f'Final 7%: Bs. {resultados["resultados"]["simple_7"]:,.2f}',
                    xy=(meses[-1], simple_7[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    fontsize=9)
        
        plt.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generando gráfico evolución simple: {str(e)}")
        return None
    finally:
        if fig is not None:
            plt.close(fig)

def generar_grafico_evolucion_edos(resultados):
    """Genera gráfico de evolución para modelos EDO, solo si los valores son no negativos"""
    plt.close('all')
    fig = None  
    try:
        montos = [
            resultados['resultados']['simple_0'],
            resultados['resultados']['simple_3'],
            resultados['resultados']['simple_7'],
            resultados['resultados']['edo_3'],
            resultados['resultados']['edo_7']
        ]
        if any(m < 0 for m in montos):
            print("No se puede generar gráfico evolución EDO: valores negativos detectados")
            return None
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        meses = np.arange(0, resultados['datos_entrada']['meses'] + 1)
        pmt_0 = resultados['datos_entrada']['ahorro_mensual'] / resultados['datos_entrada']['factor_ahorro']
        g = resultados['datos_entrada']['tasa_crecimiento'] / 100
        
        def calcular_ahorro_edo(t, r):
            s = [0.0] 
            r_mensual = r / 12
            g_mensual = g / 12
            for i in range(1, len(t)):
                pmt_t = pmt_0 * (1 + g_mensual)**i
                s.append(s[-1] * (1 + r_mensual) + pmt_t)
            return s
        
        edo_3 = calcular_ahorro_edo(meses, 0.03)
        edo_7 = calcular_ahorro_edo(meses, 0.07)
        
        ax.plot(meses, edo_3, label='EDO 3%', color='#e74c3c', linewidth=2)
        ax.plot(meses, edo_7, label='EDO 7%', color='#9b59b6', linewidth=2)
        
        ax.set_title('Evolución Temporal - Modelos EDO', pad=20)
        ax.set_xlabel('Meses')
        ax.set_ylabel('Monto Acumulado (Bs)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.annotate(f'Final 3%: Bs. {resultados["resultados"]["edo_3"]:,.2f}',
                    xy=(meses[-1], edo_3[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    fontsize=9)
        ax.annotate(f'Final 7%: Bs. {resultados["resultados"]["edo_7"]:,.2f}',
                    xy=(meses[-1], edo_7[-1]),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                    fontsize=9)
        
        plt.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generando gráfico evolución EDOs: {str(e)}")
        return None
    finally:
        if fig is not None:
            plt.close(fig)

def generar_grafico_torta(resultados):
    """Genera gráfico de torta comparativo, solo si los valores son no negativos"""
    plt.close('all')
    fig = None 
    try:
        montos = [
            resultados['resultados']['simple_0'],
            resultados['resultados']['simple_3'],
            resultados['resultados']['simple_7'],
            resultados['resultados']['edo_3'],
            resultados['resultados']['edo_7']
        ]
        if any(m < 0 for m in montos):
            print("No se puede generar gráfico de torta: valores negativos detectados")
            return None
        
        fig, ax = plt.subplots(figsize=(6, 6))
        
        labels = ['Simple 0%', 'Simple 3%', 'Simple 7%', 'EDO 3%', 'EDO 7%']
        sizes = montos
        colors = ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6']
        explode = (0, 0, 0.1, 0, 0)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct=lambda p: f'Bs. {p*sum(sizes)/100:,.0f}\n({p:.1f}%)',
               shadow=True, startangle=90, textprops={'fontsize': 9})
        
        ax.set_title('Distribución Comparativa de Resultados', pad=20)
        ax.axis('equal')
        
        plt.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generando gráfico torta: {str(e)}")
        return None
    finally:
        if fig is not None:
            plt.close(fig)

def generar_grafico_ingresos_gastos(resultados):
    """Genera gráfico de barras comparativo para ingreso bruto, ingreso neto, gasto mensual y ahorro mensual"""
    plt.close('all')
    fig = None
    try:
        valores = [
            resultados['datos_entrada']['salario'],  # Ingreso bruto
            resultados['datos_entrada']['ingreso_neto'],  # Ingreso neto
            resultados['datos_entrada']['gasto'],  # Gasto mensual
            resultados['datos_entrada']['ahorro_mensual']  # Ahorro mensual inicial
        ]
        if any(v < 0 for v in valores):
            print("No se puede generar gráfico de ingresos y gastos: valores negativos detectados")
            return None

        fig, ax = plt.subplots(figsize=(8, 5))
        
        categorias = ['Ingreso Bruto', 'Ingreso Neto', 'Gasto Mensual', 'Ahorro Mensual']
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'] 
        bars = ax.bar(categorias, valores, color=colors)
        
        ax.set_title('Comparación de Ingresos, Gastos y Ahorro Mensual', pad=20)
        ax.set_ylabel('Monto (Bs)')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'Bs. {height:,.2f}',
                    ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Error generando gráfico de ingresos y gastos: {str(e)}")
        return None
    finally:
        if fig is not None:
            plt.close(fig)

def generar_reporte_completo(resultados):
    """Genera el reporte PDF con manejo seguro de recursos"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=inch/2, leftMargin=inch/2,
                               topMargin=inch/2, bottomMargin=inch/2)
        
        styles = getSampleStyleSheet()
        
        estilo_titulo = ParagraphStyle(
            'Titulo',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=12,
            textColor=colors.HexColor("#000000"),
            fontName='Helvetica-Bold'
        )
        
        estilo_subtitulo = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor("#000000"),
            fontName='Helvetica-Bold'
        )
        
        estilo_texto = ParagraphStyle(
            'Texto',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=12,
            leading=14
        )
        
        estilo_celda = ParagraphStyle(
            'Celda',
            parent=styles['BodyText'],
            fontSize=8,
            leading=10,
            spaceAfter=0,
            spaceBefore=0
        )
        
        story = []

        titulo_portada = Paragraph("<para align=center><b>REPORTE COMPLETO DE SIMULACIÓN DE AHORROS</b><br/><br/><font size=12>Análisis Financiero Detallado</font></para>", estilo_titulo)
        
        story.append(Spacer(1, 2*inch))
        story.append(titulo_portada)
        story.append(Spacer(1, 1*inch))
        
        info_portada = [
            ["Fecha generación:", datetime.now().strftime('%Y-%m-%d %H:%M')],
            ["Período analizado:", f"{resultados['datos_entrada']['meses']} meses ({resultados['datos_entrada']['meses']//12} años)"],
            ["Salario:", f"Bs. {resultados['datos_entrada']['salario']:,.2f}"],
            ["Versión del reporte:", "2.0"]
        ]
        
        tabla_portada = Table(info_portada, colWidths=[2*inch, 3*inch])
        tabla_portada.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (0,-1), 0),
            ('RIGHTPADDING', (0,0), (0,-1), 12),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(tabla_portada)
        story.append(PageBreak())
        
        story.append(Paragraph("1. RESUMEN EJECUTIVO", estilo_subtitulo))
        story.append(Spacer(1, 0.2*inch))
        
        mejor_resultado = max(resultados['resultados'].items(), key=lambda x: x[1])
        peor_resultado = min(resultados['resultados'].items(), key=lambda x: x[1])
        
        resumen_texto = f"""
        <b>Objetivo:</b> Este reporte presenta un análisis exhaustivo de la simulación de ahorros realizada bajo diferentes escenarios financieros.<br/><br/>
        
        <b>Hallazgos clave:</b><br/>
        • La mejor opción es <b>{mejor_resultado[0].replace('_', ' ').title()}</b> % con Bs. {mejor_resultado[1]:,.2f}<br/>
        • La opción menos favorable es <b>{peor_resultado[0].replace('_', ' ').title()}</b> % con Bs. {peor_resultado[1]:,.2f}<br/>
        • Diferencia entre mejor/peor opción: Bs. {mejor_resultado[1]-peor_resultado[1]:,.2f}<br/><br/>
        
        <b>Conclusiones preliminares:</b> {f'Los resultados negativos indican que tus gastos superan tus ingresos, lo que requiere una acción inmediata para reducir gastos.' if mejor_resultado[1] < 0 else 'La elección de la estrategia de ahorro puede variar significativamente el resultado final. Se recomienda considerar tanto el rendimiento esperado como el perfil de riesgo.'}
        """
        story.append(Paragraph(resumen_texto, estilo_texto))
        
        story.append(Paragraph("2. ANÁLISIS DETALLADO", estilo_subtitulo))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("<b>Detalle de Parámetros de Entrada:</b>", estilo_subtitulo))
        
        datos_entrada = [
            ["Parámetro", "Valor", "Descripción"],
            [
                "Salario bruto mensual", 
                f"Bs. {resultados['datos_entrada']['salario']:,.2f}", 
                "Salario antes de descuentos"
            ],
            [
                "Deducción AFP (12.71%)", 
                f"Bs. {resultados['datos_entrada']['salario']*0.1271:,.2f}", 
                "Aporte obligatorio a pensiones"
            ],
            [
                "Ingreso neto mensual", 
                f"Bs. {resultados['datos_entrada']['ingreso_neto']:,.2f}", 
                "Salario después de AFP"
            ],
            [
                "Gasto mensual estimado", 
                f"Bs. {resultados['datos_entrada']['gasto']:,.2f}", 
                "Gastos fijos mensuales"
            ],
            [
                "Ahorro mensual inicial", 
                f"Bs. {resultados['datos_entrada']['ahorro_mensual']:,.2f}", 
                "Ingreso neto menos gastos"
            ],
            [
                "Tasa crecimiento salarial", 
                f"{resultados['datos_entrada']['tasa_crecimiento']}% anual", 
                "Incremento salarial proyectado"
            ],
            [
                "Período de simulación", 
                f"{resultados['datos_entrada']['meses']} meses", 
                f"Equivalente a {resultados['datos_entrada']['meses']//12} años"
            ]
        ]
        
        tabla_entrada = Table(datos_entrada, colWidths=[1.8*inch, 1.5*inch, 3*inch])
        tabla_entrada.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F567")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        story.append(tabla_entrada)
        story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph("<b>Comparación Visual de Ingresos, Gastos y Ahorro:</b>", estilo_texto))
        img_ingresos_gastos = generar_grafico_ingresos_gastos(resultados)
        if img_ingresos_gastos:
            story.append(Image(img_ingresos_gastos, width=6*inch, height=3.5*inch))
        else:
            story.append(Paragraph(
                "<b>Nota:</b> No se generó el gráfico de ingresos y gastos debido a valores negativos.",
                estilo_texto
            ))
        story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph("<b>Variables que Afectan al Ahorro:</b>", estilo_subtitulo))
        try:
            vars_ahorro = resultados['datos_entrada'].get('variables_ahorro', {})
            default_vars = {
                'expectativas_ingresos': 1.0,
                'tasa_interes': 1.0,
                'inflacion': 1.0,
                'preferencias_temporales': 1.0,
                'educacion_financiera': 1.0,
                'riesgo_desempleo': 1.0,
                'situacion_familiar': 1.0,
                'gastos_salud': 1.0,
                'estabilidad_laboral': 1.0
            }
            vars_ahorro = {**default_vars, **vars_ahorro}
            
            datos_variables = [
                [
                    Paragraph("<b>Variable</b>", estilo_celda),
                    Paragraph("<b>Valor</b>", estilo_celda),
                    Paragraph("<b>Descripción</b>", estilo_celda)
                ],
                [
                    Paragraph("Expectativas de Ingresos", estilo_celda),
                    Paragraph(f"{vars_ahorro['expectativas_ingresos']:.2f}", estilo_celda),
                    Paragraph("Expectativas sobre ingresos futuros. Valores bajos (optimistas) aumentan el ahorro; altos (pesimistas) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Tasa de Interés", estilo_celda),
                    Paragraph(f"{vars_ahorro['tasa_interes']:.2f}", estilo_celda),
                    Paragraph("Tasa de interés esperada(Deudas futuras). Valores bajos fomentan el ahorro; altos incentivan el consumo.", estilo_celda)
                ],
                [
                    Paragraph("Inflación", estilo_celda),
                    Paragraph(f"{vars_ahorro['inflacion']:.2f}", estilo_celda),
                    Paragraph("Inflación esperada. Valores bajos preservan el poder adquisitivo, favoreciendo el ahorro; altos lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Preferencias Temporales", estilo_celda),
                    Paragraph(f"{vars_ahorro['preferencias_temporales']:.2f}", estilo_celda),
                    Paragraph("Gastos futuros. Orientación hacia el futuro o presente. Valores bajos (futuro) aumentan el ahorro; altos (presente) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Educación Financiera", estilo_celda),
                    Paragraph(f"{vars_ahorro['educacion_financiera']:.2f}", estilo_celda),
                    Paragraph("Nivel de conocimiento financiero. Valores bajos (alta educación) favorecen el ahorro; altos (baja) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Riesgo de Desempleo", estilo_celda),
                    Paragraph(f"{vars_ahorro['riesgo_desempleo']:.2f}", estilo_celda),
                    Paragraph("Probabilidad de desempleo. Valores bajos (bajo riesgo) aumentan el ahorro; altos (alto riesgo) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Situación Familiar", estilo_celda),
                    Paragraph(f"{vars_ahorro['situacion_familiar']:.2f}", estilo_celda),
                    Paragraph("Responsabilidades familiares. Valores bajos (menos dependientes) favorecen el ahorro; altos (más dependientes) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Gastos de Salud", estilo_celda),
                    Paragraph(f"{vars_ahorro['gastos_salud']:.2f}", estilo_celda),
                    Paragraph("Gastos médicos esperados. Valores bajos (bajos gastos) aumentan el ahorro; altos (altos gastos) lo reducen.", estilo_celda)
                ],
                [
                    Paragraph("Estabilidad Laboral", estilo_celda),
                    Paragraph(f"{vars_ahorro['estabilidad_laboral']:.2f}", estilo_celda),
                    Paragraph("Estabilidad del empleo. Valores bajos (estable) favorecen el ahorro; altos (inestable) lo reducen.", estilo_celda)
                ]
            ]
            
            tabla_variables = Table(datos_variables, colWidths=[1.5*inch, 1.0*inch, 4.5*inch])
            tabla_variables.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F567")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('WORDWRAP', (0,0), (-1,-1), 'CJK')
            ]))
            tabla_variables._argW = [1.5*inch, 1.0*inch, 4.5*inch]
            story.append(tabla_variables)
            story.append(Spacer(1, 0.3*inch))
            
            factor_ahorro = resultados['datos_entrada'].get('factor_ahorro', 1.0)
            story.append(Paragraph(
                f"""
                <b>Interpretación:</b> Estas variables ajustan el comportamiento de ahorro mediante un factor multiplicativo. 
                Un valor de 1.0 es neutral; valores < 1.0 aumentan el ahorro; valores > 1.0 lo reducen. 
                El factor de ajuste final es {factor_ahorro:.2f}.
                """,
                estilo_texto
            ))
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"Error generando tabla de variables de ahorro: {str(e)}")
            story.append(Paragraph(
                "<b>Error:</b> No se pudieron incluir las variables de ahorro debido a un problema con los datos.",
                estilo_texto
            ))
            story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph("<b>Comparación Detallada de Métodos:</b>", estilo_subtitulo))
        story.append(Spacer(1, 0.1*inch))
        
        datos_comparativos = [
            ["Método", "Tasa %", "Ahorro Final (Bs)", "Diferencia", "Rentabilidad Anualizada"],
            [
                "Fórmula Simple", "0%", 
                f"Bs. {resultados['resultados']['simple_0']:,.2f}", 
                "-", 
                "0.00%"
            ],
            [
                "Fórmula Simple", "3%", 
                f"Bs. {resultados['resultados']['simple_3']:,.2f}", 
                f"{'+' if resultados['resultados']['simple_3'] >= resultados['resultados']['simple_0'] else ''}Bs. {resultados['resultados']['simple_3']-resultados['resultados']['simple_0']:,.2f}", 
                "3.00%"
            ],
            [
                "Fórmula Simple", "7%", 
                f"Bs. {resultados['resultados']['simple_7']:,.2f}", 
                f"{'+' if resultados['resultados']['simple_7'] >= resultados['resultados']['simple_0'] else ''}Bs. {resultados['resultados']['simple_7']-resultados['resultados']['simple_0']:,.2f}", 
                "7.00%"
            ],
            [
                "Modelo EDO", "3%", 
                f"Bs. {resultados['resultados']['edo_3']:,.2f}", 
                f"{'+' if resultados['resultados']['edo_3'] >= resultados['resultados']['simple_0'] else ''}Bs. {resultados['resultados']['edo_3']-resultados['resultados']['simple_0']:,.2f}", 
                f"3.00% + crecimiento {resultados['datos_entrada']['tasa_crecimiento']}%"
            ],
            [
                "Modelo EDO", "7%", 
                f"Bs. {resultados['resultados']['edo_7']:,.2f}", 
                f"{'+' if resultados['resultados']['edo_7'] >= resultados['resultados']['simple_0'] else ''}Bs. {resultados['resultados']['edo_7']-resultados['resultados']['simple_0']:,.2f}", 
                f"7.00% + crecimiento {resultados['datos_entrada']['tasa_crecimiento']}%"
            ]
        ]
        
        tabla_comparativa = Table(datos_comparativos, colWidths=[1.8*inch, 0.8*inch, 1.5*inch, 1.5*inch, 2*inch])
        tabla_comparativa.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F567")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f5f9fc')]),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4)
        ]))
        story.append(tabla_comparativa)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("""
        <b>Interpretación:</b> Esta tabla muestra el rendimiento comparativo de los diferentes métodos de cálculo. 
        La columna "Diferencia" indica cuánto más (o menos) se obtiene respecto al método base (0% de interés). 
        La rentabilidad anualizada combina el interés con el crecimiento salarial en los modelos EDO.
        """, estilo_texto))
        
        story.append(PageBreak())
        
        story.append(Paragraph("<b>Comparación Visual de Resultados:</b>", estilo_texto))
        img_comparativo = generar_grafico_comparativo(resultados)
        if img_comparativo:
            story.append(Image(img_comparativo, width=6*inch, height=3.5*inch))
        else:
            story.append(Paragraph(
                "<b>Nota:</b> No se generó el gráfico debido a resultados negativos. Esto indica que tus gastos superan tus ingresos, generando un déficit proyectado.",
                estilo_texto
            ))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("<b>Evolución Temporal - Fórmulas Simples:</b>", estilo_texto))
        img_evol_simple = generar_grafico_evolucion_simple(resultados)
        if img_evol_simple:
            story.append(Image(img_evol_simple, width=6*inch, height=4*inch))
        else:
            story.append(Paragraph(
                "<b>Nota:</b> No se generó el gráfico debido a resultados negativos. Esto indica que tus gastos superan tus ingresos, generando un déficit proyectado.",
                estilo_texto
            ))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("""
        <b>Análisis fórmulas simples:</b> Este modelo considera aportes constantes sin crecimiento salarial, 
        con capitalización mensual de intereses. Las líneas punteadas muestran la progresión acumulada 
        bajo diferentes tasas de interés anual.
        """, estilo_texto))
        
        story.append(PageBreak())
        
        story.append(Paragraph("<b>Evolución Temporal - Modelos EDO:</b>", estilo_texto))
        img_evol_edos = generar_grafico_evolucion_edos(resultados)
        if img_evol_edos:
            story.append(Image(img_evol_edos, width=6*inch, height=4*inch))
        else:
            story.append(Paragraph(
                "<b>Nota:</b> No se generó el gráfico debido a resultados negativos. Esto indica que tus gastos superan tus ingresos, generando un déficit proyectado.",
                estilo_texto
            ))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(f"""
        <b>Análisis modelos EDO:</b> Este modelo considera crecimiento salarial del {resultados['datos_entrada']['tasa_crecimiento']}% anual, 
        con aportes variables que aumentan progresivamente. Las líneas continuas muestran la evolución 
        considerando tasas de interés compuesto más crecimiento salarial.
        """, estilo_texto))
        
        story.append(Spacer(1, 0.02*inch))

        story.append(Paragraph("<b>Distribución Comparativa de Resultados:</b>", estilo_texto))
        img_torta = generar_grafico_torta(resultados)
        if img_torta:
            story.append(Image(img_torta, width=4.5*inch, height=4.5*inch))
        else:
            story.append(Paragraph(
                "<b>Nota:</b> No se generó el gráfico debido a resultados negativos. Esto indica que tus gastos superan tus ingresos, generando un déficit proyectado.",
                estilo_texto
            ))
        story.append(PageBreak())
        
        story.append(Paragraph("Conclusión del Análisis Financiero", estilo_subtitulo))
        story.append(Spacer(1, 0.0*inch))
        
        ahorro_mensual = resultados['datos_entrada']['ahorro_mensual']
        ingreso_neto = resultados['datos_entrada']['ingreso_neto']
        gasto = resultados['datos_entrada']['gasto']
        factor_ahorro = resultados['datos_entrada']['factor_ahorro']
        vars_ahorro = resultados['datos_entrada'].get('variables_ahorro', {})
        
        vars_problematicas = {k: v for k, v in vars_ahorro.items() if v > 1.0}
        vars_mensaje = []
        if vars_problematicas.get('situacion_familiar', 1.0) > 1.0:
            vars_mensaje.append("responsabilidades familiares altas")
        if vars_problematicas.get('gastos_salud', 1.0) > 1.0:
            vars_mensaje.append("gastos médicos elevados")
        if vars_problematicas.get('preferencias_temporales', 1.0) > 1.0:
            vars_mensaje.append("tendencia a gastar en el presente")
        
        proporcion_gasto = (gasto / ingreso_neto) * 100 if ingreso_neto > 0 else 100
        
        if ahorro_mensual <= 0:
            conclusion_texto = f"""
            Tu reporte muestra que no estás ahorrando nada porque tus gastos (Bs. {gasto:,.2f}) igualan o superan tu ingreso neto (Bs. {ingreso_neto:,.2f}). 
            Esto lleva a resultados negativos en todas las simulaciones, como Bs. {resultados['resultados']['edo_7']:,.2f} en el modelo EDO al 7%. 
            Es urgente que reduzcas tus gastos. Analiza dónde puedes recortar, como en salidas, suscripciones o compras no esenciales. 
            {f'Tus {", ".join(vars_mensaje)} están empeorando la situación.' if vars_mensaje else ''} 
            Por ejemplo, si tienes muchas responsabilidades familiares, haz un presupuesto más estricto. 
            Si gastas mucho en el presente, piensa en metas futuras como un fondo de emergencia. 
            Intenta ahorrar al menos Bs. {ingreso_neto*0.05:,.2f} al mes (5% de tu ingreso) para empezar a construir un futuro financiero sólido.
            """
        elif proporcion_gasto > 80:
            conclusion_texto = f"""
            Tu reporte muestra que aunque puedes ahorrar Bs. {ahorro_mensual:,.2f} al mes, tus gastos (Bs. {gasto:,.2f}) representan el {proporcion_gasto:.1f}% de tu ingreso neto (Bs. {ingreso_neto:,.2f}), lo cual es muy alto. 
            Esto limita tu capacidad de ahorro, como se ve en los resultados (hasta Bs. {resultados['resultados']['edo_7']:,.2f} en {resultados['datos_entrada']['meses']//12} años con EDO al 7%). 
            {f'Tus {", ".join(vars_mensaje)} están afectando tu capacidad de ahorrar más.' if vars_mensaje else ''} 
            Por ejemplo, si tienes gastos médicos altos, considera un seguro de salud. 
            Revisa tus gastos y recorta en cosas no imprescindibles, como entretenimiento. 
            Intenta reducir tus gastos en un 10% (Bs. {gasto*0.1:,.2f}) para aumentar tu ahorro y destinarlo a una cuenta con intereses.
            """
        else:
            conclusion_texto = f"""
            Tu reporte muestra que estás ahorrando Bs. {ahorro_mensual:,.2f} al mes, lo que te permite proyectar hasta Bs. {resultados['resultados']['edo_7']:,.2f} en {resultados['datos_entrada']['meses']//12} años con la opción EDO al 7%. 
            Tus gastos (Bs. {gasto:,.2f}) son el {proporcion_gasto:.1f}% de tu ingreso neto (Bs. {ingreso_neto:,.2f}), lo cual está bien controlado. 
            {f'Sin embargo, tus {", ".join(vars_mensaje)} podrían permitirte ahorrar aún más si las mejoras.' if vars_mensaje else ''} 
            Por ejemplo, si gastas mucho en el presente, considera guardar más para metas grandes como comprar una casa. 
            Intenta aumentar tu ahorro en un 5% (Bs. {ahorro_mensual*0.05:,.2f}) y colócalo en una cuenta con buena rentabilidad.
            """
        
        story.append(Paragraph(conclusion_texto, estilo_texto))

        story.append(Paragraph("3. RECOMENDACIONES ESTRATÉGICAS", estilo_subtitulo))
        story.append(Spacer(1, 0.2*inch))
        
        recomendaciones = [
            ("Diversificación de inversiones", 
             "Asignar el ahorro entre diferentes instrumentos financieros según el perfil de riesgo"),
            ("Revisión periódica", 
             f"Reevaluar trimestralmente los supuestos y ajustar la estrategia según cambios en el {resultados['datos_entrada']['tasa_crecimiento']}% de crecimiento salarial"),
            ("Fondo de emergencia", 
             "Mantener un colchón equivalente a 3-6 meses de gastos antes de invertir"),
            ("Consideración fiscal", 
             "Evaluar el impacto impositivo de los diferentes instrumentos de inversión"),
            ("Ajuste por inflación", 
             "Priorizar instrumentos que superen la inflación esperada (mínimo 5% anual)"),
            ("Educación financiera", 
             "Capacitación continua sobre productos financieros y estrategias de ahorro")
        ]
        
        for titulo, desc in recomendaciones:
            story.append(Paragraph(f"<b>{titulo}:</b> {desc}", estilo_texto))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        story.append(Paragraph("4. ANEXOS TÉCNICOS", estilo_subtitulo))
        story.append(Spacer(1, 0.2*inch))
        
        anexos = [
            ("Metodología", 
             "Los cálculos consideran: Crecimiento salarial progresivo, tasas de interés compuesto mensual, y aportes constantes ajustados por inflación."),
            ("Supuestos clave", 
             f"Tasa de crecimiento salarial constante ({resultados['datos_entrada']['tasa_crecimiento']}% anual), estabilidad económica, y gastos constantes en términos reales."),
            ("Limitaciones", 
             "El modelo no considera: Cambios abruptos en políticas económicas, fluctuaciones cambiarias, o eventos imprevistos que afecten los ingresos/gastos."),
            ("Glosario", 
             "EDO: Ecuación Diferencial Ordinaria. AFP: Administradora de Fondos de Pensiones. ROI: Retorno sobre la inversión.")
        ]
        
        for titulo, contenido in anexos:
            story.append(Paragraph(f"<b>{titulo}:</b>", estilo_subtitulo))
            story.append(Paragraph(contenido, estilo_texto))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("<i>Documento generado automáticamente - Sistema de Simulación Financiera v2.0</i>", 
                             ParagraphStyle(name='Pie', parent=styles['BodyText'], fontSize=8, textColor=colors.grey)))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generando reporte completo: {str(e)}")
        raise
    finally:
        plt.close('all')

def register_callbacks(app):
    @app.callback(
        [Output("descargar-reporte", "data"),
         Output("reporte-error", "children")],
        Input("generar-reporte", "n_clicks"),
        State("store-resultados", "data"),
        prevent_initial_call=True
    )
    def descargar_reporte(n_clicks, resultados):
        if not n_clicks or not resultados:
            return None, dbc.Alert("No hay datos para generar el reporte. Calcule las proyecciones primero.", color="warning")
            
        try:
            plt.close('all')
            print("Iniciando generación de reporte...")  
            pdf_buffer = generar_reporte_completo(resultados)
            print("Reporte generado exitosamente.") 
            
            montos = [
                resultados['resultados']['simple_0'],
                resultados['resultados']['simple_3'],
                resultados['resultados']['simple_7'],
                resultados['resultados']['edo_3'],
                resultados['resultados']['edo_7']
            ]
            if any(m < 0 for m in montos):
                print("Nota: Gráficos no generados debido a resultados negativos")
            
            return dcc.send_bytes(
                pdf_buffer.getvalue(),
                filename=f"Reporte_Ahorros_Detallado_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            ), None
        except Exception as e:
            error_msg = f"Error al generar el reporte: {str(e)}"
            print(error_msg)
            return None, dbc.Alert(error_msg, color="danger")
        finally:
            plt.close('all')