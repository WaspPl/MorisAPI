from fastapi import APIRouter, Depends, status, HTTPException
from scripts.auth import get_admin
from scripts.database import SessionDep
from scripts.dataValidations import enforce_existing, enforce_unique
import models.DTOS.assignRoleDTOS as DTO
from models.databaseModels import Command_Role_Assignment, Command, Role, User
from sqlmodel import select
from typing import Annotated

router = APIRouter(prefix="/role_assignments", tags=["role_assignments"])

@router.post("",response_model=DTO.createAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_role_assignment(new_assignment: DTO.createAssignmentRequest,session: SessionDep,current_user: Annotated[User, Depends(get_admin)]):
    enforce_existing(Command, new_assignment.command_id, session)
    enforce_existing(Role, new_assignment.role_id, session)
    
    exisitingAssignment = session.exec(select(Command_Role_Assignment).where(Command_Role_Assignment.command_id == new_assignment.command_id).where(Command_Role_Assignment.role_id == new_assignment.role_id)).first()
    if exisitingAssignment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This assignment already exists")
    
    assignment = Command_Role_Assignment.model_validate(new_assignment)
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignPrompt(assignment_id: str,session: SessionDep, current_user:Annotated[User, Depends(get_admin)]):
    assignment = enforce_existing(Command_Role_Assignment, assignment_id, session)
    if assignment.role_id == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail = "You can't unassign the admin")
    session.delete(assignment)
    session.commit()
    return
