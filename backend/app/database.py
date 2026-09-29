from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Support both PostgreSQL and SQLite (for local dev / CI)
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(settings.DATABASE_URL)
else:
    # SQLite fallback — no external DB server needed
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
