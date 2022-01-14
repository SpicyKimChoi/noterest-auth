from datetime import datetime, timedelta

import jwt
import boto3
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import File, UploadFile
from starlette.responses import JSONResponse
from starlette.requests import Request
from jwt.exceptions import ExpiredSignatureError, DecodeError
from sqlalchemy.orm import Session
from os import environ
from botocore.exceptions import ClientError

from app.database.schema import Users
from app.models import UserMe, UserModify, Token, UserToken
from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.common.consts import S3_BUCKET_NAME, REGION, PROFILE_FOLDER_NAME
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


@router.put('/update-profile', response_model=Token)
async def put_profile_img(request: Request, file_obj: UploadFile = File(...), session: Session = Depends(db.session)):
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
    
    user = Users.filter(session, id=id)
    userdata = Users.get(session, id=id)
    legacy_profile_url = userdata.profile_img
    
    new_profile_name = f'{id}#{datetime.utcnow()}#{file_obj.filename}'

    bucket_location = boto3.client('s3').get_bucket_location(Bucket=S3_BUCKET_NAME)
    
    if user is None:
        raise JSONResponse(status_code=404, content=dict(msg="User Not Found")) 

    upload_obj = upload_file(s3_client=get_s3_client(), 
        file_obj=file_obj.file,
        object_name=new_profile_name
    )

    if not upload_obj:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File could not be uploaded")
    elif legacy_profile_url:
        delt= delete_file(s3_client=get_s3_client(),object_name=legacy_profile_url)
        if delt:
            print('success!')
        else:
            print('delete fail')

    object_url = "https://s3-{0}.amazonaws.com/{1}/{2}/{3}".format(
        bucket_location['LocationConstraint'],
        S3_BUCKET_NAME,
        PROFILE_FOLDER_NAME,
        new_profile_name)    

    change_user = user.update(auto_commit=True, 
        profile_img=object_url)
    token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(change_user).dict(exclude={'pw'}),)}")
    return token


def get_s3_client():
    aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY")
    s3_client = boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return s3_client


def upload_file(s3_client: boto3.client, file_obj, object_name=None):
    """Upload a file to an S3 bucket
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_obj
    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET_NAME, f"{PROFILE_FOLDER_NAME}/{object_name}",  ExtraArgs={"ACL": "public-read"})
    except ClientError as e:
        return False
    return True


def delete_file(s3_client: boto3.client, object_name=None):
    """Upload a file to an S3 bucket
    """
    # If S3 object_name was not specified, use file_name
    print(object_name)
    bucket_location = boto3.client('s3').get_bucket_location(Bucket=S3_BUCKET_NAME)
    obj_name = object_name.replace(f"https://s3-{bucket_location['LocationConstraint']}.amazonaws.com/{S3_BUCKET_NAME}/", "")
    print('!!!!!!!!!!!!!!!!!!!')
    print(obj_name)
    print('!!!!!!!!!!!!!!!!!!!')
    # print(f"{PROFILE_FOLDER_NAME}/{object_name}")
    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=obj_name
        )
    except ClientError as e:
        return False
    return True


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