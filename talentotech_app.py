import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# 1. Configuración inicial de la aplicación
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="📈",
    layout="wide"
)
st.title("📈 Dashboard Interactivo con Streamlit")
st.sidebar.title("⚙️ Opciones de navegación")

# 2. Cargar datos o Generación de Datos Aleatorios
uploaded_file = st.sidebar.file_uploader("⬆️ Sube tu archivo CSV", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    # Cargar un conjunto de datos predeterminado
    np.random.seed(42)
    data = pd.DataFrame({
        "Fecha": pd.date_range(start="2024-01-01", periods=100, freq="D"),
        "Ventas": np.random.randint(100, 500, size=100),
        "Categoría": np.random.choice(["A", "B", "C", "D"], size=100),
        "Descuento": np.random.uniform(5, 30, size=100),
        "Satisfacción": np.random.randint(1, 10, size=100),
        "Región": np.random.choice(["Norte", "Sur", "Este", "Oeste"], size=100)
    })

# 3. Implementación de la Barra de Navegación
menu = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio", "📋 Datos", "🔎 Visualización", "🧰 Configuración"]
)

# 4. Mostrar los Datos
if menu == "📋 Datos":
    st.subheader("📂 Vista previa de los datos")
    st.dataframe(data)

# 5. Filtrar por Categoría
filtered_data = data  # Asegurar que filtered_data esté definido en todo el script
if menu == "🔎 Visualización":
    st.subheader("📊 Visualización de Datos")
    categoria = st.sidebar.selectbox("Selecciona una categoría", data["Categoría"].unique())
    filtered_data = data[data["Categoría"] == categoria]
    st.write(f"Mostrando datos para la categoría {categoria}")
    st.dataframe(filtered_data)

    # 6. Filtrar por Ventas
    ventas_min, ventas_max = st.sidebar.slider(
        "Selecciona el rango de ventas:",
        min_value=int(data["Ventas"].min()),
        max_value=int(data["Ventas"].max()),
        value=(int(data["Ventas"].min()), int(data["Ventas"].max()))
    )
    filtered_data = filtered_data[(filtered_data["Ventas"] >= ventas_min) & (filtered_data["Ventas"] <= ventas_max)]

    # 7. Filtrar por Fecha
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        [data["Fecha"].min(), data["Fecha"].max()],
        min_value=data["Fecha"].min(),
        max_value=data["Fecha"].max()
    )
    filtered_data = filtered_data[(filtered_data["Fecha"] >= pd.to_datetime(fecha_inicio)) & (filtered_data["Fecha"] <= pd.to_datetime(fecha_fin))]

    # 8. Botón para Reiniciar Filtros
    if st.sidebar.button("Reiniciar Filtros"):
        filtered_data = data
        st.experimental_rerun()

    # 9. Implementar Pestañas
    st.subheader("📌 Navegación entre Pestañas")
    tab1, tab2 = st.tabs(["📊 Gráficos", "📂 Datos"])
    with tab1:
        st.subheader("Visualización de Datos")
        fig_plotly = px.scatter(
            filtered_data,
            x="Ventas",
            y="Descuento",
            color="Región",
            title="Relación entre Ventas y Descuento por Región",
        )
        st.plotly_chart(fig_plotly)
    with tab2:
        st.subheader("Datos Crudos")
        st.dataframe(filtered_data)

# 10. Mensaje de Confirmación
st.sidebar.success("🎉 Configuración completa")

