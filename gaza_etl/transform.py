import pandas as pd
from pathlib import Path
import geopandas as gpd
import duckdb, sys, json, requests, pytest

dossier_racine = Path(__file__).resolve().parent.parent
if str(dossier_racine) not in sys.path:
   sys.path.append(str(dossier_racine))
from utilis.utilis import Utilis
LOGGER  = Utilis.setup_logging("gaza_project", "logs_streamlit")
class Transform:
  def getCsvFromJSON(filename: str):
      """
      Prend les resultats d'un élements {} d'un fichier json et lui applique le dictionnaire
      
      Entrée:
       - results: objet {} d'un fichier json

      Sorties:
       - new_rows: objet {} avec les datas de ton json.
      """
      
      with open(filename, 'r', encoding='utf-8') as f:
          data = json.load(f)
      
      new_rows = []
      
      for el in data:
        row = {
            "id": el.get("id"),
            "name": el.get("name"),
            "alt_url": el.get("alt_url"),
            "created": el.get("created"),
            "last_modified": el.get("last_modified"),
            "description": el.get("description"),
            "download_url": el.get("download_url"),
            "format": el.get("format"),
            "hash": el.get("hash"),
            "hdx_rel_url": el.get("hdx_rel_url")}
        new_rows.append(row)
        url_downloader = row['download_url']
        format = row['format']
        nom = row["name"]
        if url_downloader and format.lower() == "csv":
            nom = nom.replace(' ', '_')
            silver_path = dossier_racine/Path(cfg['paths']['silver'])
            nom_parquet = silver_path/Path(nom).with_suffix(".parquet")
            
            try:
                # Plus besoin d'URL en dur, on injecte les variables Python directement
                duckdb.sql(f"""
                COPY (
                    SELECT * FROM read_csv(
                        '{url_downloader}',
                        header=True, 
                        auto_detect=True,
                        ignore_errors=True
                        )
                    ) 
                    TO '{silver_path/nom_parquet}' (FORMAT PARQUET, COMPRESSION 'SNAPPY');
                    """)
            except Exception as e:
                    LOGGER.error(f"Erreur de téléchargement DuckDB pour {nom}: {e}")
            
      with open(silver_path/"test.json", "w", encoding='utf-8') as f:
          json.dump(new_rows, f, ensure_ascii=True)
      
      return new_rows
  
  
  def convert_all(cfg):
     """
     Lit les Shapefiles décompressés de la couche Bronze avec DuckDB Spatial,
     et les convertit proprement en fichiers Parquet dans la couche Silver.
     """
     # 1. Extraction des chemins depuis la configuration YAML
     # On prend la donnée brute extraite (Bronze) pour créer la donnée propre (Silver)
     dossier_source = Path(cfg['paths']['extracted']) 
     dossier_silver = Path(cfg['paths']['silver']) # Assure-toi d'avoir une clé 'silver' dans ton config.yaml
     
     dossier_silver.mkdir(parents=True, exist_ok=True)
     
     LOGGER.info(f"Instanciation du moteur DuckDB pour le scan de : {dossier_source}")
     
     # 2. Initialisation d'une connexion DuckDB en mémoire
     con = duckdb.connect(database=':memory:')
     
     # 3. Chargement obligatoire de l'extension spatiale de DuckDB
     con.execute("INSTALL spatial; LOAD spatial;")
    
     fichiers_shp = list(dossier_source.rglob('*.shp'))
     
     if not fichiers_shp:
         LOGGER.info("⚠️ Aucun fichier Shapefile (.shp) trouvé dans le dossier source.")
         return

     for shp_path in fichiers_shp:
         # On définit le nom du fichier Parquet cible dans la couche Silver (ex: gaza_roads.parquet)
         nom_parquet = shp_path.stem + ".parquet"
         chemin_parquet_cible = dossier_silver / nom_parquet
         
         LOGGER.INFO(f"DuckDB Spatial transforme -> {shp_path.name} en {nom_parquet}")
         
         try:
             # La requête SQL magique de DuckDB Spatial :
             # - ST_Read lit le Shapefile directement sur le disque (via le driver GDAL intégré à DuckDB)
             # - COPY ... TO ... FORMAT PARQUET écrit le résultat à la vitesse de l'éclair
             requete_sql = f"""
                 COPY (
                     SELECT * FROM ST_Read('{str(shp_path.resolve())}')
                 ) TO '{str(chemin_parquet_cible.resolve())}' (FORMAT 'PARQUET');
             """
             
             con.execute(requete_sql)
             LOGGER.INFO(f"Fichier Silver généré avec succès : {chemin_parquet_cible.name}")
             
         except Exception as e:
             LOGGER.INFO(f"Erreur DuckDB lors de la conversion de {shp_path.name} : {e}")
             
     con.close()

if __name__ == "__main__":
    cfg = Utilis.load_cfg()
    file = Path(cfg['paths']['bronze'])/"thailand_subnational_boundaries"
    Transform.getCsvFromJSON(file/"results.json")
    # Transform.convert_all(cfg)
    