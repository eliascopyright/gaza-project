
import streamlit as st
import pydeck as pdk
import duckdb
import pandas as pd

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

# Simulation : Création d'une table si elle n'existe pas et injection de fausses données pour tester le rendu
# (À remplacer plus tard par tes vraies données extraites de l'ETL)
db.execute("""
    CREATE TABLE IF NOT EXISTS geo_events (
        id INTEGER,
        latitude DOUBLE,
        longitude DOUBLE,
        intensity INT,
        type VARCHAR
    )
""")

if db.execute("SELECT COUNT(*) FROM geo_events").fetchone()[0] == 0:
    # Données de test autour de Gaza pour valider que Pydeck fonctionne
    db.execute("""
        INSERT INTO geo_events VALUES 
        (1, 31.50, 34.45, 50, 'Aide Humanitaire'),
        (2, 31.42, 34.38, 80, 'Incident'),
        (3, 31.35, 34.30, 30, 'Point de passage')
    """)

# 3. ACCÈS AUX DONNÉES VIA SQL (Le réflexe Data Engineer)
@st.fragment # Permet de ne recharger que cette partie si on fait du stream
def render_map_section():
    st.subheader("Flux de données géographiques")
    
    # Extraction rapide via DuckDB vers un DataFrame Pandas (Zéro surcharge mémoire)
    df = db.execute("SELECT latitude, longitude, intensity, type FROM geo_events").df()
    
    # 4. CONFIGURATION DE PYDECK (La carte Uber-performance)
    # Définition de la vue initiale de la caméra centrée sur Gaza
    view_state = pdk.ViewState(
        latitude=31.43,
        longitude=34.38,
        zoom=10,
        pitch=45 # Effet 3D incliné
    )
    
    # Création d'une couche de points (Scatterplot)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[longitude, latitude]",
        get_color="[200, 30, 0, 160]", # RGBA
        get_radius="intensity * 10",   # Le rayon dépend de l'intensité du point
        pickable=True,
    )
    
    # Rendu de la carte dans Streamlit
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Type: {type}\nIntensité: {intensity}"}
    ))
    
    # Affichage des données brutes en dessous pour validation
    st.dataframe(df, use_container_width=True)

# Lancement du rendu
render_map_section()
 
  



