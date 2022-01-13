from app.database.schema import Users
from app.routes.auth import create_access_token
from app.models import UserToken

def test_get_me(client):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    regi_res = client.post("api/auth/register", json=user)
    regi_res_body = regi_res.json()
    token = regi_res_body["Authorization"]

    res = client.get("api/user/me", headers={"Authorization": token})
    res_body = res.json()

    assert res.status_code == 200
    assert 'id' in res_body.keys() 
    assert 'email' in res_body.keys() 
    assert 'nickname' in res_body.keys() 
    assert 'phone_number' in res_body.keys() 
    assert 'profile_img' in res_body.keys() 
    assert res_body['email'] == user['email']
    assert res_body['nickname'] == user['nickname']


def test_get_me_without_token(client):
    res = client.get("api/user/me")
    res_body = res.json()
    print(res_body)

    assert res.status_code == 401
    assert 'Could not validate credentials' == res_body["detail"]


def test_put_me(client):
    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    regi_res = client.post("api/auth/register", json=user)
    regi_res_body = regi_res.json()
    token = regi_res_body["Authorization"]

    user_modify = dict(nickname="더욱더 매운 김치", phone_number="010-1234-5678")
    res = client.put("api/user/me", headers={"Authorization": token}, json=user_modify)
    res_body = res.json()

    db_user = Users.get(email=user['email'])
    access_token = create_access_token(data=UserToken.from_orm(db_user).dict(exclude={'pw'}),)
    assert res.status_code == 200
    assert res_body["Authorization"] is not None
    assert res_body["Authorization"] == f"Bearer {access_token}"


def test_put_me_with_exist_nick(client):
    test_user = dict(email="test@test.com", pw="123", nickname='테스터')
    client.post("api/auth/register", json=test_user)

    user = dict(email="spicykimchoi@test.com", pw="123", nickname='매운김치')
    regi_res = client.post("api/auth/register", json=user)
    regi_res_body = regi_res.json()
    token = regi_res_body["Authorization"]

    user_modify = dict(nickname="테스터", phone_number="010-1234-5678")
    res = client.put("api/user/me", headers={"Authorization": token}, json=user_modify)
    res_body = res.json()

    assert res.status_code == 400
    assert 'NICK_EXISTS' == res_body["msg"]
    