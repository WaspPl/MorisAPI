from fastapi import APIRouter
import jwt
from sqlmodel import select
import models.DTOS.tokenDTOS as DTO
from models.databaseModels import RefreshTokens
from scripts.auth import authenticate_user, create_access_token, create_refresh_token, get_password_hash, get_user, validate_refresh_token
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
    
    user = authenticate_user(form_data.username, form_data.password, session = session)
    

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong login or password")
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=user.access_token_duration_minutes)
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(days=settings.auth.refresh_token_duration_days), 
        session=session, 
        user_id=user.id
    )

    return DTO.loginResponse(
        access_token=access_token, 
        refresh_token=new_refresh_token,
        token_type="bearer",
        refresh_token_duration_days=settings.auth.refresh_token_duration_days,
        access_token_duration_minutes=user.access_token_duration_minutes
        
    )
@router.post("/refresh", response_model=DTO.loginResponse)
async def refresh_access_token(refresh_token: str, session: SessionDep, settings: SettingsDep):

    user, db_token_entry = validate_refresh_token(refresh_token, session)    
    session.delete(db_token_entry)
    session.commit()
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=user.access_token_duration_minutes)
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(days=settings.auth.refresh_token_duration_days), 
        session=session, 
        user_id=user.id
    )

    return DTO.loginResponse(
        access_token=access_token, 
        refresh_token=new_refresh_token,
        token_type="bearer",
        refresh_token_duration_days=settings.auth.refresh_token_duration_days,
        access_token_duration_minutes=user.access_token_duration_minutes
    )

@router.post("/logout")
async def logout(refresh_token: str, session: SessionDep):
    user, hashed_token = validate_refresh_token(refresh_token, session)

    session.delete(hashed_token)
    session.commit()
    return {"detail": "Logged out successfully"}
