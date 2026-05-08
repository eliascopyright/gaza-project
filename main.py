from pathlib import	Path
import os, sys

import	yaml, geopandas	as gpd, requests, zipfile, argparse
from gaza_etl.extract import	extract_all
from gaza_etl.transform	import	convert_all
from gaza_etl.download	import	extract_from_db
from gaza_etl.map	import	make_map



BASE_DIR = Path(__file__).resolve().parent / "gaza_etl"
CONFIG_PATH = BASE_DIR / "config.yaml"

def load_cfg():
	with open(CONFIG_PATH, "r") as f:
		return yaml.safe_load(f)
	
def main():
	p = argparse.ArgumentParser(description="Gaza Evidence ETL")
	p.add_argument("cmd", choices=["run-all", "download", "extract", "transform", "map"])
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
					make_map(cfg)

if __name__ == "__main__":
	main()