from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()

@router.get('/ping')
def ping():
    """ Liveness probe """
    resp = {
        "status" : "pass"
    }
    return JSONResponse(resp)


@router.get('/health')
def health():
    """ readiness probe """
    resp = {
        "status" : "pass"
    }
    return JSONResponse(resp)
