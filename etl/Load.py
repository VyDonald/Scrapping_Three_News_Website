import os
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import pandas as pd
from config.logger import setup_logger
load_dotenv()
logger = setup_logger()

# =============================
# DATABASE CONNECTION
# =============================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

Session = sessionmaker(bind=engine)


# =============================
# LOAD FUNCTION
# =============================

def load_to_db(df: pd.DataFrame):

    logger.info("[LOAD] Starting load process")

    session = Session()

    try:

        for _, row in df.iterrows():

            # -----------------------------
            # 1️⃣ UPSERT SOURCE
            # -----------------------------
            source_stmt = insert_source(row["source"])
            result = session.execute(source_stmt)
            source_id = result.scalar()


            # -----------------------------
            # 2️⃣ UPSERT AUTHOR
            # -----------------------------
            author_stmt = insert_author(row["auteur"])
            result = session.execute(author_stmt)
            author_id = result.scalar()


            # -----------------------------
            # 3️⃣ UPSERT ARTICLE
            # -----------------------------
            article_stmt = insert_article(
                row=row,
                source_id=source_id,
                author_id=author_id
            )

            session.execute(article_stmt)

        session.commit()
        logger.info(f"[LOAD] Successfully loaded {len(df)} records")

    except Exception as e:
        session.rollback()
        logger.exception("[LOAD] Error during loading")
        raise

    finally:
        session.close()


# =============================
# UPSERT HELPERS
# =============================

def insert_source(source_name: str):

    stmt = text("""
        INSERT INTO sources (name)
        VALUES (:name)
        ON CONFLICT (name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
    """)

    return stmt.bindparams(name=source_name)


def insert_author(author_name: str):

    stmt = text("""
        INSERT INTO authors (name)
        VALUES (:name)
        ON CONFLICT (name)
        DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
    """)

    return stmt.bindparams(name=author_name)


def insert_article(row, source_id, author_id):

    stmt = text("""
        INSERT INTO articles (
            id,
            title,
            url,
            source_id,
            author_id,
            published_at,
            scraped_at
        )
        VALUES (
            :id,
            :title,
            :url,
            :source_id,
            :author_id,
            :published_at,
            :scraped_at
        )
        ON CONFLICT (id)
        DO UPDATE SET
            title = EXCLUDED.title,
            scraped_at = EXCLUDED.scraped_at;
    """)

    return stmt.bindparams(
        id=row["id"],
        title=row["title"],
        url=row["lien"],
        source_id=source_id,
        author_id=author_id,
        published_at=row["date"],
        scraped_at=row["scraped_at"]
    )
if __name__ == "__main__":
    # Test local uniquement
    df_test = pd.DataFrame({
        "id": ["test123"],
        "title": ["Test Article"],
        "lien": ["https://example.com/test-article"],
        "source": ["Test Source"],
        "auteur": ["Test Author"],
        "date": [pd.Timestamp("2024-01-01T12:00:00Z")],
        "scraped_at": [pd.Timestamp.utcnow()]
    })
    load_to_db(df_test)