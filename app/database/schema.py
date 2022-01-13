from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Enum,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Session
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.conn import Base, db


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    https://docs.sqlalchemy.org/en/14/core/custom_types.html#backend-agnostic-guid-type
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, 
        comment="PK user id")
    uuid = Column(GUID(), default=uuid.uuid4, 
        comment="uuid")
    
    status = Column(Enum("active", "deleted", "blocked"), default="active", 
        comment="계정 상태")
    email = Column(String(length=255), nullable=False, unique=True, comment="이메일")
    pw = Column(String(length=2000), nullable=False, comment="비밀번호")
    nickname = Column(String(length=255), nullable=False, comment="닉네임")
    phone_number = Column(String(length=20), nullable=True, unique=True,
        comment="전화번호")
    profile_img = Column(String(length=1000), nullable=True, comment="프로필 이미지")

    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp(),
        comment="생성일자")
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(),
        onupdate=func.utc_timestamp(), comment="최종 수정 일자")