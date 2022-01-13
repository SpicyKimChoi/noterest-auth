from pydantic.main import BaseModel

class UserRegister(BaseModel):
    email: str = None
    pw: str = None
    nickname: str = None


class UserLogin(BaseModel):
    email: str = None
    pw: str = None


class Token(BaseModel):
    Authorization: str = None


class UserModify(BaseModel):
    nickname: str = None
    phone_number: str = None


class UserToken(BaseModel):
    id: int
    email: str = None
    nickname: str = None
    phone_number: str = None
    profile_img: str = None

    class Config:
        orm_mode = True


class UserMe(BaseModel):
    id: int
    email: str = None
    nickname: str = None
    phone_number: str = None
    profile_img: str = None

    class Config:
        orm_mode = True

