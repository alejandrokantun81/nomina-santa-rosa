import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Nómina Santa Rosa",
    page_icon="📚",
    layout="wide"
)

# 2. Función de Carga y Limpieza (Backend)
@st.cache_data
def cargar_datos():
    # Cargar CSV
    file_path = 'SANTA ROSA ASIMILADOS 2025A.csv'
    df = pd.read_csv(file_path, header=7, encoding='latin-1')
    
    # Rellenar datos del docente hacia abajo
    cols_docente = [
        'ID DEL DOCENTE', 'APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRE (S)',
        'CATEGORÍA', 'CURP', 'INFORMACIÓN ACADÉMICA DEL DOCENTE'
    ]
    df[cols_docente] = df[cols_docente].ffill()
    
    # Filtrar filas vacías de materia
    df = df.dropna(subset=['UNIDAD DE APRENDIZAJE CURRICULAR/ASIGNATURA'])
    
    # Crear nombre completo
    df['DOCENTE'] = df['NOMBRE (S)'] + ' ' + df['APELLIDO PATERNO'] + ' ' + df['APELLIDO MATERNO']
    
    # Asegurar que las horas sean números
    df['HRS. POR UAC/ASIG'] = pd.to_numeric(df['HRS. POR UAC/ASIG'], errors='coerce').fillna(0)
    
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("⚠️ No se encuentra el archivo CSV 'SANTA ROSA ASIMILADOS 2025A.csv'. Asegúrate de subirlo a GitHub.")
    st.stop()

# 3. Interfaz de Usuario (Frontend)

# Barra lateral de filtros
st.sidebar.header("🔍 Filtros")
filtro_nombre = st.sidebar.text_input("Buscar Docente o ID")
filtro_turno = st.sidebar.multiselect("Turno", df['TURNO'].unique())

# Filtrado de datos
df_filtered = df.copy()

if filtro_nombre:
    df_filtered = df_filtered[
        df_filtered['DOCENTE'].str.contains(filtro_nombre, case=False) | 
        df_filtered['ID DEL DOCENTE'].astype(str).str.contains(filtro_nombre, case=False)
    ]

if filtro_turno:
    df_filtered = df_filtered[df_filtered['TURNO'].isin(filtro_turno)]

# Calcular resumen por docente
resumen = df_filtered.groupby(['ID DEL DOCENTE', 'DOCENTE', 'CATEGORÍA', 'INFORMACIÓN ACADÉMICA DEL DOCENTE'])['HRS. POR UAC/ASIG'].sum().reset_index()
resumen.rename(columns={'HRS. POR UAC/ASIG': 'TOTAL HORAS'}, inplace=True)

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Docentes Encontrados", len(resumen))
col2.metric("Horas Totales", int(resumen['TOTAL HORAS'].sum()))
col3.metric("Promedio Horas", f"{resumen['TOTAL HORAS'].mean():.1f}")

st.divider()

# TABLA PRINCIPAL (Con barra de progreso visual)
st.subheader("📋 Carga Académica")

# Configuración de columnas para que se vea bonito
st.dataframe(
    resumen,
    column_config={
        "DOCENTE": st.column_config.TextColumn("Docente", width="medium"),
        "CATEGORÍA": st.column_config.TextColumn("Categoría", width="small"),
        "TOTAL HORAS": st.column_config.ProgressColumn(
            "Carga Horaria (Max 40)",
            format="%d hrs",
            min_value=0,
            max_value=40,
        ),
    },
    use_container_width=True,
    hide_index=True
)

# Detalle (Expander)
with st.expander("Ver Detalle de Asignaturas por Docente"):
    st.dataframe(df_filtered[['DOCENTE', 'UNIDAD DE APRENDIZAJE CURRICULAR/ASIGNATURA', 'TURNO', 'HRS. POR UAC/ASIG']], use_container_width=True)