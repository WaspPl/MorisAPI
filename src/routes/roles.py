from fastapi import APIRouter, Depends, HTTPException, status
import models.DTOS.roleDTOS as DTO
from scripts.database import SessionDep, protectCoreRoles, enforceUnique, enforceExisting
from models.databaseModels import Role
from sqlmodel import select
from scripts.auth import getCurrentUser, getAdmin

router = APIRouter(prefix="/Role", tags=["Role"],)

## GET Role
@router.get("", response_model=list[DTO.GetRoleResponse])
async def get_Role(session: SessionDep, offset: int = 0, limit: int = 10, currentUser = Depends(getCurrentUser)):
    Role = session.exec(select(Role).offset(offset).limit(limit)).all()
    return Role

## GET ROLE BY ID
@router.get("/{role_id}", response_model=DTO.GetRoleResponse)
async def get_role(session: SessionDep, role_id: int, currentUser = Depends(getAdmin)):
    role = enforceExisting(Role, role_id, session)
    return role

## CREATE A ROLE
@router.post("", response_model=DTO.CreateRoleResponse, status_code=201)
async def create_role(role: DTO.CreateRoleRequest, session: SessionDep, currentUser = Depends(getAdmin)):

    # Check if the role already exists.
    enforceUnique(Role, Role.name, role.name, session)
    # Add the role to the DB.
    roleItem = Role.model_validate(role)
    session.add(roleItem)
    session.commit()
    session.refresh(roleItem)

    # Return role, response model in the parameters.
    return roleItem

## UPDATE ROLE BY ID
@router.put("/{role_id}", response_model=DTO.UpdateRoleResponse, status_code=200)
async def update_role(role_id: int, role: DTO.UpdateRoleRequest, session: SessionDep, currentUser = Depends(getAdmin)):
    
    protectCoreRoles(role_id)

    foundRole = enforceExisting(Role, role_id, session)   
    enforceUnique(Role, Role.name, role.name, session)
    
    roleData = role.model_dump(exclude_unset=True)
    foundRole.sqlmodel_update(roleData)

    session.add(foundRole)
    session.commit()
    session.refresh(foundRole)

    return foundRole

## DELETE ROLE BY ID
@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, session: SessionDep, currentUser = Depends(getAdmin)):

    
    protectCoreRoles(role_id)

    role = enforceExisting(Role, role_id, session)
    
    session.delete(role)
    session.commit()

    return
