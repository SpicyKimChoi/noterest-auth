import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from starlette.requests import Request
from jwt.exceptions import ExpiredSignatureError, DecodeError
from sqlalchemy.orm import Session

from app.database.schema import Users
from app.models import UserMe, UserModify, Token, UserToken
from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db

router = APIRouter(prefix='/user')


@router.get('/me', response_model=UserMe)
async def get_me(request: Request):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate':'Bearer'}
    )

    headers = request.headers

    try:
        if "authorization" in headers.keys():
            payload = await token_decode(headers.get("Authorization"))
            print(payload)
            id = payload.get('id')
            if id is None:
                raise credentials_exception
        else:
            raise credentials_exception
        
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content=dict(msg="Invaild Token")) 
    
    user = Users.get(id=id)
    if user is None:
        raise JSONResponse(status_code=404, content=dict(msg="User Not Found")) 
    
    return UserMe.from_orm(user).dict(exclude={'pw'})


@router.put('/me', response_model=Token)
async def put_me(request: Request, user_info: UserModify, session: Session = Depends(db.session)):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate':'Bearer'}
    )

    headers = request.headers
    is_n_exist = await is_nick_exist(user_info.nickname)

    try:
        if "authorization" in headers.keys():
            payload = await token_decode(headers.get("Authorization"))
            print(payload)
            id = payload.get('id')
            if id is None:
                raise credentials_exception
        else:
            raise credentials_exception
        
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content=dict(msg="Invaild Token")) 
    
    if is_n_exist:
        return JSONResponse(status_code=400, content=dict(msg="NICK_EXISTS"))

    user = Users.filter(session, id=id)
    
    if user is None:
        raise JSONResponse(status_code=404, content=dict(msg="User Not Found")) 

    change_user = user.update(auto_commit=True, 
        nickname=user_info.nickname, 
        phone_number=user_info.phone_number)
    token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(change_user).dict(exclude={'pw'}),)}")
    return token


async def token_decode(access_token):
    token_expired=HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token Expired",
    )

    token_decode_err=HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token has been compromised",
    )

    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
    except ExpiredSignatureError:
        return token_expired
    except DecodeError:
        raise token_decode_err
    return payload

async def is_nick_exist(nick: str):
    get_nick = Users.get(nickname=nick)
    if get_nick:
        return True
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt