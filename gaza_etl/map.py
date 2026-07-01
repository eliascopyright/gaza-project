from pathlib import Path
import pydeck as pdk, sys
import geopandas as gpd, json
dossier_racine = Path(__file__).resolve().parent.parent
if str(dossier_racine) not in sys.path:
   sys.path.append(str(dossier_racine))
from utilis.utilis import Utilis
Utilis.loadConfiguration()
   
LOGGER = Utilis.setup_logging("gaza_project", "logs_streamlit")

class Map:
   
 def make_map_pydeck(cfg):
    """
    Crée une carte interactive avec Pydeck à partir des fichiers GeoJSON dans le dossier bronze depuis la configuration
    YAML en entrée.
    Args:
          cfg (dict): Dictionnaire de configuration contenant les chemins d'accès.
    Returns:
          pdk.Deck: Objet Pydeck représentant la carte interactive.
          
    """
    bronze = Path(cfg['paths']["bronze"]); outdir = Path(cfg['paths']['maps'])
    
    layers = []
    for gj in bronze.glob("*.geojson"):
       gdf = gpd.read_file(gj)
       LOGGER.info(f"Processing {gj} with geometry type {gdf.geometry.geom_type.iloc[0]}")
       
       
       
       if gdf.geometry.geom_type.iloc[0] == "Point":
          layer = pdk.Layer(
          "ScatterplotLayer",
          data = json.loads(gdf.to_json()),
          get_position = "[geometry.coordinates[0], geometry.coordinates[1]]",
          get_radius = 100,
          get_fill_color=[30, 144, 255, 180],
          pickable=True
          )
          LOGGER.info(f"Created ScatterplotLayer for {gj}")
       
       else:
          layer = pdk.Layer(
          "GeoJsonLayer",
          data = json.loads(gdf.to_json()),
          get_fill_color=[30, 144, 255, 50],
          get_line_color=[30, 144, 255, 200],
          pickable=True
          )
 
       layers.append(layer)
          
       view = pdk.ViewState(latitude=31.5, longitude=34.47, zoom=11)
       LOGGER.info(f"Created view state for {gj}")
       deck = pdk.Deck(
          layers=layers,
          initial_view_state=view,
          tooltip={"text": "{name}"},
          map_provider="mapbox",
          )
       LOGGER.info(f"Nombre de layers : {len(layers)}")
       LOGGER.info(deck)
      #  for l in layers:
      #      LOGGER.info(l.data)
    LOGGER.info(deck)
    return deck
 
 def save(deck, outdir, name):
  outdir.mkdir(exist_ok=True)
  deck.to_html(outdir / f"{name}.html")
  
if __name__ == "__main__":
   cfg = Utilis.load_cfg()
   Map.make_map_pydeck(cfg)