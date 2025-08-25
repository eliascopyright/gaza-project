import requests, zipfile
from pathlib import	Path
from download	import extract_from_db

def extract_all(cfg):
	Path("data").mkdir(exist_ok=True)

	download_links = extract_from_db()

	for url in download_links:
		filename = Path('data')/Path(url).name
		print(f"Downloading {url} to {filename}")
		r = requests.get(url)
		r.raise_for_status()
		filename.write_bytes(r.content)

	raw = Path('data')
	out = Path('data_extracted')
	out.mkdir(exist_ok=True)

	for z in raw.glob("*.zip"):
		dest = out/z.stem
		dest.mkdir(exist_ok=True)
		with zipfile.ZipFile(z, 'r') as zf:
			zf.extractall(dest)
			print(f"Extracted ->", dest.resolve())
		return	out