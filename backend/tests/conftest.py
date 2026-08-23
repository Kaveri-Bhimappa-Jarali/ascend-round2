import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
def isolated_database(tmp_path):
    from app.database.database import Base, configure_database, engine, init_db

    db_path = tmp_path / "test_compliance.db"
    configure_database(f"sqlite:///{db_path}")
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
