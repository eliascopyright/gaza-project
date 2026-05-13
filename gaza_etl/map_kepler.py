from pathlib import Path
import pydeck as pdk
import geopandas as gpd, json



def make_map_kepler(cfg):
 bronze = Path(cfg['paths']["bronze"]); outdir = Path(cfg['paths']['maps'])
 
 layers = []
 for gj in bronze.glob("*.geojson"):
  gdf = gpd.read_file(gj)
  print(f"Processing {gj} with geometry type {gdf.geometry.geom_type.iloc[0]}")
  
 
  
  if gdf.geometry.geom_type.iloc[0] == "Point":
   layer = pdk.Layer(
    "ScatterplotLayer",
    data = json.loads(gdf.to_json()),
    get_position = "[geometry.coordinates[0], geometry.coordinates[1]]",
    get_radius = 100,
    get_fill_color=[30, 144, 255, 180],
    pickable=True
   )
   print(f"Created ScatterplotLayer for {gj}")
  
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
 print(f"Created view state for {gj}")
 deck = pdk.Deck(
    layers=layers,
    initial_view_state=view,
    tooltip={"text": "{name}"},
    map_provider="mapbox",
     )
#  print(f"Nombre de layers : {len(layers)}")
#  for l in layers:
#     print(l.data)
 print(deck)
 return deck
def save(deck, outdir, name):
 outdir.mkdir(exist_ok=True)
 deck.to_html(outdir / f"{name}.html")