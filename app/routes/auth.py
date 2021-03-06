from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.schema import Users
from app.models import Token, UserToken, UserRegister, UserLogin

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=201, response_model=Token)
async def register(reg_info: UserRegister, session: Session = Depends(db.session)):
    """
    `회원가입 API`
    """
    is_e_exist = await is_email_exist(reg_info.email)
    is_n_exist = await is_nick_exist(reg_info.nickname)

    if not reg_info.email or not reg_info.pw or not reg_info.nickname:
        return JSONResponse(status_code=400, content=dict(msg="Email and PW, Nickname must be provided'"))

    if is_e_exist:
        return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
    
    if is_n_exist:
        return JSONResponse(status_code=400, content=dict(msg="NICK_EXISTS"))

    hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt())
    new_user = Users.create(session, auto_commit=True, pw=hash_pw.decode('utf-8'), email=reg_info.email, nickname=reg_info.nickname)
    token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw'}),)}")
    
    return token


@router.post("/login", status_code=200, response_model=Token)
async def login(user_info: UserLogin):
    is_exist = await is_email_exist(user_info.email)

    if not user_info.email or not user_info.pw:
        return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided'"))

    if not is_exist:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

    user = Users.get(email=user_info.email)
    is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))
    
    if not is_verified:
        return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
    token = dict(
        Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw'}),)}")
    return token


async def is_email_exist(email: str):
    get_email = Users.get(email=email)
    if get_email:
        return True
    return False


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