<div align="center">

# 📰 NewsScraper

### **Pipeline ETL** — TechCrunch · The Verge · Ars Technica

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.32.5-FF6B35?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.14.3-BB86FC?style=for-the-badge&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Postgres-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Latest-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlite&logoColor=white)

**Extract → Transform → Load** : extraction multi-site, nettoyage via **pandas** et chargement vers Postgres (Supabase friendly). Logs locaux et fallback CSV/JSON si la BD est indisponible.

[Installation](#-installation-rapide) · [Utilisation](#-exemples-dutilisation) · [Architecture](#️-fichiers-clés--architecture) · [Configuration](#️-configuration--supabase)

</div>

---

## 📑 Table des matières

- [🎯 Aperçu](#-aperçu)
- [✨ Fonctionnalités clés](#-fonctionnalités-clés)
- [⚡ Installation rapide](#-installation-rapide)
- [🚀 Exemples d'utilisation](#-exemples-dutilisation)
- [🏗️ Fichiers clés & architecture](#️-fichiers-clés--architecture)
- [🔄 Détails ETL](#-détails-etl)
- [⚙️ Configuration & Supabase](#️-configuration--supabase)
- [💾 Schéma SQL minimal](#-schéma-sql-minimal)
- [📝 Journalisation & debugging](#-journalisation--debugging)
- [🔧 Dépannage rapide](#-dépannage-rapide)
- [🤝 Contribuer](#-contribuer)

---

## 🎯 Aperçu

Ce projet met en place un pipeline ETL léger qui :

```mermaid
graph LR
    A[🔍 Scrape] -->|Actualités tech| B[🧹 Nettoie]
    B -->|Normalise| C[💾 Charge]
    C -->|Postgres/Supabase| D[✅ Stocké]
    style A fill:#FF6B35,stroke:#fff,stroke-width:2px,color:#fff
    style B fill:#F7931E,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#00D9FF,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#00E676,stroke:#fff,stroke-width:2px,color:#fff
```

### 🌐 Sources implémentées

| Site | Script | Description |
|------|--------|-------------|
| 🚀 **TechCrunch** | [`sources/extract_tech.py`](sources/extract_tech.py) | Actualités startup & tech |
| 🔷 **The Verge** | [`sources/extract_thev.py`](sources/extract_thev.py) | Tech, science, culture |
| ⚙️ **Ars Technica** | [`sources/extract_ar.py`](sources/extract_ar.py) | Tech approfondie |

---

## ✨ Fonctionnalités clés

<table>
<tr>
<td width="50%">

### 🔎 Extraction HTML multi-page
Via `requests` + `BeautifulSoup`
- Parcourt plusieurs pages (configurable)
- Headers & User-Agent personnalisables
- Gestion des timeouts

</td>
<td width="50%">

### 🧹 Transformation pandas
Nettoyage intelligent des données
- Déduplication automatique
- Parsing de dates avec fallback
- Génération d'ID unique (SHA256)

</td>
</tr>
<tr>
<td width="50%">

### 💾 Chargement Postgres
Via SQLAlchemy
- Upsert pour éviter doublons
- Compatible Supabase
- Gestion des relations (sources, authors)

</td>
<td width="50%">

### 🧾 Logging centralisé
Configuration via `config/logger.py`
- Console + fichier horodaté
- Niveaux de log configurables
- Fallback CSV/JSON si BD indisponible

</td>
</tr>
</table>

---

## ⚡ Installation rapide

```bash
# 1️⃣ Cloner le repo
git clone <votre-repo> NewsScraper
cd NewsScraper

# 2️⃣ Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3️⃣ Installer les dépendances
pip install -r requirements.txt
```

> [!IMPORTANT]
> Créez un fichier `.env` (NE PAS committer) et vérifiez qu'il est dans `.gitignore`

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Exemple: URL fournie par Supabase — gardez-la secrète 🔒
```

---

## 🚀 Exemples d'utilisation

### Lancer le pipeline complet

```bash
python main.py
```

### Exécution par étapes

<table>
<tr>
<td>

**📥 Extraction uniquement**
```bash
python -m etl.Extract
```

</td>
<td>

**🔄 Transformation uniquement**
```bash
python -m etl.Transform
```

</td>
<td>

**📤 Chargement uniquement**
```bash
python -m etl.Load
```

</td>
</tr>
</table>

> [!TIP]
> Utilisez les modules individuels pour tester chaque étape séparément

**Fichiers clés** : [`main.py`](main.py) · [`etl/Extract.py`](etl/Extract.py) · [`etl/Transform.py`](etl/Transform.py) · [`etl/Load.py`](etl/Load.py)

---

## 🏗️ Fichiers clés & architecture

```
NewsScraper/
├── 📁 etl/
│   ├── Extract.py      # 📥 Agrège les articles → data/raw/extracted_data.json
│   ├── Transform.py    # 🔄 Normalise & nettoie → data/clean/clean.csv
│   └── Load.py         # 📤 Upserts vers Postgres (DATABASE_URL)
├── 📁 sources/
│   ├── extract_tech.py # 🚀 Scraper TechCrunch
│   ├── extract_thev.py # 🔷 Scraper The Verge
│   └── extract_ar.py   # ⚙️ Scraper Ars Technica
├── 📁 config/
│   └── logger.py       # 📝 Configuration logging centralisé
├── 📁 data/
│   ├── raw/            # 📊 Données brutes (JSON)
│   └── clean/          # ✨ Données nettoyées (CSV)
├── 📁 logs/            # 📋 Fichiers de log horodatés
├── main.py             # 🎭 Orchestrateur principal
└── requirements.txt    # 📦 Dépendances Python
```

---

## 🔄 Détails ETL

### 📥 **Extraction**

Les scripts dans `sources/` parcourent les pages **1..5** (configurable) et extraient :

| Champ | Description |
|-------|-------------|
| `title` | Titre de l'article |
| `lien` | URL complète |
| `date` | Date de publication |
| `auteur` | Nom de l'auteur |
| `source` | Nom du site |

**Output** → `data/raw/extracted_data.json`

---

### 🔄 **Transformation**

`etl/Transform.py` effectue les opérations suivantes :

```python
# 1️⃣ Suppression des doublons
df.drop_duplicates(subset=["source", "lien"], inplace=True)

# 2️⃣ Parsing des dates avec fallback
df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
df['date'].fillna(df['scraped_at'], inplace=True)

# 3️⃣ Génération d'ID unique (SHA256)
df['id'] = df.apply(lambda row: hashlib.sha256(
    f"{row['source'].lower()}|{row['lien']}".encode()
).hexdigest(), axis=1)
```

**Output** → `data/clean/clean.csv`

---

### 📤 **Chargement**

`etl/Load.py` utilise `DATABASE_URL` pour créer un engine SQLAlchemy :

```mermaid
graph TD
    A[Données nettoyées] -->|1| B[Upsert sources]
    B -->|2| C[Upsert authors]
    C -->|3| D[Insert/Update articles]
    D -->|ON CONFLICT id| E[Base à jour ✅]
    style A fill:#00D9FF,stroke:#fff,stroke-width:2px,color:#fff
    style E fill:#00E676,stroke:#fff,stroke-width:2px,color:#fff
```

---

## ⚙️ Configuration & Supabase

### 🔐 Fichier `.env` (local, gitignored)

```env
DATABASE_URL=postgresql://user:password@db.host.supabase.co:5432/dbname
```

> [!WARNING]
> **NE JAMAIS** committer `DATABASE_URL` dans le dépôt

### 📋 Étapes rapides pour Supabase

1. **Créez un projet Supabase** sur [supabase.com](https://supabase.com)
2. **Copiez l'URL Postgres** (Settings → Database → Connection String)
3. **Collez dans `.env`** sous `DATABASE_URL`
4. **Créez les tables** (voir schéma SQL ci-dessous)

---

## 💾 Schéma SQL minimal

Copiez/executez ce SQL dans **Supabase SQL Editor** ou via `psql` :

```sql
-- Table des sources (sites web)
CREATE TABLE sources (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- Table des auteurs
CREATE TABLE authors (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- Table des articles
CREATE TABLE articles (
  id TEXT PRIMARY KEY,
  title TEXT,
  url TEXT,
  source_id INTEGER REFERENCES sources(id),
  author_id INTEGER REFERENCES authors(id),
  published_at TIMESTAMP WITH TIME ZONE,
  scraped_at TIMESTAMP WITH TIME ZONE
);

-- Index pour les recherches par date
CREATE INDEX idx_articles_published_at ON articles(published_at);
```

### 📊 Relations entre tables

```mermaid
erDiagram
    sources ||--o{ articles : "a plusieurs"
    authors ||--o{ articles : "écrit plusieurs"
    
    sources {
        int id PK
        text name UK
    }
    
    authors {
        int id PK
        text name UK
    }
    
    articles {
        text id PK
        text title
        text url
        int source_id FK
        int author_id FK
        timestamp published_at
        timestamp scraped_at
    }
```

---

## 📝 Journalisation & debugging

### 📋 Logger centralisé

Configuration dans [`config/logger.py`](config/logger.py) :
- ✅ **Console** : affichage en temps réel
- ✅ **Fichier** : `logs/scraper_YYYYMMDD.log`

### 💾 Fallback automatique

Si la BD est indisponible, `main.py` :
1. Capture l'erreur
2. Sauvegarde les données dans `data/clean/`
3. Formats : **CSV** + **JSON**

> [!TIP]
> Augmentez le niveau de logs à `DEBUG` dans `config/logger.py` pour plus de détails

---

## 🔧 Dépannage rapide

<table>
<tr>
<td width="30%">

### ❌ ModuleNotFoundError

</td>
<td width="70%">

**Solution** : Installer la dépendance manquante
```bash
pip install psycopg2-binary
# ou autre driver Postgres
```

</td>
</tr>
<tr>
<td width="30%">

### ⏱️ Timeouts requests

</td>
<td width="70%">

**Solution** : Vérifier connectivité et User-Agent
- Testez votre connexion internet
- Ajustez le User-Agent dans `sources/*`
- Augmentez le timeout si nécessaire

</td>
</tr>
<tr>
<td width="30%">

### 🔍 Sélecteurs cassés

</td>
<td width="70%">

**Solution** : Mettre à jour les sélecteurs BeautifulSoup
- Les sites changent leur HTML régulièrement
- Inspectez le HTML actuel du site
- Mettez à jour les sélecteurs dans `sources/*`

</td>
</tr>
</table>

---

## 🤝 Contribuer

```mermaid
graph LR
    A[🍴 Fork] -->|Clone| B[🌿 Branche feature]
    B -->|Commit| C[✅ Tests]
    C -->|Push| D[📬 Pull Request]
    style A fill:#FF6B35,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#00E676,stroke:#fff,stroke-width:2px,color:#fff
```

### 📝 Guidelines

- ✅ **Fork** le repo → créez une branche `feature/ma-feature`
- ✅ **Tests** : ajoutez des tests pour toute transformation
- ✅ **Documentation** : documentez les changements
- ✅ **Pull Request** : description claire des modifications

> [!NOTE]
> Merci de suivre le style de code existant et d'ajouter des docstrings

---

<div align="center">

### Fait avec ❤️ pour le scraping intelligent d'actualités tech

**📰 NewsScraper** — Pipeline ETL moderne et efficace

[![GitHub](https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge&logo=github)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>
