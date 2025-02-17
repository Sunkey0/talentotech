import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# 1. configuración inicial de la aplicación 
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
if menu == "Datos":
    st.subheader("📂 Vista previa de los datos")
    st.dataframe(data)
