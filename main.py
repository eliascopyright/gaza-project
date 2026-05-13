from pathlib import	Path
import os, sys, subprocess

import	yaml, geopandas	as gpd, requests, zipfile, argparse
from app.app import serve_map
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from gaza_etl.extract import	extract_all
from gaza_etl.transform	import	convert_all
from gaza_etl.download	import	extract_from_db
from gaza_etl.map	import	make_map
from gaza_etl.map_kepler import	make_map_kepler
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse



app = FastAPI()
app.mount("/static", StaticFiles(directory="maps"), name="static")

@app.get("/map", response_class=HTMLResponse)
def serve_map():
    cfg = load_cfg()
    deck = make_map_kepler(cfg)
    deck_html = deck.to_html()
    with open("maps/gaza_kepler.html", "r") as f:
        return f.read()
    return deck_html
    # return RedirectResponse(url = "/static/gaza_layers.html")
  
   
BASE_DIR = Path(__file__).resolve().parent / "gaza_etl"
CONFIG_PATH = BASE_DIR / "config.yaml"

def load_cfg():
 with open(CONFIG_PATH, "r") as f:
  return yaml.safe_load(f)
 
def main():
 p = argparse.ArgumentParser(description="Gaza Evidence ETL")
 p.add_argument("cmd", choices=["run-all", "download", "extract", "transform", "map", "serve"])
 p.add_argument("--config", default=CONFIG_PATH, help="Chemin du fichier de config")
 args = p.parse_args()

 cfg = load_cfg()
 
 # (facultatif) affiche où on écrit les fichiers
 print("Working dir:", Path.cwd().resolve())
 print("Config file:", Path(args.config).resolve())
 print("Paths:", cfg.get("paths"))

 if args.cmd in ("download", "run-all"):
     extract_from_db()
 if args.cmd in ("extract", "run-all"):
     extract_all(cfg)
 if args.cmd in ("transform", "run-all"):
     convert_all(cfg)
 if args.cmd in ("map", "run-all"):
     make_map_kepler(cfg)
 if args.cmd == "serve":
    script_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")
    
    # Lancement du processus Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", script_path]
    subprocess.run(cmd)
    

if __name__ == "__main__":
 main()