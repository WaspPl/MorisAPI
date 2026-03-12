from fastapi import APIRouter, Depends, status, HTTPException
from scripts.auth import getCurrentUser, getPasswordHash, createAccessToken
from scripts.database import SessionDep
from scripts.dataValidations import protectAdminCount, enforceUnique, enforceExisting
from models.databaseModels import User, Role
from typing import Annotated
import models.DTOS.meDTOS as DTO
from scripts.configToObject import SettingsDep

router = APIRouter(prefix="/me", tags=["me"])

@router.get("", response_model= DTO.getMeResponse)
async def get_active_user(currentUser: Annotated[User, Depends(getCurrentUser)]):
    return currentUser

@router.put("", response_model=DTO.updateMeResponse)
async def update_current_user(newUser: DTO.updateMeRequest, currentUser: Annotated[User, Depends(getCurrentUser)], session: SessionDep, settings: SettingsDep):
    
    enforceExisting(Role, newUser.role_id, session)

    if newUser.role_id != currentUser.role_id:
        if currentUser.role_id != 1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You don't have permission to change your own role.")
        else:
            protectAdminCount(session)

    

    enforceUnique(User, User.username, newUser.username, session, currentUser.id)
    
    userData = newUser.model_dump(exclude_unset=True)
    if "password" in userData and userData["password"]:
        userData["password"] = getPasswordHash(userData["password"])

    currentUser.sqlmodel_update(userData)

    session.add(currentUser)
    session.commit()
    session.refresh(currentUser)

    token = createAccessToken(data={"sub":currentUser.username})


    response = {
        **currentUser.model_dump(),
        'role' : currentUser.role.__dict__,
        'access_token' : token,
        'token_type' : 'bearer'

    }

    return DTO.updateMeResponse.model_validate(response)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(currentUser: Annotated[User, Depends(getCurrentUser)], session: SessionDep):
    protectAdminCount(session)
    session.delete(currentUser)
    session.commit()
    return