from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.event import listen
from sqlalchemy.sql import select, func

from config import SQLALCHEMY_DATABASE_URL


def load_spatialite(dbapi_conn, _):
    """Loads SpatiaLite module for spatial SQLite capabilities."""
    dbapi_conn.enable_load_extension(True)
    dbapi_conn.load_extension("/usr/lib/x86_64-linux-gnu/mod_spatialite.so")


# check_same_thread only applies to sqlite
# In FastAPI, more than one thread could interact with the database
# for the same request. So we bypass this check.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
listen(engine, "connect", load_spatialite)

# Initialize necessary metadata tables.
# This may take time at first attempt, but will be ignored
# once the tables are created.
conn = engine.connect()
conn.execute(select([func.InitSpatialMetadata()]))
conn.close()


# A session will be created for each request via dependencies.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Creates a new session for each request and closes it once finished."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
