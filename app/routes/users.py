import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from starlette.requests import Request
from jwt.exceptions import ExpiredSignatureError, DecodeError

from app.database.schema import Users
from app.models import UserMe
from app.common.consts import JWT_SECRET, JWT_ALGORITHM

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