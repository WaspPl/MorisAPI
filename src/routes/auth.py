from fastapi import APIRouter
import models.DTOS.tokenDTOS as DTO
from scripts.auth import authenticate_user, create_access_token, get_password_hash, get_user
from fastapi import HTTPException, status
from scripts.settings import SettingsDep
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from scripts.database import SessionDep

router = APIRouter(prefix="/token", tags=["auth"])




@router.post("", response_model=DTO.loginResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, settings: SettingsDep):
    
    token_expire_minutes = settings.auth.token_expire_minutes

    authenticatedUser = authenticate_user(form_data.username, form_data.password, session = session)

    if not authenticatedUser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password")
    
    tokenExpireDelta = timedelta(minutes=token_expire_minutes)

    token = create_access_token(data={"sub":form_data.username}, expires_delta=tokenExpireDelta)

    return DTO.loginResponse(token_type="bearer", access_token=token)

