
import sys
print(f"DEBUG: J'utilise ce Python : {sys.executable}")

import KeplerGL
from streamlit_keplergl import keplergl_static
import streamlit as st
import os


st.set_config(layout = "wide", page_title = "HDX Geo Explorer")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "bronze")

st.sidebar.title("Configuration")
# 
st.selected_file = st.sidebar.selectbox("Choisir une couche: ", os.listdir(DATA_DIR))


#2. Chargement des fichirs GEOJSON
@st.cache_data
def load_data(file_path):
 with open(file_path, "r", encoding = "utf-8") as f:
  return f.load(f)
 
geojson_data = load_data(os.path.join(DATA_DIR, st.selected_file))

#Rendu Kepler
st.subheader(f"Visualisation de : {st.selected_file}")

map_1 = KeplerGL(height = 700)
map_1.add_data(data = geojson_data, name = st.selected_file.replace('.', '_'))

keplergl_static(map_1)
 
  



