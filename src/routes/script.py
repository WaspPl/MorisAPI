from fastapi import APIRouter

router = APIRouter(prefix="/scripts", tags=["script"])

@router.get("")
def get_scripts():
    return