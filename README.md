git clone <votre-repo> OpenFoodFacts
cd OpenFoodFacts
```
python3 -m venv venv
source venv/bin/activate
```
pip install -r requirements.txt
```
df = pd.DataFrame(records)
df.drop_duplicates(subset=['code'], inplace=True)
df.dropna(subset=['product_name'], inplace=True)
df['energy_kcal'] = df['energy_100g'] * 0.239006
# 📰 NewsScraper — Pipeline ETL (TechCrunch / The Verge / Ars Technica)

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org)
[![Requests](https://img.shields.io/badge/requests-2.32.5-orange.svg)](https://pypi.org/project/requests)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.14.3-purple.svg)](https://www.crummy.com/software/BeautifulSoup/)
[![Supabase](https://img.shields.io/badge/Supabase-Postgres-5ed3a2.svg)](https://supabase.com)

> Pipeline ETL léger pour extraire les dernières actualités depuis trois sites (TechCrunch, The Verge, Ars Technica), nettoyer et charger les articles dans une base Postgres (compatible Supabase).

---

## 🧭 Mini table des matières
- [Aperçu](#aper%C3%A7u)
- [Fonctionnalités](#fonctionnalit%C3%A9s)
- [Installation rapide](#installation-rapide)
- [Usage](#usage)
- [Architecture & fichiers clés](#architecture--fichiers-cl%C3%A9s)
- [Détails ETL (Extract / Transform / Load)](#d%C3%A9tails-etl-extract--transform--load)
- [Configuration (Supabase / .env)](#configuration-supabase--env)
- [Schéma de la base de données (Postgres)](#sch%C3%A9ma-de-la-base-de-donn%C3%A9es-postgres)
- [Journalisation & Debug](#journalisation--debug)
- [Dépannage](#d%C3%A9pannage)
- [Contribution](#contribution)

---

## Aperçu

Ce dépôt contient un petit orchestrateur ETL : `main.py` exécute les étapes d'extraction (scraping), transformation (pandas) et chargement (SQLAlchemy vers Postgres). Les sources sont implémentées dans `sources/` et l'ETL dans `etl/`.

Les trois sites ciblés :
- TechCrunch — `sources/extract_tech.py`
- The Verge — `sources/extract_thev.py`
- Ars Technica — `sources/extract_ar.py`

---

## Fonctionnalités

- 🔎 Extraction HTML via `requests` + `BeautifulSoup` (multi-page)
- 🧹 Nettoyage et normalisation avec `pandas` (déduplication, parsing date, id unique)
- 💾 Chargement vers Postgres (SQLAlchemy). Conçu pour fonctionner avec Supabase.
- 🧾 Logs vers console et fichier via `config/logger.py`.
- ✅ Upsert (ON CONFLICT) pour sources/auteurs/articles.

---

## Installation rapide

```bash
git clone <votre-repo> newsscraper
cd newsscraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créez un fichier `.env` (non commité) contenant au minimum :

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
# ou l'URL fournie par Supabase (ne la partagez jamais publiquement)
```

Ajoutez `.env` à `.gitignore` si ce n'est pas déjà fait.

---

## Usage

- Exécuter le pipeline complet :

```bash
python main.py
```

- Exécuter une étape séparée :

```bash
python -m etl.Extract
python -m etl.Transform
python -m etl.Load
```

Fichiers importants : [main.py](main.py), [etl/Extract.py](etl/Extract.py), [etl/Transform.py](etl/Transform.py), [etl/Load.py](etl/Load.py), [config/logger.py](config/logger.py).

---

## Architecture & fichiers clés

- `main.py` — orchestrateur qui appelle `extract_data()`, puis `etl.Transform.load_data()` et `transform_data()`, puis `etl.Load.load_to_db()`.
- `etl/Extract.py` — combine les résultats des modules `sources/*` et écrit `data/raw/extracted_data.json`.
- `etl/Transform.py` — charge `data/raw/extracted_data.json`, parse les dates, déduit un `id` SHA256 sur `source|lien`, supprime les duplicatas et écrit `data/clean/clean.csv`.
- `etl/Load.py` — lit le DataFrame et effectue des upserts (`sources`, `authors`, `articles`) via SQLAlchemy et requêtes SQL textuelles (Postgres `ON CONFLICT`).
- `sources/` — trois scrapers : `extract_tech.py`, `extract_thev.py`, `extract_ar.py`.

---

## Détails ETL (Extract / Transform / Load)

Extraction
- Chaque module de `sources/` parcourt les premières pages (actuellement 1..5) et extrait `title`, `lien`, `date`, `auteur`, `source`.
- Les responses sont agrégées dans `data/raw/extracted_data.json`.

Transformation
- `etl/Transform.py`
  - `drop_duplicates(subset=["source", "lien"])`
  - `date` parsée avec `pd.to_datetime(..., errors='coerce', utc=True)` puis remplie par `scraped_at` si manquante
  - `id` généré par SHA256 de `source.lower() + '|' + lien`
  - export `data/clean/clean.csv`

Chargement
- `etl/Load.py` attend une variable d'environnement `DATABASE_URL` (Postgres). Il construit un `engine` SQLAlchemy et fait :
  1. upsert `sources` (RETURNING id)
  2. upsert `authors` (RETURNING id)
  3. insert/update `articles` (ON CONFLICT (id) DO UPDATE)

Le code utilise `sqlalchemy.dialects.postgresql.insert` et des requêtes `text()` pour la portabilité Postgres.

---

## Configuration (Supabase)

- Supabase fournit une URL Postgres que vous pouvez stocker dans `.env` sous `DATABASE_URL`.
- NE PARTEZ JAMAIS VOTRE `DATABASE_URL` DANS LE DÉPÔT PUBLIC. Utilisez :

```
# .env (local, gitignored)
DATABASE_URL=postgresql://user:password@db.host.supabase.co:5432/dbname
```

- Pour déployer sur Supabase :
  1. Créez un projet Supabase
  2. Copiez l'URL Postgres dans `.env`
  3. Créez les tables (voir schéma ci-dessous)

---

## Schéma de la base de données (Postgres)

Extrait minimal (adapté au code dans `etl/Load.py`):

```sql
CREATE TABLE sources (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE authors (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE articles (
  id TEXT PRIMARY KEY,
  title TEXT,
  url TEXT,
  source_id INTEGER REFERENCES sources(id),
  author_id INTEGER REFERENCES authors(id),
  published_at TIMESTAMP WITH TIME ZONE,
  scraped_at TIMESTAMP WITH TIME ZONE
);

-- Indexes recommandés
CREATE INDEX idx_articles_published_at ON articles(published_at);
```

---

## Journalisation & Debug

- Logger centralisé : `config/logger.py` écrit en console et dans `logs/scraper_YYYYMMDD.log`.
- Si `etl.Load` échoue à cause d'un driver/manquant `DATABASE_URL`, `main.py` catchera `ModuleNotFoundError` et sauvegardera `data/clean/loaded_data.csv` et `loaded_data.json` en fallback.

---

## Dépannage rapide

- `ModuleNotFoundError` → installer la dépendance (ex: `pip install psycopg2-binary` ou vérifier `requirements.txt`).
- `requests` timeouts → vérifier votre connectivité réseau et User-Agent (déjà paramétré dans `sources/*`).
- Si le site change son HTML, les sélecteurs BeautifulSoup dans `sources/*` doivent être mis à jour.

---

## Contribution

- Fork → branche feature → PR
- Merci d'ajouter des tests pour toute transformation ajoutée et de documenter les changements.

---

### Besoin d'aide ?
Je peux :
- générer un diagramme SVG du pipeline
- ajouter badges CI / coverage
- automatiser la création des tables via migration SQL

Si vous voulez, je peux maintenant :
- créer une migration SQL pour Supabase basée sur le schéma ci-dessus, ou
- ajouter des badges CI (GitHub Actions) et un diagramme.

---

