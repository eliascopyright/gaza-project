# 📓 Journal de Bord Technique - Projet Gaza
> Ce document retrace les choix d'architecture, les bugs rencontrés et leurs résolutions.

---

## 📅 ÉTAPE 1 : Migration de l'Infrastructure (Mai 2026)

### 🛑 Problème Initial : "Access is Denied" & Imports Fantômes
- **Symptôme :** `micromamba list` montrait les paquets (Geopandas, etc.), mais Python renvoyait `ModuleNotFoundError`.
- **Cause :** Installation dans `C:\Users\elias\...`. L'antivirus Windows bloquait les appels système de Micromamba vers Python.exe pendant l'installation, empêchant la création des liens symboliques.
- **Décision :** Déplacement complet de l'infrastructure à la racine du disque pour échapper aux restrictions des dossiers utilisateurs.

### 🛠️ Nouvelle Architecture
- **Root Prefix :** `C:\micromamba`
- **Environnements :** `C:\micromamba\envs`
- **Cache Paquets :** `C:\micromamba\pkgs`

---

## 📅 ÉTAPE 2 : Configuration du Système

### 🔍 Bug : Commande 'micromamba' non reconnue
- **Symptôme :** La commande ne fonctionnait que via `.\micromamba` dans le dossier local.
- **Résolution :** 
    1. Ajout forcé de `C:\micromamba` dans le `PATH` utilisateur via PowerShell.
    2. Suppression des anciens fichiers de configuration hérités (`.condarc` / `.mambarc` dans Users) qui causaient des erreurs de parsing YAML (`yaml-cpp`).
    3. Initialisation du shell via `micromamba shell init`.

### 🔍 Bug : ImportError DLL load failed (_ctypes)
- **Symptôme :** Python incapable de charger les modules système de base.
- **Cause :** Migration "à chaud" d'un environnement. Les liens vers le Runtime C++ (UCRT) pointaient encore vers l'ancien dossier `Users`.
- **Résolution :** Suppression de l'env `gaza_v4`, purge du cache (`clean --all`) et recréation d'un environnement neuf `gaza_project` dans la nouvelle structure.

---

## 📅 ÉTAPE 3 : Automatisation de la Traçabilité

### 🤖 Dispositif 'debug.py'
- **Objectif :** Éviter la "flemme" de documenter en automatisant le push vers GitHub.
- **Fonctionnement :** Un script Python récupère les résumés d'IA, les ajoute au `.md` avec la date, fait le commit et le push en une seule commande.

---

## ✅ État Actuel du Système
- [x] Micromamba accessible globalement.
- [x] Dossier `Users` totalement évité (Zéro problème de permissions).
- [x] Environnement Python 3.11 stable avec Geopandas fonctionnel.
- [x] Journal de bord lié au dépôt Git.

## [SESSION_2026-05-13] - DÉBOGAGE STREAMLIT & KEPLERGL
---
### 🛑 BUG : `ModuleNotFoundError: No module named 'keplergl'`
- **Symptôme :** Erreur d'import uniquement lors du lancement de l'application Streamlit.
- **Cause :** "Détournement d'interpréteur". Streamlit utilisait l'exécutable Python d'Anaconda par défaut au lieu de celui de l'environnement actif `gaza_project`.
- **Action corrective :** 
    1. Changement de la commande de lancement : passage de `streamlit run` à `python -m streamlit run`.
    2. Vérification de l'interpréteur via `sys.executable` dans le script.
- **Résultat :** Streamlit s'exécute désormais avec les bibliothèques installées dans `C:\micromamba\envs\`.
- **Statut :** RÉSOLU
---

