import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import database as db


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    db_path = tmp_path / "test_compliance.db"
    db.configure_database(f"sqlite:///{db_path}")
    db.init_db()
    yield
    db.Base.metadata.drop_all(bind=db.engine)
    if db.engine:
        db.engine.dispose()

