from fastapi import APIRouter, Depends, HTTPException
import models.DTOS.rolesDTOS as DTO
from scripts.database import get_session, SessionDep
from models.databaseModels import Roles
from sqlmodel import select


router = APIRouter(prefix="/roles", tags=["roles"])

## GET ROLES
@router.get("", response_model=list[DTO.GetRoleResponse])
async def get_roles(session: SessionDep, offset: int = 0, limit: int = 100):
    roles = session.exec(select(Roles).offset(offset).limit(limit)).all()
    return roles

## GET ROLE BY ID
@router.get("/{role_id}", response_model=DTO.GetRoleResponse)
async def get_role(session: SessionDep, role_id: str):
    role = session.get(Roles, role_id)
    if not role:
        raise HTTPException(
            status_code=404, 
            detail=f"A role with an id of '{role_id}' does not exist"
            )
    return role

## CREATE A ROLE
@router.post("", response_model=DTO.CreateRoleResponse, status_code=201)
async def create_role(role: DTO.CreateRoleRequest, session: SessionDep):

    # Check if the role already exists.
    existingRecord = session.exec(select(Roles).where(Roles.name == role.name)).first()
    if existingRecord:
        raise HTTPException(
            status_code=400,
            detail=f"A role with the name of '{role.name}' already exists"
            )
    
    # Add the role to the DB.
    roleItem = Roles.model_validate(role)
    session.add(roleItem)
    session.commit()
    session.refresh(roleItem)

    # Return role, response model in the parameters.
    return roleItem

## UPDATE ROLE BY ID
@router.put("/{role_id}", response_model=DTO.UpdateRoleResponse, status_code=200)
async def update_role(role_id: str, role: DTO.UpdateRoleRequest, session: SessionDep):
    foundRole = session.get(Roles, role_id)

    if not foundRole:
        raise HTTPException(
            status_code=404,
            detail=f"A role with the Id of '{role_id}' could not be found"
        )
    
    roleData = role.model_dump(exclude_unset=True)
    foundRole.sqlmodel_update(roleData)

    session.add(foundRole)
    session.commit()
    session.refresh(foundRole)

    return foundRole

## DELETE ROLE BY ID
@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: str, session: SessionDep):
    role = session.get(Roles, role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail=f"A role with the Id of '{role_id}' could not be found")
    
    session.delete(role)
    session.commit()

    return
