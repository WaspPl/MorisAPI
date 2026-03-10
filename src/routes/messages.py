from fastapi import APIRouter, Depends, HTTPException, status
from scripts.auth import getCurrentUser
from scripts.database import SessionDep
import models.DTOS.messagesDTOS as DTO
from models.databaseModels import Message, Command, Command_Role_Assignment, User, Prompt, Sprite
from sqlmodel import select, desc, asc
from typing import Annotated
from scripts.configToObject import SettingsDep
from scripts.messageScripts import getLLMResponse, executeCommand, sendDataToDisplays
from asyncio import create_task, sleep
from datetime import datetime, timezone

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

    # get a command that satisfies requirements
    command = session.exec(select(Command)
                           .join(Command_Role_Assignment)
                           .join(Prompt)
                           .where(Command_Role_Assignment.role_id == currentUser.role_id)
                           .where(Prompt.text == newMessage.content)).first()
    
    # get settings depending on if the command was found or not
    defaultCommand = Command(id = None,
                             llm_prefix="",
                            sprite_repeat_times=1,
                            sprite= Sprite(content=""),
                            is_output_llm=True)
    activeCommand = command or defaultCommand
    print(activeCommand)

    prefix = activeCommand.llm_prefix
    content = await executeCommand() if command else ""
    sprite = activeCommand.sprite.content if activeCommand.sprite else ""
    spriteRepeatTimes = activeCommand.sprite_repeat_times
    llmOutput = activeCommand.is_output_llm

    # if llmOutput is True send data to an llm
    if llmOutput:
        textResponse = await getLLMResponse(content)
    else: 
        textResponse = content

    if settings.display.enabled:
        create_task(sendDataToDisplays())
    
    userMessage = Message(user_id=currentUser.id,
                      is_users=True,
                      content= newMessage.content,
                      time_sent= sentTime)
    responseMessage = Message(user_id=currentUser.id,
                              is_users=False,
                              content=textResponse,
                              executed_command_id=activeCommand.id)

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