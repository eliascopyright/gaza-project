from pathlib import	Path
import  sys, subprocess
import	yaml, geopandas	as gpd, requests, zipfile, argparse
from gaza_etl.transform	import	Transform
from gaza_etl.map import Map
from hdx.api.configuration import Configuration
import hdx.api.configuration
from gaza_etl.extract_hdxapi import Extract
from gaza_etl.map import Map
from gaza_etl.download_hdxapi import Download
from utilis.utilis import Utilis

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse


   
BASE_DIR = Path(__file__).resolve().parent / "gaza_etl"
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
LOGGER = Utilis.setup_logging("gaza_project", "logs_streamlit")
Utilis.loadConfiguration()
def load_cfg() -> dict:
    """
    Ouvre le fichier de configuration YAML et retourne son contenu sous forme de dictionnaire.
    """
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
    
def serve_map():
    cfg = load_cfg() # Charger la configuration (depuis le fichier YAML)
    deck = Map.make_map_pydeck(cfg)
    deck_html = deck.to_html()
    with open("maps/gaza_kepler.html", "r") as f:
        return f.read()
    return deck_html
    # return RedirectResponse(url = "/static/gaza_layers.html")

def main():
 p = argparse.ArgumentParser(description="Humanitarian Evidence ETL")
 p.add_argument("--cmd", choices=["run-all", "download", "extract", "transform", "map", "serve"])
 p.add_argument("zone", nargs = "?", default = None, help = "Zone géographique cm la thailande")
 p.add_argument("--config", default=CONFIG_PATH, help="Chemin du fichier de config")
 
 if len(sys.argv) == 1:
     args = p.parse_args(['--cmd', 'run-all', 'thailand'])
     LOGGER.info(f'Aucun argument détecté : --cmd: run-all, zone : thailand')
 else:
     args = p.parse_args()

 cfg = load_cfg()
 
 # (facultatif) affiche où on écrit les fichiers
 LOGGER.info("Working dir:", Path.cwd().resolve())
 LOGGER.info("Config file:", Path(args.config).resolve())
 LOGGER.info("Paths:", cfg.get("paths"))
 

 if args.cmd in ("download", "run-all"):
     Download.getJSON_file(terme_recherche)
 if args.cmd in ("extract", "run-all"):
     terme_recherche = cfg['query'][args.zone]
     Extract.getApiUrls(terme_recherche)
     results = Extract.queryApis(terme_recherche)
     Extract.JSONToFile(results, filename="results.json", search = terme_recherche)  
 if args.cmd in ("transform", "run-all"):
     Transform.getCsvFromJSON()
     Transform.convert_all(cfg)
 if args.cmd in ("map", "run-all"):
     Map.make_map_pydeck(cfg)
 if args.cmd == "serve":
    script_path = Path(__file__)/ "streamlit_app.py"
    
    # Lancement du processus Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", script_path]
    subprocess.run(cmd)
    

if __name__ == "__main__":
 main()