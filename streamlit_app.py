from pathlib import Path
import pydeck as pdk
import duckdb
from utilis.utilis import Utilis
import pandas as pd
import streamlit as st

st.set_page_config(layout = "wide", page_title = "HDX Geo Explorer")

cfg = Utilis.load_cfg()

DATA_DIR = Path(cfg['paths']['bronze2'])

LOGGER = Utilis.setup_logging('streamlit_gaza', "logs_streamlit.log")
GEOJSON_PATH = [f.stem for f in list(DATA_DIR.glob("*.json"))]
e = list(DATA_DIR.glob("*.json"))
LOGGER.info(f"Voila Data_dir : {e}")

st.sidebar.title("Configuration")
# 
st.selected_file = st.sidebar.selectbox("Choisir une couche: ",(DATA_DIR))



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

GEOJSON_PATH = Path(cfg['paths']['bronze2'])

# 2. Fragment interactif (streamnig layer)
# run_every=5 pour rafraîchir toutes les 5 secondes
@st.fragment(run_every=5)
def render_live_map():
    
    st.subheader("Flux de données en temps réel")
    
    if not GEOJSON_PATH == []:
        st.error(f"En attnte du fichier GeoJSON dans {GEOJSON_PATH}")
        return
    
    try:
        db.execute("LOAD spatial;")
        query = f"""
        SELECT
              Shape_Area,
              ST_X(ST_Centroid(geom)) AS longitude,
              ST_Y(ST_Centroid(geom)) AS latitude,
            FROM ST_READ('{GEOJSON_PATH}')
        """
        
        df = db.execute(query).df()
    
        st.metric(label = "Nombre de points ingérés", value = len(df))
        # Configuration de la carte Pydeck
        view_state = pdk.ViewState(
            latitude=df['latitude'].mean() if not df.empty else 31.43,
            longitude=df['longitude'].mean() if not df.empty else 34.38,
            zoom=10,
            pitch=30
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_color="[230, 50, 50, 180]",
            get_radius=150,
            pickable=True,
        )
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Type: {type}"}
        ))
    except Exception as e:
        st.error(f'Erreur de lecture : {e}')


render_live_map()

st.write("---") # Séparateur visuel
st.caption("Note de l'architecture : Le reste de la page statique, juste la carte DuckDB s'exécute en boucle")