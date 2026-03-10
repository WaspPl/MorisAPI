from fastapi import APIRouter, Depends, status, HTTPException
from scripts.auth import getCurrentUser, getAdmin
from scripts.database import SessionDep, enforceExisting, enforceUnique
import models.DTOS.assignRoleDTOS as DTO
from models.databaseModels import Command_Role_Assignment, Command, Role
from sqlmodel import select

router = APIRouter(prefix="/role_assignments", tags=["role_assignments"])

@router.post("",response_model=DTO.createAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_role_assignment(newAssignment: DTO.createAssignmentRequest,session: SessionDep,user = Depends(getAdmin)):
    enforceExisting(Command, newAssignment.command_id, session)
    enforceExisting(Role, newAssignment.role_id, session)
    
    exisitingAssignment = session.exec(select(Command_Role_Assignment).where(Command_Role_Assignment.command_id == newAssignment.command_id).where(Command_Role_Assignment.role_id == newAssignment.role_id)).first()
    if exisitingAssignment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This assignment already exists")
    
    assignment = Command_Role_Assignment.model_validate(newAssignment)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.delete("/{assignPrompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignPrompt(assignPrompt_id: str,session: SessionDep, user = Depends(getAdmin)):
    assignment = enforceExisting(Command_Role_Assignment, assignPrompt_id, session)

    session.delete(assignment)
    session.commit()
    return
