import requests, zipfile
from pathlib import	Path

def download_from_hdx():
	BASE_URL = "https://data.humdata.org/api/3/action/package_search"
	params = {"q": "gaza"}
	resp = requests.get(BASE_URL, params = params)
	resp.raise_for_status()
	data = resp.json()

	download_links = []
	for result in data["result"]["results"]:
		for resource in result["resources"]:
			if resource["format"] == "SHP":
				download_links.append(resource["url"])
	
	return download_links	