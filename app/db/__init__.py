from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from ..config import settings

Base = declarative_base()

engine = create_engine(f'postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:5432/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

@contextmanager
def get_db_for_alembic(bind=None):
  db = SessionLocal(bind=bind or engine) # Uses alembic's bind if provided. Chose to do this for migration scripts.
  try:
    yield db
    db.commit()
  except Exception as error:
    db.rollback()
    raise error
  finally:
    db.close()