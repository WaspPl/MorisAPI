from fastapi import APIRouter, Depends
import models.DTOS.roleDTOS as DTO
from scripts.database import SessionDep
from scripts.dataValidations import protect_core_roles, enforce_unique, enforce_existing
from models.databaseModels import Role, User
from sqlmodel import asc, desc, select
from scripts.auth import get_current_user, get_admin
from typing import Annotated

router = APIRouter(prefix="/roles", tags=["Role"],)

## GET Role
@router.get("", response_model=list[DTO.GetRoleResponse])
async def get_roles(session: SessionDep, current_user: Annotated[User,Depends(get_current_user)], offset: int = 0, limit: int = 10, descending: bool =True):
    roles = session.exec(select(Role).offset(offset).limit(limit).order_by(desc(Role.id) if descending else asc(Role.id) )).all()
    return roles

## GET ROLE BY ID
@router.get("/{role_id}", response_model=DTO.GetRoleDetailsResponse)
async def get_role(session: SessionDep, role_id: int, current_user: Annotated[User,Depends(get_current_user)]):
    role = enforce_existing(Role, role_id, session)
    return role

## CREATE A ROLE
@router.post("", response_model=DTO.CreateRoleResponse, status_code=201)
async def create_role(new_role: DTO.CreateRoleRequest, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):

    # Check if the role already exists.
    enforce_unique(Role, Role.name, new_role.name, session)
    # Add the role to the DB.
    roleItem = Role.model_validate(new_role)
    session.add(roleItem)
    session.commit()
    session.refresh(roleItem)

    # Return role, response model in the parameters.
    return roleItem

## UPDATE ROLE BY ID
@router.put("/{role_id}", response_model=DTO.UpdateRoleResponse, status_code=200)
async def update_role(role_id: int, new_role: DTO.UpdateRoleRequest, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):
    
    protect_core_roles(role_id)

    foundRole = enforce_existing(Role, role_id, session)   
    enforce_unique(Role, Role.name, new_role.name, session)
    
    roleData = new_role.model_dump(exclude_unset=True)
    foundRole.sqlmodel_update(roleData)

    session.add(foundRole)
    session.commit()
    session.refresh(foundRole)

    return foundRole

## DELETE ROLE BY ID
@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):

    
    protect_core_roles(role_id)

    role = enforce_existing(Role, role_id, session)
    
    session.delete(role)
    session.commit()

    return
