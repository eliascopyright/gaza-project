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
FIN