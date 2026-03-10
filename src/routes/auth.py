from fastapi import APIRouter
import models.DTOS.tokenDTOS as DTO
from scripts.auth import authenticateUser, createAccessToken, getPasswordHash, getUser
from fastapi import HTTPException, status
from scripts.configToObject import SettingsDep
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from scripts.database import SessionDep
from models.databaseModels import User

router = APIRouter(prefix="/token", tags=["auth"])




@router.post("", response_model=DTO.loginResponse)
async def login(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep, settings: SettingsDep):
    
    token_expire_minutes = settings.auth.token_expire_minutes

    authenticatedUser = authenticateUser(formData.username, formData.password, session = session)

    if not authenticatedUser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password")
    
    tokenExpireDelta = timedelta(minutes=token_expire_minutes)

    token = createAccessToken(data={"sub":formData.username}, expiresDelta=tokenExpireDelta)

    return DTO.loginResponse(token_type="bearer", access_token=token)

