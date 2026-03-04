from fastapi import APIRouter
import models.DTOS.authDTOS as DTO
from scripts.auth import authenticateUser, createAccessToken, getPasswordHash, getUser
from fastapi import HTTPException, status
from scripts.configToObject import loadSettings
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from scripts.database import SessionDep
from models.databaseModels import Users

router = APIRouter(prefix="/auth", tags=["auth"])

settings = loadSettings("config.yaml")

token_expire_minutes = settings.auth.token_expire_minutes

@router.post("/login", response_model=DTO.loginResponse)
async def login(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    
    authenticatedUser = authenticateUser(formData.username, formData.password, session = session)

    if not authenticatedUser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password")
    
    tokenExpireDelta = timedelta(minutes=token_expire_minutes)

    token = createAccessToken(data={"sub":formData.username}, expiresDelta=tokenExpireDelta)

    return {"token": token}

@router.post("/register", response_model=DTO.registerResponse)
async def register(formData: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    existingUser = getUser(formData.username, session)
    if existingUser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with that username already exists")
    
    if not formData.username or not formData.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    passwordHash = getPasswordHash(formData.password)
    
    userModel = Users(username=formData.username, hashed_password=passwordHash, roleId=1)

    userItem = Users.model_validate(userModel)
    session.add(userItem)
    session.commit()
    session.refresh(userItem)

    return userItem