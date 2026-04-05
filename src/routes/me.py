from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException
from scripts.auth import create_refresh_token, get_current_user, get_password_hash, create_access_token
from scripts.database import SessionDep
from scripts.dataValidations import protect_admin_count, enforce_unique, enforce_existing
from models.databaseModels import User, Role
from typing import Annotated
import models.DTOS.meDTOS as DTO
from scripts.settings import SettingsDep

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model= DTO.getMeResponse)
async def get_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.put("", response_model=DTO.updateMeResponse)
async def update_current_user(new_user: DTO.updateMeRequest, current_user: Annotated[User, Depends(get_current_user)], session: SessionDep, settings: SettingsDep):
    
    enforce_existing(Role, new_user.role_id, session)

    if (new_user.role_id != current_user.role_id):
        if current_user.role_id != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You don't have permission to change your own role.")
        else:
            protect_admin_count(session)
    if new_user.token_duration_minutes != current_user.token_duration_minutes and current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You don't have permission to change token duration.")

    

    enforce_unique(User, User.username, new_user.username, session, current_user.id)
    
    userData = new_user.model_dump(exclude_unset=True)
    if "password" in userData and userData["password"]:
        userData["password"] = get_password_hash(userData["password"])

    current_user.sqlmodel_update(userData)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    access_token = create_access_token(data={"sub":current_user.username}, expires_delta=timedelta(days = settings.auth.refresh_token_duration_days))
    refresh_token = create_refresh_token(data={"sub":current_user.username}, expires_delta=timedelta(minutes= current_user.access_token_duration_minutes))

    response = {
        **current_user.model_dump(),
        'role' : current_user.role.__dict__,
        'access_token' : access_token,
        'refresh_token': refresh_token,
        'refresh_token_duration_days': current_user.access_token_duration_minutes,
        'access_token_duration_minutes': current_user.access_token_duration_minutes,
        'token_type' : 'bearer'

    }

    return DTO.updateMeResponse.model_validate(response)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    protect_admin_count(session)
    session.delete(current_user)
    session.commit()
    return