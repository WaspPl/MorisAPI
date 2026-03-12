import asyncio
from pathlib import Path
from fastapi import HTTPException, status
import subprocess
from scripts.database import SessionDep
from sqlmodel import select, desc
from models.databaseModels import Message, Command, User
from scripts.configToObject import SettingsDep
import requests
import json
from scripts.dataValidations import enforce_base64_image


async def executeCommand(script_path: Path, arguments) -> str:
    if not script_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script file not found."
        )
    try:
        result = subprocess.run(
            ["python", str(script_path), json.dumps(arguments)],
            capture_output=True,
            text=True,
            check=True
            )
        return result.stdout

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Script crashed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error: {str(e)}"
        )

def buildLLMQuery(session: SessionDep, user_id: int, previous_messages_count: int, newMessage: str, user_prefix: str) -> list[dict]:
    previousMessages = session.exec(select(Message)
                                    .where(Message.user_id == user_id)
                                    .limit(previous_messages_count)
                                    .order_by(desc(Message.time_sent))).all()

    systemQuery = {'role': 'system', 'content': user_prefix}
    messagesQuery = [{'role': 'user' if message.is_users else 'assistant', 'content': message.content} for message in previousMessages.__reversed__()]
    newMessageQuery = {'role': 'user', 'content': newMessage}
    return [systemQuery] + messagesQuery + [newMessageQuery]

async def getLLMResponse(messages: list[dict], settings: SettingsDep) -> str:
    url = settings.LLM.api_url
    headers = {
        "Authorization": f"Bearer {settings.LLM.auth_token}",
        "Content-Type": "application/json"
    }
    data = {
        "model": settings.LLM.model,
        "messages": messages,
        "verbosity": settings.LLM.verbosity
    }
    try: 
        response = requests.post(url,headers=headers,json=data)
    except:
        return "There was an error connecting to the LLM."
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    else:
        return f"Error: {response.status_code}, Details: {response._content}"

async def sendDataToDisplays(settings: SettingsDep, text: str = "", sprite_base64: str = "", sprite_repeat_times: int = 1) -> None:
    # This function is made to work with MALDC, but can be changed without any major effect on the rest of the program
    
    url = settings.display.api_url

    data = {
        "message": text,
        "spriteBase64": sprite_base64,
        "spriteReplayTimes": sprite_repeat_times
    }
    
    requests.post(url, json=data)
    return

async def getResponseFromTextMessage(newMessageText: str, session: SessionDep, currentUser: User, settings: SettingsDep, command: Command, command_arguments = None) -> str:
    response = ""
    if command and command.script_path:
        response = await executeCommand(Path(command.script_path), command_arguments)
    # if llmOutput is True send data to an llm
    if command.is_output_llm:
        LLMQuery = buildLLMQuery(session, currentUser.id, settings.LLM.previous_messages_sent, newMessageText, currentUser.llm_prefix)
        response = await getLLMResponse(LLMQuery, settings)
    
    return response

async def getResponseFromImageMessage(image_base64: str) -> str:
    enforce_base64_image(image_base64)
    return "I got an image but don't have my code prepared for it yet"