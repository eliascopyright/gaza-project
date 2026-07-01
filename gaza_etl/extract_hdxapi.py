import time
from pathlib import Path
import requests
from hdx.utilities.easy_logging import setup_logging
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
import json, sys

dossier_racine = Path(__file__).resolve().parent.parent
if str(dossier_racine) not in sys.path:
   sys.path.append(str(dossier_racine))
from utilis.utilis import Utilis

setup_logging()
LOGGER = Utilis.setup_logging("gaza_project", "logs_streamlit")
Utilis.loadConfiguration()

class Extract:
# API_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJVcW9vazRxNmx1SXgybVRkZURuMnhoZi1hcU1pMk9ieGFveUNpNllULWc4IiwiaWF0IjoxNzc5MjY4Njk3LCJleHAiOjE3ODE4NjA2OTd9.q7M3c4kiNf4NXy5BOb_xLtlKS0cfAlgZTSYVp4TriGA
    
 def getApiUrls(search : str):
   
   """Récupère les API URLs à partir du fichier JSON généré par getJSONFileFromSearch et les retourne sous forme de liste.
   Args:
      None
   Returns: 
      list: Liste des API URLs extraites du fichier JSON.  
   """ 
   search = search.replace(' ', '_')
   bronze_path = Path(Utilis.load_cfg()['paths']['bronze'])/search
   with open(bronze_path/"resources.json", "r") as f:
    api_urls = json.load(f)
   return api_urls
 
 def queryApis(search:str ):
  """
  Interroge les API URLs fournies, stocke les résultats dans une liste et les sauvegarde dans un fichier JSON.
  Args:
     api_urls (list): Liste des API URLs à interroger.
     
  Returns:
     string: Nom du fichier JSON contenant les résultats des API.
  """
  api_urls = Extract.getApiUrls(search)
  LOGGER.info("\n API URLs extraites du fichier JSON :")
  resultats = []
  for index, url in enumerate(api_urls, start=1):
     LOGGER.info(url)
     LOGGER.info(f"\n Il ya {len(api_urls)} API URLS à interroger...")
     LOGGER.info(f"\n Interrogation de l'API {index}/{len(api_urls)} : {url}")
     response = requests.get(url, headers={"accept": "application/json"})
     if response.status_code == 200:
        data = response.json()
        LOGGER.info(f"La requête est un succès")
     
        if data.get("success") and "result" in data:
            info_resource = data["result"]
            LOGGER.info(f"L'API de l'url {index}/{len(api_urls)} a été interrogée avec succès.\n")
            resultats.append(info_resource)
            LOGGER.info(f"Les résultats ont bien été extraits : {len(resultats)}")
            
        else:
            LOGGER.info(f"L'API de l'url {index} a été interrogée avec succès, mais la réponse contient pas le champ 'result'.\n".format(index))
     else:
      LOGGER.info(f"Erreur lors de l'interrogation de l'API de l'url {index}, code {response.status_code}.\n")
    
    
     # pour ne pas se faire bannir notre IP par le pare-feu d'HDX (Rate Limiting)
     time.sleep(0.5) 
  LOGGER.info(f"resultats: {resultats}")    
  return resultats
 
 def JSONToFile(list_to_save: list, filename, search: str):
  """
  Sauvegarde les résultats des API dans un fichier JSON.
  Args:
     filename (str): Nom du fichier JSON dans lequel sauvegarder les résultats.
  Returns:
     None
  """
  search = search.replace(" ", "_")
  bronze_path = Path(Utilis.load_cfg()["paths"]['bronze'])/search
  bronze_path.mkdir(exist_ok=True, parents = True)
  
  with open(bronze_path/filename, "w", encoding='utf-8') as f:
   json.dump(list_to_save, f, indent = 4, ensure_ascii=False)

 def downloadFiles(results_file:str, zone_geographique: str):
    with open(results_file, "r", encoding='utf-8') as f:
        data = json.load(f)
     #On va parcourir chaque élément de data[]
    bronze_path = Path(Utilis.load_cfg()["paths"]["bronze"]) / zone_geographique
    bronze_path.mkdir(exist_ok=True, parents=True)
    for line in data:
        url = line.get("download_url")
        local_url = url.split('/')[-1]
        
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(bronze_path/local_url, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                    f.write(chunk)

        LOGGER.info(f"[{zone_geographique}] Téléchargé : {bronze_path}")
if __name__ == "__main.py":
  Extract.getApiUrls()
  Extract.queryApis()
  Extract.JSONToFile()  
   