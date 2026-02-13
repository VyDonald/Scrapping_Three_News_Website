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
<div align="center">
  <h1>📰 NewsScraper</h1>
  <p><strong>Pipeline ETL</strong> — TechCrunch · The Verge · Ars Technica</p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt="python"> 
    <img src="https://img.shields.io/badge/requests-2.32.5-orange.svg" alt="requests"> 
    <img src="https://img.shields.io/badge/BeautifulSoup-4.14.3-purple.svg" alt="bs4"> 
    <img src="https://img.shields.io/badge/Supabase-Postgres-5ed3a2.svg" alt="supabase">
  </p>
  <p style="max-width:800px">Extract → Transform → Load : extraction multi-site, nettoyage via <strong>pandas</strong> et chargement vers Postgres (Supabase friendly). Logs locaux et fallback CSV/JSON si la BD est indisponible.</p>
</div>

---
---


## 🧭 Mini table des matières

- [Aperçu](#aper%C3%A7u)
- [Fonctionnalités clés](#fonctionnalit%C3%A9s-cl%C3%A9s)
- [Installation rapide](#installation-rapide)
- [Exemples d'utilisation](#exemples-dutilisation)
- [Fichiers clés & architecture](#fichiers-cl%C3%A9s--architecture)
- [Détails ETL](#d%C3%A9tails-etl)
- [Configuration & Supabase (.env)](#configuration--supabase-env)
- [Schéma SQL minimal](#sch%C3%A9ma-sql-minimal)
- [Journalisation & debugging](#journalisation--debugging)
- [Dépannage rapide](#d%C3%A9pannage-rapide)
- [Contribuer](#contribuer)

---

---

## Aperçu

Ce projet met en place un pipeline ETL léger qui :

- Scrape les dernières actualités de trois sites techno
- Nettoie et normalise les métadonnées (date, auteur, url)
- Charge les articles dans une base Postgres (Supabase)

Sources implémentées :

- TechCrunch — [sources/extract_tech.py](sources/extract_tech.py)
- The Verge — [sources/extract_thev.py](sources/extract_thev.py)
- Ars Technica — [sources/extract_ar.py](sources/extract_ar.py)

---


## Fonctionnalités clés

- 🔎 Extraction HTML multi-page via `requests` + `BeautifulSoup`
- 🧹 Transformation avec `pandas` : déduplication, parsing de dates, génération d'un `id` unique (SHA256)
- 💾 Chargement via SQLAlchemy vers Postgres (compatible Supabase). Upsert pour éviter les doublons.
- 🧾 Logging centralisé (console + fichier) via [config/logger.py](config/logger.py)
- ♻️ Fallback : si la BD est indisponible, les données nettoyées sont sauvegardées en CSV/JSON dans `data/clean/`


---


## Installation rapide

```bash
git clone <votre-repo> OpenFoodFacts
cd OpenFoodFacts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` (NE PAS committer) :

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Exemple: URL fournie par Supabase — gardez-la secrète
```

Vérifiez que `.env` est dans `.gitignore`.

---


## Exemples d'utilisation

- Lancer le pipeline complet :

```bash
python main.py
```

- Lancer uniquement l'extraction :

```bash
python -m etl.Extract
```

- Lancer la transformation locale :

```bash
python -m etl.Transform
```

- Lancer le chargement (attention à `DATABASE_URL`) :

```bash
python -m etl.Load
```

Fichiers clés : [main.py](main.py), [etl/Extract.py](etl/Extract.py), [etl/Transform.py](etl/Transform.py), [etl/Load.py](etl/Load.py), [config/logger.py](config/logger.py).

---


## Fichiers clés & architecture

- `main.py` — orchestrateur : Extract → Transform → Load
- `etl/Extract.py` — agrége les articles extraits et écrit `data/raw/extracted_data.json`
- `etl/Transform.py` — charge le JSON brut, normalise, génère `id` et écrit `data/clean/clean.csv`
- `etl/Load.py` — effectue les upserts vers Postgres (utilise `DATABASE_URL`)
- `sources/` — implémentations Scraper pour chaque site : [sources/extract_tech.py](sources/extract_tech.py), [sources/extract_thev.py](sources/extract_thev.py), [sources/extract_ar.py](sources/extract_ar.py)


---


## Détails ETL

Extraction

- Les scripts dans `sources/` parcourent les pages 1..5 (configurable) et extraient : `title`, `lien`, `date`, `auteur`, `source`.
- Résultat agrégé dans `data/raw/extracted_data.json` par [etl/Extract.py](etl/Extract.py).

Transformation

- `etl/Transform.py` :
  - Supprime les doublons via `drop_duplicates(subset=["source","lien"])`.
  - Parse `date` avec `pd.to_datetime(..., errors='coerce', utc=True)` et remplit avec `scraped_at` si absent.
  - Génère `id` SHA256 sur `source.lower() + '|' + lien`.
  - Exporte `data/clean/clean.csv`.

Chargement

- `etl/Load.py` utilise `DATABASE_URL` (Postgres) pour créer un `engine` SQLAlchemy.
- Processus : upsert `sources`, upsert `authors`, insert/update `articles` (ON CONFLICT sur `id`).


---


## Configuration & Supabase (.env)

- Supabase fournit une URL Postgres (stockez-la dans `.env` sous `DATABASE_URL`).
- NE JAMAIS committer `DATABASE_URL` dans le dépôt.

Exemple `.env` (local, gitignored) :

```env
DATABASE_URL=postgresql://user:password@db.host.supabase.co:5432/dbname
```

Étapes rapides pour Supabase :

1. Créez un projet Supabase
2. Copiez l'URL Postgres dans `.env`
3. Créez les tables (voir schéma SQL minimal)

---


## Schéma SQL minimal

Copiez/executez ce SQL dans Supabase SQL Editor ou via psql :

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

CREATE INDEX idx_articles_published_at ON articles(published_at);
```

---


## Journalisation & debugging

- Logger centralisé dans [config/logger.py](config/logger.py) : écriture console + `logs/scraper_YYYYMMDD.log`.
- `main.py` capture les erreurs de driver/base et écrit un fallback CSV/JSON dans `data/clean/` si nécessaire.

Conseil : augmentez le niveau de logs dans `config/logger.py` pour DEBUG localement.

---


## Dépannage rapide

- `ModuleNotFoundError` → installer la dépendance (`pip install psycopg2-binary` ou autre driver Postgres).
- `requests` timeouts → vérifier connectivité et User-Agent dans `sources/*`.
- Sélecteurs cassés → mettre à jour les sélecteurs BeautifulSoup dans `sources/*` lorsque le HTML des sites change.

---

## Contribuer

- Fork → branche feature → PR
- Ajoutez des tests pour toute logique de transformation

---

Si vous voulez, je peux maintenant :

- générer un fichier `migrations/initial_schema.sql` basé sur le schéma ci-dessus, ou
- ajouter un diagramme SVG du pipeline et des badges CI.


---

## Contribution

- Fork → branche feature → PR
- Merci d'ajouter des tests pour toute transformation ajoutée et de documenter les changements.

---
