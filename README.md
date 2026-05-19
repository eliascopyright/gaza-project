# Gaza Geo Explorer

Ce projet est une application d'ingénierie de données géospatiales conçue pour capturer, stocker, transformer et visualiser des flux de données géographiques en temps réel (fichiers GeoJSON issus d'HDX et de plateformes humanitaires) sur la région de Gaza.

Initialement freiné par la dette technique de bibliothèques obsolètes (`KeplerGL`), l'architecture a été entièrement migrée vers un écosystème moderne, hautement performant, robuste et vectorisé, s'appuyant sur l'exécution couplée de **DuckDB** et de **Pydeck**.

---

##  Architecture Technique (Medallion Pattern)

Le traitement des flux de données respecte les principes de robustesse d'un environnement de production via un découpage en couches distinctes (*Medallion Architecture*) :

1. **Couche Bronze (Raw Data) :** Ingestion brute et immuable des fichiers GeoJSON extraits en tâche de fond par le script d'ETL. Stockage direct sans altération dans le répertoire `data/bronze/`.
2. **Couche Silver (Cleaned / Conformed) :** Prise en charge par le moteur SQL de **DuckDB Spatial**. Décodage natif des géométries complexes via le driver GDAL sous-jacent, conversion et typage strict à la volée des attributs du dictionnaire `properties` en structures relationnelles.
3. **Couche Gold (Analytics / Presentation) :** Génération de snapshots mémoires projetés dynamiquement toutes les 5 secondes vers l'interface utilisateur grâce au mécanisme de scope isolé `@st.fragment` de Streamlit.

>  **Note d'architecture Senior :** Le système utilise une base de données embarquée 100% *In-Memory* (`database=':memory:'`). Les opérations intensives d'I/O et de calcul géospatial (calcul des coordonnées avec `ST_X` et `ST_Y`) s'exécutent entièrement au sein de la mémoire vive (RAM), garantissant des performances d'analyse de flux de l'ordre de la milliseconde et supprimant l'usure prématurée des disques de stockage locaux.

---

##  Stack Technologique

* **Langage & Isolation :** Python 3.11, Micromamba (Environnement contraint)
* **Compute / Database Layer :** DuckDB & Extension Spatial (Moteur colonnaire vectorisé)
* **Visualisation :** Pydeck (Moteur WebGL 3D optimisé) & Streamlit (Framework applicatif)
* **Data manipulation :** Pandas (uniquement pour l'interopérabilité avec Pydeck)

---

##  Installation et Déploiement

### 1. Prérequis & Environnement Virtuel
Pour garantir la reproductibilité parfaite du runtime et éviter tout conflit avec les installations Python globales ou Anaconda, la stack s'isole rigoureusement via un gestionnaire d'environnement Micromamba épuré :

```powershell
# Clonage du dépôt et positionnement
cd gaza-project

# Destruction et recréation propre de l'environnement isolé (Clean Slate)
micromamba create -p ".\micromamba\envs\gaza_project" python=3.11 streamlit pydeck duckdb pandas pyyaml -c conda-forge --no-rc -y

# Activation de la ressource
micromamba activate ".\micromamba\envs\gaza_project"