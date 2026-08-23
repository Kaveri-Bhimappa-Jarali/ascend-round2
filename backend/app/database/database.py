"""SQLite database engine setup and session helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.settings import settings

Base = declarative_base()
engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def configure_database(database_url: str | None = None) -> None:
    """Configure the process-wide SQLAlchemy engine.

    Tests can call this with a temporary SQLite URL. Application startup uses
    the configured settings value. This function does not drop data.
    """

    global engine, SessionLocal

    url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)

    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    if engine is None:
        configure_database()

    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        configure_database()

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


configure_database()
