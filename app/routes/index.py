from fastapi import APIRouter
from starlette.responses import Response

router = APIRouter()

@router.get('/ping')
def ping():
    """ Liveness probe """
    resp = {
        "status" : "pass"
    }
    return Response(resp)


@router.get('/health')
def health():
    """ readiness probe """
    resp = {
        "status" : "pass"
    }
    return Response(resp)
