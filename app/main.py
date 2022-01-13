from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI

from app.database.conn import db
from app.common.config import conf
from app.routes import index, auth

def create_app():
    """ 앱 함수 실행 """
    c = conf()
    app = FastAPI()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)

    # 라우터 정의
    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    
    return app


app = create_app()
