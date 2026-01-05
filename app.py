import streamlit as st
import pandas as pd

# 1. Configuración visual
st.set_page_config(page_title="Nómina Santa Rosa", layout="wide", page_icon="🎓")

# Estilos CSS para quitar márgenes extra y parecerse más a una web
st.markdown("""
<style>
    div.block-container {padding-top: 2rem;}
    div[data-testid="stMetricValue"] {font-size: 1.2rem;}
</style>
""", unsafe_allow_html=True)

# 2. Carga de datos (Backend)
@st.cache_data
def cargar_datos():
    file_path = 'SANTA ROSA ASIMILADOS 2025A.csv'
    # Intentamos leer, si falla devolvemos None
    try:
        df = pd.read_csv(file_path, header=7, encoding='latin-1')
    except:
        return None
        
    # Limpieza
    cols_docente = ['ID DEL DOCENTE', 'APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRE (S)', 'CATEGORÍA', 'INFORMACIÓN ACADÉMICA DEL DOCENTE']
    df[cols_docente] = df[cols_docente].ffill()
    df = df.dropna(subset=['UNIDAD DE APRENDIZAJE CURRICULAR/ASIGNATURA'])
    df['DOCENTE'] = df['NOMBRE (S)'] + ' ' + df['APELLIDO PATERNO'] + ' ' + df['APELLIDO MATERNO']
    df['HRS. POR UAC/ASIG'] = pd.to_numeric(df['HRS. POR UAC/ASIG'], errors='coerce').fillna(0)
    return df

df = cargar_datos()

if df is None:
    st.error("⚠️ Sube el archivo 'SANTA ROSA ASIMILADOS 2025A.csv' a tu repositorio de GitHub para ver los datos.")
    st.stop()

# 3. Interfaz Principal

# Encabezado
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.markdown("## 🏫")
with col_titulo:
    st.title("Plantel Santa Rosa 2025A")
    st.caption("Gestión Dinámica de Carga Académica")

# Buscador
busqueda = st.text_input("🔍 Buscar Docente, ID o Materia...", placeholder="Escribe aquí...")

# Lógica de Filtro
df_filtrado = df.copy()
if busqueda:
    term = busqueda.upper()
    df_filtrado = df_filtrado[
        df_filtrado['DOCENTE'].str.contains(term, case=False) |
        df_filtrado['UNIDAD DE APRENDIZAJE CURRICULAR/ASIGNATURA'].str.contains(term, case=False)
    ]

# Agrupar por docente
docentes_unicos = df_filtrado.groupby('ID DEL DOCENTE').first().reset_index()

# KPIs Rápidos
st.divider()
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Docentes", len(docentes_unicos))
kpi2.metric("Materias Asignadas", len(df_filtrado))
kpi3.metric("Total Horas", int(df_filtrado['HRS. POR UAC/ASIG'].sum()))
st.divider()

# --- AQUÍ ESTÁ LA MAGIA: VISTA DE TARJETAS ---
st.subheader("Directorio Docente")

# Creamos una cuadrícula de 3 columnas
cols = st.columns(3)

# Iteramos sobre los docentes únicos
for index, row in docentes_unicos.iterrows():
    # Calculamos en qué columna cae esta tarjeta (0, 1 o 2)
    columna_actual = cols[index % 3]
    
    with columna_actual:
        # st.container(border=True) crea el efecto de "Tarjeta" con borde
        with st.container(border=True):
            # Encabezado de la tarjeta
            st.markdown(f"**{row['DOCENTE']}**")
            st.caption(f"ID: {row['ID DEL DOCENTE']} | {row['CATEGORÍA']}")
            
            # Calculamos sus horas totales y materias
            sus_materias = df[df['ID DEL DOCENTE'] == row['ID DEL DOCENTE']]
            total_hrs = sus_materias['HRS. POR UAC/ASIG'].sum()
            
            # Semáforo simple con colores de Streamlit
            color = "green" if total_hrs < 20 else ("orange" if total_hrs < 35 else "red")
            st.markdown(f":{color}[**{total_hrs} hrs asignadas**]")
            
            # Expander para ver detalles (simula el click de la web anterior)
            with st.expander("Ver Materias"):
                for _, materia in sus_materias.iterrows():
                    st.text(f"• {materia['UNIDAD DE APRENDIZAJE CURRICULAR/ASIGNATURA']} ({materia['HRS. POR UAC/ASIG']}h)")

if len(docentes_unicos) == 0:
    st.warning("No se encontraron resultados.")
