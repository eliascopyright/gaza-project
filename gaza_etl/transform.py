from pathlib import Path
import geopandas as gpd

def convert_all(cfg):
	src = Path(cfg['src']['extracted']); bronze = Path(cfg['paths']['bronze'])
	bronze.mkdir(exist_ok=True)
	for shp in src.glob('*.shp'):
		gdf = gpd.read_file(shp)
		if gdf.crs and gdf.crs.to_epsg() != 4326:
							gdf = gdf.to_crs(4326)

		out_geojson = bronze / (shp.stem + ".geojson")
		out_parquet = bronze / (shp.stem + ".parquet")
		Path(cfg["paths"]["bronze"]).mkdir(exist_ok=True)

		gdf.to_file(out_geojson, driver="GeoJSON")
		gdf.to_parquet(out_parquet, index=False)
		
		print("🧪 converted ->", out_geojson.name, out_parquet.name)
