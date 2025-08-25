from pathlib import Path
import folium, json

def make_map(cfg):
    bronze = Path(cfg["paths"]["bronze"]); outdir = Path(cfg["paths"]["maps"])
    
    outdir.mkdir(parents=True, exist_ok=True)
    m = folium.Map(location=[31.5, 34.47], zoom_start=11)
    for gj in bronze.glob("*.geojson"):
        try:
            folium.GeoJson(
                json.loads(
                    gj.read_text(encoding="utf-8")),
																	name=gj.stem).add_to(m)
        except Exception as e:
            print("skip", gj, e)
    folium.LayerControl().add_to(m)
    out = outdir / "gaza_layers.html"
    m.save(out)
    print("🗺  map ->", out.resolve())
