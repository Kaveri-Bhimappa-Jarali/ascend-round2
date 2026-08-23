import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DEFAULT_DATABASE_URL = "sqlite:///./data/cloud_compliance.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

if DATABASE_URL.startswith("sqlite:///./data/"):
    Path("data").mkdir(exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app.db import models  # noqa: F401

    _drop_legacy_phase1_violations_table()
    Base.metadata.create_all(bind=engine)


def _drop_legacy_phase1_violations_table() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "violations" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("violations")}
    if "resource_snapshot_id" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("DROP TABLE violations"))


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
