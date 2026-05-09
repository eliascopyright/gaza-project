# app.py (FastAPI)
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from gaza_etl.map import make_map
import yaml

app = FastAPI()

@app.get("/map", response_class=HTMLResponse)
def serve_map():
    cfg = yaml.safe_load(open("gaza_etl/config.yaml"))
    deck = make_map(cfg)
    return deck.to_html()