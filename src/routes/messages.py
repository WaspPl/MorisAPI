from fastapi import APIRouter, Depends, HTTPException, status
from scripts.auth import getCurrentUser
from scripts.database import SessionDep
from scripts.dataValidations import is_base64_image, enforce_base64_image
import models.DTOS.messagesDTOS as DTO
from models.databaseModels import Message, Command, Command_Role_Assignment, User, Prompt, Sprite
from sqlmodel import select, desc, asc, literal, func, delete
from typing import Annotated
from scripts.configToObject import SettingsDep
from scripts.messageScripts import getLLMResponse, executeCommand, sendDataToDisplays, buildLLMQuery, getResponseFromImageMessage, getResponseFromTextMessage
from asyncio import create_task
from datetime import datetime, timezone
from pathlib import Path
import re

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("", response_model=list[DTO.getMessageResponse])
async def get_messages(session: SessionDep,limit: int = 10, offset: int = 0,currentUser = Depends(getCurrentUser)):
    response = session.exec(select(Message)
                            .where(Message.user_id == currentUser.id)
                            .limit(limit)
                            .offset(offset)
                            .order_by(desc(Message.time_sent))).all()
    return response

@router.post("",response_model=DTO.createMessageResponse,  status_code=status.HTTP_201_CREATED)
async def create_message(newMessage: DTO.createMessageRequest,session: SessionDep,settings: SettingsDep, currentUser: Annotated[User,Depends(getCurrentUser)]):

    sentTime = datetime.now(timezone.utc).replace(microsecond=0)
    defaultCommand = Command(id = None,
                                    llm_prefix="",
                                    sprite_repeat_times=1,
                                    sprite= Sprite(content=""),
                                    script_path="",
                                    is_output_llm=True)
    
    if newMessage.type == "text":
        # get a command that satisfies requirements
        result = session.exec(select(Command, Prompt.text)
                            .join(Command_Role_Assignment)
                            .join(Prompt)
                            .where(Command_Role_Assignment.role_id == currentUser.role_id)
                            .where(literal(newMessage.content).op('REGEXP')(Prompt.text))
                            .order_by(func.char_length(Prompt.text).desc())).first()
        if result:
            command, prompt_pattern = result
            match = re.search(prompt_pattern, newMessage.content)
            if match:
                arguments = match.groupdict()
        # get settings depending on if the command was found or not
        
        activeCommand = command if result else defaultCommand
        textResponse = await getResponseFromTextMessage(newMessage.content, session, currentUser, settings, activeCommand, arguments)

    elif newMessage.type == "imgBase64":
        activeCommand = defaultCommand
        textResponse = await getResponseFromImageMessage()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unsupported message type")

    if settings.display.enabled and newMessage.send_to_displays:
        create_task(sendDataToDisplays(settings=settings, 
                                       text=textResponse, 
                                       sprite_base64=activeCommand.sprite.content, 
                                       sprite_repeat_times=activeCommand.sprite_repeat_times))
    
    userMessage = Message(user_id=currentUser.id,
                    is_users=True,
                    content= newMessage.content,
                    time_sent= sentTime,
                    type = newMessage.type)
    responseMessage = Message(user_id=currentUser.id,
                            is_users=False,
                            content=textResponse,
                            executed_command_id=activeCommand.id,
                            type = 'imgBase64' if is_base64_image(textResponse) else 'text')

    session.add(userMessage)
    session.add(responseMessage)
    session.commit()
    session.refresh(userMessage)
    session.refresh(responseMessage)

    userMessageData = userMessage.model_dump()
    responseMessageData = responseMessage.model_dump()
    if responseMessage.executed_command:
        responseMessageData["executed_command"] = responseMessage.executed_command.model_dump()
        
    return DTO.createMessageResponse(
        user=DTO.getMessageResponse.model_validate(userMessageData),
        response=DTO.getMessageResponse.model_validate(responseMessageData)
    )

@router.delete("/all", status_code=status.HTTP_204_NO_CONTENT)
async def remove_all_users_messages(session: SessionDep, currentUser: Annotated[User, Depends(getCurrentUser)]):
    session.exec(delete(Message)
                 .where(Message.user_id == currentUser.id))
    session.commit()
    return