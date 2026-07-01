import json, sys
from hdx.utilities.easy_logging import setup_logging
from pathlib import Path
from hdx.data.dataset import Dataset

# API_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJVcW9vazRxNmx1SXgybVRkZURuMnhoZi1hcU1pMk9ieGFveUNpNllULWc4IiwiaWF0IjoxNzc5MjY4Njk3LCJleHAiOjE3ODE4NjA2OTd9.q7M3c4kiNf4NXy5BOb_xLtlKS0cfAlgZTSYVp4TriGA

setup_logging()
dossier_racine = Path(__file__).resolve().parent.parent
if str(dossier_racine) not in sys.path:
   sys.path.append(str(dossier_racine))
from utilis.utilis import Utilis
Utilis.loadConfiguration()
   
LOGGER = Utilis.setup_logging("gaza_project", "logs_streamlit")

class Download:

 def getJSON_file(search: str):		# ========== TEST : SEARCH IN DATASET BANK ==========
   LOGGER.info(f"\n Recherche des datasets {search}......")
   search = search.replace(' ', '_')
   datasets_thai = Dataset.search_in_hdx(search, rows=10)
   resources_thai = Dataset.get_all_resources(datasets_thai)
   resources_thai_dict = [resource.get_api_url() for resource	in resources_thai]
   bronze_path = Path(Utilis.load_cfg()['paths']['bronze'])/search
   bronze_path.mkdir(exist_ok=True, parents=True)
   json_file_name = f"resources.json" 
 
   with open(bronze_path/json_file_name, "w") as f:
    json.dump(resources_thai_dict, f, indent=4, ensure_ascii=False)
    
   LOGGER.info("✅ Ressources de thailande sauvegardées dans resources_thai.json")

   return json_file_name

