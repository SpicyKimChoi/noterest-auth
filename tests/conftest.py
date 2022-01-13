from fastapi.testclient import TestClient
from dotenv import load_dotenv
from typing import List
from sqlalchemy.orm import Session
import os
import pytest

from app.main import app
from app.database.conn import db, Base


os.environ["API_ENV"] = "test"
# client = TestClient(app)

@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope="function", autouse=True)
def session():
    sess = next(db.session())
    yield sess
    clear_all_table_data(
        session=sess,
        metadata=Base.metadata,
        except_tables=[]
    )
    sess.rollback()


@pytest.fixture(scope="session")
def client():
    # Create tables
    return TestClient(app=app)


def clear_all_table_data(session: Session, metadata, except_tables: List[str] = None):
    session.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in metadata.sorted_tables:
        if table.name not in except_tables:
            session.execute(table.delete())
    session.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()