## [SESSION_2026-05-13] - PROTECTION DE L'INTÉGRITÉ DE L'ENVIRONNEMENT
---
### 🛡️ STRATÉGIE : Évitement de PIP
- **Problème :** Risque de corruption des binaires C++ en mélangeant les gestionnaires de paquets (Mamba vs Pip).
- **Décision Technique :** Priorité absolue aux paquets `conda-forge`. Refus d'utiliser `pip install` pour les bibliothèques géospatiales complexes (KeplerGL, Geopandas).
- **Action :** Installation groupée de `keplergl` avec ses dépendances de widgets (`ipywidgets`) via le canal officiel conda-forge pour garantir la cohérence des DLL.
- **Résultat :** Environnement stable et 100% géré par libmamba.
- **Statut :** PROTECTION ACTIVÉE.
---
## [SESSION_2026-05-13] - GESTION DES RESSOURCES ET VERSIONS
---
### 🛠️ ACTION : Installation de setuptools (pkg_resources)
- **Objectif :** Permettre au script de localiser des fichiers de données internes ou de vérifier les versions des dépendances via `pkg_resources`.
- **Méthode :** Installation de `setuptools` via `conda-forge` pour éviter tout conflit avec les outils de base de l'environnement.
- **Note technique :** Surveillance des performances au démarrage de Streamlit (risque de latence lié au scan des points d'entrée par pkg_resources).
- **Alternative future :** Envisager la migration vers `importlib.metadata` pour plus de rapidité.
- **Statut :** COMPOSANT AJOUTÉ.
---
## [SESSION_2026-05-13] - RECONSOLIDATION DES CHEMINS CONFIG
---
### ⚙️ CONFIGURATION : Modification de `envs_dirs`
- **Objectif :** Rediriger la création d'environnements vers l'espace utilisateur pour contourner définitivement les erreurs de permission NTFS.
- **Action :** 
    1. `micromamba config append envs_dirs` -> Nouveau point de montage.
    2. `micromamba config append pkgs_dirs` -> Déplacement du cache de téléchargement.
- **Résultat attendu :** Fin des erreurs "Configuration introuvable" lors de l'installation de nouveaux paquets comme `pyyaml`.
- **Statut :** SYSTÈME RÉALIGNÉ.
---
FIN## [SESSION_2026-05-15] - ÉLUCIDATION DU CONFLIT DE CONFIG
---
### 🔍 ANALYSE : Origine des fichiers fantômes
- **Constat :** Micromamba agrège les fichiers de configuration (.mambarc + .condarc + config interne).
- **Cause :** Des restes d'installations précédentes (Conda/VS Code) polluaient le processus de décision du solver.
- **Action :** Transition vers une exécution en mode "Isolation" (`--no-rc`) pour garantir que seuls les chemins du dossier Users sont utilisés.
- **Résultat attendu :** Alignement strict entre l'interpréteur Python et les dossiers de modules.
---
## [SESSION_2026-05-15] - NETTOYAGE DU PRÉFIXE
---
### 🛑 BUG : "non conda folder exists at prefix"
- **Symptôme :** Refus de création d'environnement par libmamba.
- **Cause :** Présence de fichiers résiduels dans le dossier cible sans les métadonnées de structure Conda.
- **Action :** 1. Suppression forcée du dossier `gaza_project` via `Remove-Item`.
    2. Relance de la création sur un répertoire vierge.
- **Statut :** PRÉPARATION DU TERRAIN.
---
## [SESSION_2026-05-15] - FORÇAGE DE CIBLE (TARGETED INSTALL)
---
### 🛠️ STRATÉGIE : Installation par cible directe
- **Problème :** Persistance de l'absence de `pkg_resources`.
- **Hypothèse :** Conflit de PATH ou environnement mal lié (ghost environment).
- **Action :** Utilisation du flag `--target` pour bypasser la gestion de l'environnement et copier les fichiers sources directement dans le `site-packages` local.
- **Vérification :** Inspection de `sys.path` pour confirmer l'alignement des répertoires.
---
## [SESSION_2026-05-16] - CORRECTION DU REPOSITORING KEPLERGL
---
### 🛠️ PATCH : NameError 'Unicode'
- **Symptôme :** `NameError: name 'Unicode' is not defined` à la ligne 96 de `keplergl.py`.
- **Cause :** Manque d'importation explicite de la classe `Unicode` depuis le package `traitlets` dans le code source de la bibliothèque tiers.
- **Action :** Ajout manuel de `from traitlets import Unicode...` au sommet du fichier cible.
- **Statut :** PROGRESSION VALIDÉE (LE CORPS DE LA LIBRAIRIE S'EXÉCUTE DESORMAIS).
---
## [SESSION_2026-05-17] - PIVOT ARCHITECTURAL : ABANDON DE KEPLERGL
---
### 🏛️ DÉCISION DESIGN : Choix technologique orienté Production
- **Constat :** KeplerGL introduit une dette technique majeure (libs obsolètes, rupture au runtime Python 3.11+) et gère mal le rafraîchissement par flux (State Rendering inefficace).
- **Pivot DE Senior :** Migration de la couche de visualisation vers une stack standard de l'industrie : `Pydeck` pour le rendu cartographique performant, combiné à un stockage intermédiaire léger (`DuckDB`) pour bufferiser le stream de données géographiques.
- **Objectif :** Garantir la scalabilité de l'application face à l'accumulation des données du stream.
---
## [SESSION_2026-05-17] - PIVOT ARCHITECTURAL : ABANDON DE KEPLERGL
---
### 🏛️ DÉCISION DESIGN : Choix technologique orienté Production
- **Constat :** KeplerGL introduit une dette technique majeure (libs obsolètes, rupture au runtime Python 3.11+) et gère mal le rafraîchissement par flux (State Rendering inefficace).
- **Pivot DE Senior :** Migration de la couche de visualisation vers une stack standard de l'industrie : `Pydeck` pour le rendu cartographique performant, combiné à un stockage intermédiaire léger (`DuckDB`) pour bufferiser le stream de données géographiques.
- **Objectif :** Garantir la scalabilité de l'application face à l'accumulation des données du stream.
---
## [SESSION_2026-05-17] - PURGE ET REMISE À ZÉRO DE L'INFRASTRUCTURE LOCALE
---
### 🛠️ ACTION : Hard Reset de l'environnement virtuel
- **Objectif :** Éliminer la dette technique accumulée lors des tentatives d'installation de KeplerGL (fichiers tar.gz manuels, conflits Jaraco).
- **Nouvelle Stack Cible :** Python 3.11 + Streamlit + Pydeck (Visualisation performante) + DuckDB (Moteur de stockage/calcul spatial).
- **Méthode :** Isolation stricte (`--no-rc`) pour garantir la reproductibilité du pipeline.
- **Résultat :** Environnement 100% propre, prêt pour le développement de l'architecture de streaming.
---
## [SESSION_2026-05-17] - PURGE ET REMISE À ZÉRO DE L'INFRASTRUCTURE LOCALE
---
### 🛠️ ACTION : Hard Reset de l'environnement virtuel
- **Objectif :** Éliminer la dette technique accumulée lors des tentatives d'installation de KeplerGL (fichiers tar.gz manuels, conflits Jaraco).
- **Nouvelle Stack Cible :** Python 3.11 + Streamlit + Pydeck (Visualisation performante) + DuckDB (Moteur de stockage/calcul spatial).
- **Méthode :** Isolation stricte (`--no-rc`) pour garantir la reproductibilité du pipeline.
- **Résultat :** Environnement 100% propre, prêt pour le développement de l'architecture de streaming.
---
## [SESSION_2026-05-18] - PARADIGME DES BASES DE DONNÉES EMBARQUÉES (DUCKDB)
---
### 🧠 CONCEPT APPRIS : Base In-Memory vs Serveur Dédié
- **Définition :** DuckDB est une base de données relationnelle colonnaire embarquée. Elle ne nécessite pas de processus serveur (contrairement à PostgreSQL) et s'exécute dans le thread de l'application Python.
- **Mécanisme de Stockage :** 1. `:memory:` -> Stockage volatile dans la RAM, idéal pour le traitement de flux/stream à haute performance (zéro IO disque).
  2. `fichier.db` -> Stockage persistant sous forme d'un fichier unique sur le système de fichiers local.
- **Cas d'usage DE Senior :** Remplacement avantageux de Pandas (il charge tout en mémoire d'un coup (Eager) et utilise beaucoup de RAM) pour le requêtage de fichiers volumineux (GeoJSON, Parquet) grâce au requêtage colonnaire et à l'analyse spatiale vectorisée.
---
## [SESSION_2026-05-18] - CYCLE DE VIE DES EXTENSIONS DUCKDB
---
### 🛠️ RÉSOLUTION : Échec de résolution de ST_Read (Spatial Extension)
- **Symptôme :** Erreur de fonction inconnue sur `ST_Read` lors de l'exécution du fragment Streamlit.
- **Cause :** L'extension `spatial`, bien qu'installée globalement, n'était pas chargée (`LOAD`) dans le contexte d'exécution isolé du fragment Streamlit.
- **Action Senior :** Ajout systématique de la commande `db.execute("LOAD spatial;")` juste avant la requête analytique pour garantir la présence des fonctions géospatiales au runtime.
---
## [SESSION_2026-05-18] - ERREUR D'ENTRÉE/SORTIE GDAL (IO ERROR)
---
### 🛑 BUG : Échec d'ouverture du dataset GDAL par ST_Read
- **Symptôme :** `IO Error: Could not open GDAL dataset` pointant vers le répertoire `data\bronze`.
- **Cause :** La fonction `ST_Read` (via le driver GDAL) requiert un descripteur de fichier ou un pattern explicite, et non un pointeur vers un dossier/répertoire brut.
- **Résolution :** - Option 1 : Spécification du nom de fichier absolu.
  - Option 2 (DE Target) : Utilisation du wildcard `*.geojson` pour permettre à DuckDB d'exécuter un scan de type "Globbing" sur l'ensemble des partitions du dossier bronze.
---
FIN