import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sqlalchemy import create_engine

# --- 1. CONFIGURACIÓN DE PÁGINA ---
# Configuración inicial de la pestaña del navegador
st.set_page_config(
    page_title="Software Rápido BI",
    page_icon="⚡",
    layout="wide"
)

# --- 2. ESTILOS CSS PERSONALIZADOS (Look Corporativo) ---
# Se definen los colores institucionales: Pantone 306C (#00B5E2) y Pantone 302C (#194056)
st.markdown("""
<style>
    /* Ocultar elementos por defecto de Streamlit (Menu hamburguesa, footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo del Título Principal en el encabezado */
    .main-title {
        font-size: 3rem;
        color: #194056; /* Pantone 302 C - Azul Oscuro */
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #00B5E2; /* Pantone 306 C - Cyan */
        font-weight: 600;
        margin-top: -10px;
    }

    /* Personalización de las Tarjetas de Métricas (KPIs) */
    div[data-testid="metric-container"] {
        background-color: #194056; /* Fondo Oscuro */
        border-left: 5px solid #00B5E2; /* Borde lateral Cyan */
        padding: 15px;
        border-radius: 8px;
        color: white !important; /* Texto blanco */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Forzar color blanco en las etiquetas de las métricas */
    div[data-testid="metric-container"] label {
        color: #E0E0E0 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Personalización de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: white;
        border: 1px solid #E1E6EA;
        border-radius: 5px;
        color: #194056;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00B5E2 !important; /* Fondo Cyan al seleccionar */
        color: white !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN A BASE DE DATOS (SQLITE) ---
# Conecta al archivo local 'proyecto_bi.db' (No requiere usuario/contraseña)
def init_connection():
    return create_engine('sqlite:///proyecto_bi.db')

try:
    conn = init_connection()
except Exception as e:
    st.error(f"Error de conexión a base de datos: {e}")
    st.stop()

# --- 4. FUNCIONES DE LÓGICA DE NEGOCIO ---
def get_data(view_name):
    """Trae los datos de una vista SQL y los devuelve como DataFrame."""
    return pd.read_sql(f"SELECT * FROM {view_name}", conn)

def predecir_defectos(esfuerzo, madurez):
    """Modelo matemático de Rayleigh simplificado."""
    # Factor de defectos según madurez (Nivel 4 = menos defectos)
    factor = {4: 0.005, 3: 0.01}.get(madurez, 0.02)
    return int(esfuerzo * factor)

# --- 5. ENCABEZADO Y NAVEGACIÓN SUPERIOR ---
# Diseño de 2 columnas: Izquierda (Logo/Texto) - Derecha (Menú de Navegación)
col_header, col_nav = st.columns([1, 2])

with col_header:
    st.markdown('<div class="main-title">Software Rápido</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Inteligencia de Negocios</div>', unsafe_allow_html=True)

with col_nav:
    # Espacio para alinear verticalmente el menú
    st.write("") 
    st.write("") 
    # Menú horizontal usando Radio Button estilizado
    modo = st.radio(
        "Navegación:", 
        ["📊 Dashboard Directivo", "🔮 Simulador Predictivo"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("---") # Línea divisoria

# --- 6. CONTENIDO DEL MÓDULO: DASHBOARD ---
if "Dashboard" in modo:
    
    # Pestañas internas
    tab1, tab2 = st.tabs(["🚀 Misión: Calidad y Operaciones", "👁️ Visión: Estrategia (BSC)"])

    with tab1:
        st.subheader("Indicadores Clave de Desempeño (KPIs)")
        
        try:
            # Carga de datos desde las vistas SQL
            df_cal = get_data("Vista_Calidad_Defectos")
            df_fin = get_data("Vista_Desempeño_Proyectos")
            
            # Fila de Tarjetas de Métricas
            c1, c2, c3, c4 = st.columns(4)
            
            total_defectos = df_cal['Total_Defectos'].sum()
            mttr_promedio = df_cal['Promedio_Horas_Resolucion_MTTR'].mean()
            costo_total = df_fin['Costo_Real_Actual'].sum()
            proyectos_activos = len(df_fin[df_fin['estado_actual'] == 'Activo'])

            c1.metric("Defectos Totales", f"{total_defectos}")
            c2.metric("MTTR Promedio", f"{mttr_promedio:.1f} h")
            c3.metric("Costo Real", f"${costo_total:,.0f}")
            c4.metric("Proyectos Activos", f"{proyectos_activos}")
            
            st.markdown("<br>", unsafe_allow_html=True)

            # Fila de Gráficos
            col_L, col_R = st.columns([2, 1])
            
            with col_L:
                st.markdown("##### 📉 Análisis de Defectos (Por Severidad)")
                # Gráfico de Pastel (Pie Chart) solicitado
                fig = px.pie(df_cal, names='severidad', values='Total_Defectos',
                             # Paleta personalizada: Azul Oscuro, Cyan, Grises
                             color='severidad',
                             color_discrete_map={
                                 'Crítico': '#194056', 
                                 'Mayor': '#00B5E2', 
                                 'Menor': '#7D8E95', 
                                 'Leve': '#C0CACE'
                             },
                             # Fallback sequence si los nombres no coinciden exactamente
                             color_discrete_sequence=['#194056', '#00B5E2', '#7D8E95', '#C0CACE'],
                             title="",
                             hole=0.4) # Donut style para modernidad
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_R:
                st.markdown("##### 💰 Salud Financiera (Costo por Proyecto)")
                # Histograma (que funciona como gráfico de barras de frecuencia o valores)
                # x=Proyecto, y=Costo Real
                fig2 = px.histogram(df_fin, x='nombre_proyecto', y='Costo_Real_Actual',
                              color='Estatus_Financiero',
                              color_discrete_map={'En Presupuesto': '#00B5E2', 'Sobre Costo': '#FF2E63'},
                              title="")
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                                   font_color="#194056", showlegend=True, 
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                fig2.update_yaxes(showgrid=True, gridcolor='#E1E6EA')
                st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"Error cargando datos. Asegúrate de ejecutar 'migrar_a_sqlite.py' primero. Detalle: {e}")

    with tab2:
        st.subheader("Balanced Scorecard (BSC)")
        try:
            df_bsc = get_data("Vista_Balanced_Scorecard")
            
            # Visualización del BSC con tarjetas blancas limpias
            c_bsc1, c_bsc2 = st.columns(2)
            for i, row in df_bsc.iterrows():
                col = c_bsc1 if i % 2 == 0 else c_bsc2
                with col:
                    # HTML personalizado para tarjeta de BSC
                    st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E1E6EA; margin-bottom: 10px;">
                        <h4 style="color: #194056; margin:0;">{row['Perspectiva']}</h4>
                        <p style="color: #666; font-size: 0.9em;">Objetivo: {row['KPI']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    # Barra de progreso (usa el color primario definido en config.toml)
                    st.progress(int(row['Valor_Actual'])/100)
                    st.caption(f"Cumplimiento: {row['Valor_Actual']}%")
        except:
             st.warning("Datos del BSC no disponibles.")

# --- 7. MÓDULO: SIMULADOR PREDICTIVO ---
elif "Simulador" in modo:
    st.markdown("## 🔮 Modelo Predictivo Rayleigh")
    st.info("Herramienta de estimación de riesgos de calidad para nuevos proyectos de software.")
    
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        # Panel de Inputs
        with st.container():
            st.markdown("### 📝 Parámetros")
            nombre = st.text_input("Nombre del Proyecto", "Nuevo Sistema 2025")
            e = st.number_input("Esfuerzo Estimado (Horas)", 100, 10000, 1500)
            m = st.selectbox("Nivel de Madurez (CMMI)", [2, 3, 4], index=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Botón de acción principal
            if st.button("CALCULAR RIESGO", type="primary", use_container_width=True):
                st.session_state['res'] = predecir_defectos(e, m)
                st.session_state['e'] = e
                st.session_state['n'] = nombre
    
    with col_out:
        # Panel de Resultados
        if 'res' in st.session_state:
            # Tarjeta grande de resultado destacado (Fondo Cyan)
            st.markdown(f"""
            <div style="text-align: center; padding: 30px; background-color: #00B5E2; border-radius: 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin:0; font-weight:400;">Defectos Estimados</h2>
                <h1 style="font-size: 70px; margin:0; font-weight:800;">{st.session_state['res']}</h1>
                <p style="opacity: 0.9;">Proyecto: {st.session_state['n']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de Curva de Rayleigh
            # Generación de puntos para la curva
            x = np.linspace(0, st.session_state['e'] * 1.2, 100)
            sigma = st.session_state['e'] / 4
            y = (x / sigma**2) * np.exp(-x**2 / (2 * sigma**2))
            
            fig_r = px.area(x=x, y=y, title=f"Curva de Probabilidad de Fallos (Rayleigh)",
                            labels={'x': 'Tiempo / Esfuerzo', 'y': 'Probabilidad'})
            
            # Estilo de la gráfica: Azul Oscuro con relleno
            # CORRECCIÓN: 'fillcolor' (sin guion bajo) en lugar de 'fill_color'
            fig_r.update_traces(line_color='#194056', fillcolor='rgba(25, 64, 86, 0.3)')
            fig_r.update_layout(paper_bgcolor="white", plot_bgcolor="rgba(0,0,0,0)")
            
            st.plotly_chart(fig_r, use_container_width=True)