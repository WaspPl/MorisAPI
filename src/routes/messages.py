from fastapi import APIRouter, Depends, HTTPException, status
from scripts.auth import getCurrentUser
from scripts.database import SessionDep
import models.DTOS.messagesDTOS as DTO
from models.databaseModels import Message, Command
from sqlmodel import select

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("", response_model=list[DTO.getMessageResponse])
async def get_messages(session: SessionDep,limit: int = 10, offset: int = 0,currentUser = Depends(getCurrentUser)):
    response = session.exec(select(Message)
                            .where(Message.user_id == currentUser.id)
                            .limit(limit)
                            .offset(offset)
                            .order_by(Message.time_sent.desc())).all()
    return response

@router.post("",response_model=DTO.createMessageResponse,  status_code=status.HTTP_201_CREATED)
async def create_message(newMessage: DTO.createMessageRequest,session: SessionDep,currentUser = Depends(getCurrentUser)):
    command = session.exec(select(Command))
    
    return {"message": "Message created"}