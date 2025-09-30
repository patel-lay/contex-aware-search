from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv
load_dotenv()
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_rag_db")

database_url = (
    f"postgresql+psycopg2://{POSTGRES_USERNAME}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{DATABASE_NAME}"
)

# Create the SQLAlchemy engine
engine = create_engine(
    database_url,
    pool_size = 10,               #max connection
    max_overflow = 20,            #extra temporary connection if pool is full
    pool_timeout = 30,            #wait max 30s for a connection
    pool_recycle = 1800,          #recycle connections every 30 min
    connect_args = {
        "connect_timeout": 10 }   #fail fast if Db doesn't respone
    )

# # Create the database if it doesn't exist
# if not database_exists(engine.url):
#     try:
#         create_database(engine.url)
#         print(f"Database {DATABASE_NAME} created successfully.")
#     except Exception as e:
#         print(f"Error creating database: {e}")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

from contextlib import contextmanager

@contextmanager
def get_session():
    """Provide a transactional scope for DB operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
