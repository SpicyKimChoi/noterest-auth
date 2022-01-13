from fastapi.testclient import TestClient
from dotenv import load_dotenv
from typing import List
from sqlalchemy.orm import Session
import os
import pytest

from app.main import app
from app.database.conn import db, Base
from app.database.schema import Users
from app.routes.auth import create_access_token
from app.models import UserToken

os.environ["API_ENV"] = "test"
client = TestClient(app)

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


def test_healthcheck_ping():
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.json() == {"status" : "pass"}


def test_healthcheck_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status" : "pass"}


def test_registration():
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    res = client.post("api/auth/register", json=user)
    res_body = res.json()
    print(res.json())
    assert res.status_code == 201
    assert "Authorization" in res_body.keys()


def test_registration_exist_email(session):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    user2 = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치2')
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register", json=user2)
    res_body = res.json()
    assert res.status_code == 400
    assert 'EMAIL_EXISTS' == res_body["msg"]


def test_registration_exist_nickname(session):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    user2 = dict(email="spicykimchoi@test2.com", pw="123", nickname='매운김치')
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register", json=user2)
    res_body = res.json()
    assert res.status_code == 400
    assert 'NICK_EXISTS' == res_body["msg"]


def test_login():
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    res = client.post("api/auth/register", json=user)

    user_login = dict(email="spicykimchoi@test.com", pw="123")
    res = client.post("api/auth/login", json=user_login)
    res_body = res.json()

    db_user = Users.get(email=user['email'])
    access_token = create_access_token(data=UserToken.from_orm(db_user).dict(exclude={'pw'}),)
    assert res.status_code == 200
    assert res_body["Authorization"] is not None
    assert res_body["Authorization"] == f"Bearer {access_token}"


def test_login_not_exist_email():
    user_login = dict(email="spicykimchoi@test.com", pw="123")
    res = client.post("api/auth/login", json=user_login)
    res_body = res.json()
    assert res.status_code == 400
    assert 'NO_MATCH_USER' == res_body["msg"]


def clear_all_table_data(session: Session, metadata, except_tables: List[str] = None):
    session.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in metadata.sorted_tables:
        if table.name not in except_tables:
            session.execute(table.delete())
    session.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()