from fastapi import APIRouter, Depends, HTTPException, status
from scripts.auth import get_current_user
from scripts.database import SessionDep
from scripts.dataValidations import is_base64_image
import models.DTOS.messagesDTOS as DTO
from models.databaseModels import Message, Command, Command_Role_Assignment, User, Prompt, Sprite
from sqlmodel import select, desc, literal, func, delete
from typing import Annotated
from scripts.settings import SettingsDep
from scripts.messageScripts import get_LLM_response, execute_command, send_data_to_displays, build_LLM_query, get_response_from_image_message, get_response_from_text_message
from asyncio import create_task
from datetime import datetime, timezone
from typing import Annotated
import re

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("", response_model=list[DTO.getMessageResponse])
async def get_messages(session: SessionDep, current_user: Annotated[User, Depends(get_current_user)],limit: int = 10, offset: int = 0):
    response = session.exec(select(Message)
                            .where(Message.user_id == current_user.id)
                            .limit(limit)
                            .offset(offset)
                            .order_by(desc(Message.time_sent))).all()
    return response

@router.post("",response_model=DTO.createMessageResponse,  status_code=status.HTTP_201_CREATED)
async def create_message(new_message: DTO.createMessageRequest,session: SessionDep,settings: SettingsDep, current_user: Annotated[User,Depends(get_current_user)]):
    arguments = ""
    sentTime = datetime.now(timezone.utc).replace(microsecond=0)
    defaultCommand = Command(id = None,
                                    llm_prefix="",
                                    sprite_repeat_times=1,
                                    sprite= Sprite(content=""),
                                    script_path="",
                                    is_output_llm=True)
    
    if new_message.type == "text":
        # get a command that satisfies requirements
        result = session.exec(select(Command, Prompt.text)
                            .join(Command_Role_Assignment)
                            .join(Prompt)
                            .where(Command_Role_Assignment.role_id == current_user.role_id)
                            .where(literal(new_message.content).op('REGEXP')(Prompt.text))
                            .order_by(func.char_length(Prompt.text).desc())).first()
        if result:
            command, prompt_pattern = result
            match = re.search(prompt_pattern, new_message.content)
            if match:
                arguments = match.groupdict()
        # get settings depending on if the command was found or not
        
        activeCommand = command if result else defaultCommand
        textResponse = await get_response_from_text_message(new_message.content, session, current_user, settings, activeCommand, arguments)

    elif new_message.type == "imgBase64":
        activeCommand = defaultCommand
        textResponse = await get_response_from_image_message()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Unsupported message type")

    if settings.display.enabled and new_message.send_to_displays:
        create_task(send_data_to_displays(settings=settings, 
                                       text=textResponse, 
                                       sprite_base64=activeCommand.sprite.content if activeCommand.sprite else None, 
                                       sprite_repeat_times=activeCommand.sprite_repeat_times if activeCommand.sprite else None))
    
    userMessage = Message(user_id=current_user.id,
                    is_users=True,
                    content= new_message.content,
                    time_sent= sentTime,
                    type = new_message.type)
    responseMessage = Message(user_id=current_user.id,
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
async def remove_all_users_messages(session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    session.exec(delete(Message)
                 .where(Message.user_id == current_user.id))
    session.commit()
    return