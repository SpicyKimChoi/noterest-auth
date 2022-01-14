from app.database.schema import Users
from app.routes.auth import create_access_token
from app.models import UserToken

def test_healthcheck_ping(client):
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.json() == {"status" : "pass"}


def test_healthcheck_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {"status" : "pass"}


def test_registration(client):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    res = client.post("api/auth/register", json=user)
    res_body = res.json()
    print(res.json())
    assert res.status_code == 201
    assert "Authorization" in res_body.keys()


def test_registration_exist_email(session, client):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    user2 = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치2')
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register", json=user2)
    res_body = res.json()
    assert res.status_code == 400
    assert 'EMAIL_EXISTS' == res_body["msg"]


def test_registration_exist_nickname(session, client):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    user2 = dict(email="spicykimchoi@test2.com", pw="123", nickname='매운김치')
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register", json=user2)
    res_body = res.json()
    assert res.status_code == 400
    assert 'NICK_EXISTS' == res_body["msg"]


def test_login(client):
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


def test_login_not_exist_email(client):
    user_login = dict(email="spicykimchoi@test.com", pw="123")
    res = client.post("api/auth/login", json=user_login)
    res_body = res.json()
    assert res.status_code == 400
    assert 'NO_MATCH_USER' == res_body["msg"]