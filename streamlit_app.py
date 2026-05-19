import pydeck as pdk
import duckdb
import pandas as pd
import streamlit as st
import os

st.set_page_config(layout = "wide", page_title = "HDX Geo Explorer")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "bronze")

st.sidebar.title("Configuration")
# 
st.selected_file = st.sidebar.selectbox("Choisir une couche: ", os.listdir(DATA_DIR))



# 1. CONFIGURATION DE LA PAGE (API Moderne)
st.set_page_config(layout="wide", page_title="HDX Gaza Geo Explorer")

st.title("📍 Gaza Geo Explorer - Real-Time Data Pipeline")
st.write("Analyse géographique performante propulsée par DuckDB et Pydeck.")

# 2. INITIALISATION DE DUCKDB (Gestionnaire de données Senior)
@st.cache_resource
def get_db_connection():
    # On crée une connexion persistante à DuckDB en mémoire ou vers un fichier .db
    return duckdb.connect(database=':memory:')

db = get_db_connection()

GEOJSON_PATH = r"C:\Users\elias\datapython\gaza-project\data\bronze\\*.geojson"

# 2. Fragment interactif (streamnig layer)
# run_every=5 pour rafraîchir toutes les 5 secondes

@st.fragment(run_every=5)
def render_live_map():
    
    st.subheader("Flux de données en temps réel")
    
    if not os.path.exists(GEOJSON_PATH):
        st.error(f"En attnte du fichier GeoJSON dans {GEOJSON_PATH}")
        return
    
    try:
        db.execute("LOAD spatial;")
        query = f"""
        SELECT
              CAST(properties ->> 'type' AS VARCHAR) AS type,
              ST_X(geom) AS longitude,
              ST_Y(geom) AS latitude,
            FROM ST_READ('{GEOJSON_PATH}')
        """
        
        df = db.execute(query).df()
    
        st.metric(label = "Nombre de points ingérés", value = len(df))
        
        view_state = pdk.ViewState(
            latitude = df['latitude'].mean() if not df.empty else 31.43,
            longitude = df["longitude"].mean() if not df.empty else 34.38,
            zoom  = 10,
            pitch=30
        )
    except Exception as e:
        st.error(f'Erreur de lecture : {e}')


render_live_map()

st.write("---") # Séparateur visuel
st.caption("Note de l'architecture : Le reste de la page statique, juste la carte DuckDB s'exécute en boucle")