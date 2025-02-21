import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import folium
from streamlit_folium import folium_static
import json
import branca.colormap as cm

# Configuración inicial de la aplicación
def setup_app():
    st.set_page_config(page_title="📡 Antioquia Conectada", layout="wide")
    st.markdown(
        """
        <h1 style='text-align: center; color: #007BFF;'>📊 Diagnóstico de la Cobertura Móvil en Antioquia</h1>
        <h4 style='text-align: center; color: #6C757D;'>Trimestre 3 de 2023</h4>
        """,
        unsafe_allow_html=True
    )

# Cargar datos
def load_data():
    uploaded_file = st.sidebar.file_uploader("⬆️ Sube tu archivo CSV", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        data.columns = [
            'AÑO', 'TRIMESTRE', 'PROVEEDOR', 'COD_DEPARTAMENTO', 'DEPARTAMENTO', 'COD_MUNICIPIO',
            'MUNICIPIO', 'CABECERA_MUNICIPAL', 'COD_CENTRO_POBLADO', 'CENTRO_POBLADO',
            'COBERTURA_2G', 'COBERTURA_3G', 'COBERTURA_HSPA+', 'COBERTURA_4G', 'COBERTURA_LTE', 'COBERTURA_5G'
        ]
        return data
    else:
        st.warning("Por favor, sube un archivo CSV para continuar.")
        st.stop()

# Conexión a DuckDB
def connect_to_duckdb(data):
    con = duckdb.connect(database=':memory:')
    con.register('data', data)
    return con

# Aplicar filtros
def apply_filters(con, año, trimestre, departamento):
    query = f"""
        SELECT * FROM data WHERE AÑO = {año} AND TRIMESTRE = {trimestre}
    """
    if departamento:
        query += " AND DEPARTAMENTO IN (" + ", ".join([f"'{d}'" for d in departamento]) + ")"
    return con.execute(query).fetchdf()

# Gráfico de cobertura
def plot_cobertura(data, x, y, title, color):
    if not data.empty:
        fig = px.bar(
            data, x=x, y=y, title=title,
            labels={y: 'Número de Centros Poblados'},
            color=y, color_continuous_scale=color
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No hay datos para {title}.")

# Página de visualización
def page_visualizaciones(con):
    st.header("📊 Visualizaciones de Cobertura")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        años = con.execute("SELECT DISTINCT AÑO FROM data ORDER BY AÑO").fetchdf()['AÑO'].tolist()
        año = st.selectbox("📅 Año:", años)
    with col2:
        trimestres = con.execute("SELECT DISTINCT TRIMESTRE FROM data WHERE AÑO = ?", [año]).fetchdf()['TRIMESTRE'].tolist()
        trimestre = st.selectbox("📆 Trimestre:", trimestres)
    with col3:
        departamentos = con.execute("SELECT DISTINCT DEPARTAMENTO FROM data WHERE AÑO = ? AND TRIMESTRE = ?", [año, trimestre]).fetchdf()['DEPARTAMENTO'].tolist()
        departamento = st.multiselect("🌎 Departamento:", departamentos)
    
    tecnologias = ['COBERTURA_2G', 'COBERTURA_3G', 'COBERTURA_HSPA+', 'COBERTURA_4G', 'COBERTURA_LTE', 'COBERTURA_5G']
    tecnologia = st.selectbox("📡 Tecnología:", tecnologias)
    
    data_filtrada = apply_filters(con, año, trimestre, departamento)
    st.dataframe(data_filtrada)
    
    if not data_filtrada.empty:
        cobertura_municipio = data_filtrada[data_filtrada[tecnologia] == 'S'].groupby('MUNICIPIO').size().reset_index(name='Conteo')
        plot_cobertura(cobertura_municipio, 'MUNICIPIO', 'Conteo', f"Cobertura {tecnologia} por Municipio", px.colors.sequential.Viridis)
    else:
        st.warning("No hay datos para los filtros seleccionados.")

# Página de mapas
def page_mapa_coropletico(con):
    st.header("🗺️ Mapa de Cobertura por Municipio")
    uploaded_file = st.file_uploader("⬆️ Sube un archivo GeoJSON", type=["geojson"])
    if uploaded_file is not None:
        geojson_data = json.load(uploaded_file)
        antioquia_geojson = {"type": "FeatureCollection", "features": [
            feature for feature in geojson_data["features"] if feature["properties"]["DEPTO"] == "ANTIOQUIA"
        ]}
        for loc in antioquia_geojson["features"]:
            loc["id"] = loc["properties"]["MPIO_CNMBR"]
        
        tecnologias = ['COBERTURA_2G', 'COBERTURA_3G', 'COBERTURA_HSPA+', 'COBERTURA_4G', 'COBERTURA_LTE', 'COBERTURA_5G']
        tecnologia = st.selectbox("📶 Tecnología:", tecnologias)
        
        query_porcentaje = f"""
            SELECT MUNICIPIO, COUNT(CASE WHEN {tecnologia} = 'S' THEN 1 END) * 100 / COUNT(*) AS porcentaje_cobertura
            FROM data WHERE DEPARTAMENTO = 'ANTIOQUIA' AND AÑO = 2023 AND TRIMESTRE = 3
            GROUP BY MUNICIPIO
        """
        porcentaje_cobertura = con.execute(query_porcentaje).fetchdf()
        
        mapa = folium.Map(location=[6.23, -75.59], zoom_start=8, tiles="CartoDB Positron")
        choropleth = folium.Choropleth(
            geo_data=antioquia_geojson,
            data=porcentaje_cobertura,
            columns=["MUNICIPIO", "porcentaje_cobertura"],
            key_on="feature.id",
            fill_color="viridis",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Cobertura (%)",
        ).add_to(mapa)
        folium_static(mapa)
    else:
        st.warning("Sube un archivo GeoJSON para ver el mapa.")

# Función principal
def main():
    setup_app()
    data = load_data()
    con = connect_to_duckdb(data)
    tab1, tab2 = st.tabs(["📊 Visualizaciones", "🗺️ Mapas"])
    with tab1:
        page_visualizaciones(con)
    with tab2:
        page_mapa_coropletico(con)

if __name__ == "__main__":
    main()
