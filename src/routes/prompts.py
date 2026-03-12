from fastapi import APIRouter, Depends, status
from scripts.auth import get_current_user, get_admin
from scripts.database import SessionDep
from scripts.dataValidations import  enforce_existing, enforce_unique
import models.DTOS.promptDTOS as DTO
from sqlmodel import select
from models.databaseModels import Prompt, Command


router = APIRouter(prefix="/prompts", tags=["prompts"],)

# region unnecessary
# Commented methods i deemed unnecessary, but want to keep them in case they turn out to be needed after all
# As of now i feel like we only need to create or remove a prompt
# Retrieval is done through /commands and updating makes no sense considering how simple it is


# @router.get("", response_model=list[DTO.getPromptResponse])
# async def get_prompts(session: SessionDep, current_user = Depends(get_current_user)):
#     return 

# @router.get("/{prompt_id}",response_model=DTO.getPromptDetailsResponse)
# async def get_prompt(prompt_id: str, session: SessionDep, current_user = Depends(get_current_user)):
#     return {"message": f"Prompt with ID {prompt_id}"}
# endregion
@router.post("", response_model=DTO.createPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(new_prompt: DTO.createPromptRequest, session: SessionDep, current_user = Depends(get_admin)):
    enforce_existing(Command, new_prompt.command_id, session)
    enforce_unique(Prompt, Prompt.text, new_prompt.text, session)

    promptValidated = Prompt.model_validate(new_prompt)
    session.add(promptValidated)
    session.commit()
    session.refresh(promptValidated)
    return promptValidated

# @router.put("/{prompt_id}", response_model=DTO.updatePromptResponse)
# async def update_prompt(prompt_id: str, new_prompt: DTO.updatePromptRequest, current_user = Depends(get_admin)):
#     return {"message": f"Prompt with ID {prompt_id} updated"}

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str, session: SessionDep, current_user = Depends(get_admin)):
    prompt = enforce_existing(Prompt, prompt_id, session)

    session.delete(prompt)
    session.commit()
    return 