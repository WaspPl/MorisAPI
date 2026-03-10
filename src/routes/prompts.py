from fastapi import APIRouter, Depends, status
from scripts.auth import getCurrentUser, getAdmin
from scripts.database import enforceExisting, enforceUnique, SessionDep
import models.DTOS.promptDTOS as DTO
from sqlmodel import select
from models.databaseModels import Prompt, Command


router = APIRouter(prefix="/prompts", tags=["prompts"], dependencies= [Depends(getCurrentUser)],)

# region unnecessary
# Commented methods i deemed unnecessary, but want to keep them in case they turn out to be needed after all
# As of now i feel like we only need to create or remove a prompt
# Retrieval is done through /commands and updating makes no sense considering how simple it is


# @router.get("", response_model=list[DTO.getPromptResponse])
# async def get_prompts(session: SessionDep, currentUser = Depends(getCurrentUser)):
#     return 

# @router.get("/{prompt_id}",response_model=DTO.getPromptDetailsResponse)
# async def get_prompt(prompt_id: str, session: SessionDep, currentUser = Depends(getCurrentUser)):
#     return {"message": f"Prompt with ID {prompt_id}"}
# endregion
@router.post("", response_model=DTO.createPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(newPrompt: DTO.createPromptRequest, session: SessionDep, currentUser = Depends(getAdmin)):
    enforceExisting(Command, newPrompt.command_id, session)
    enforceUnique(Prompt, Prompt.text, newPrompt.text, session)

    promptValidated = Prompt.model_validate(newPrompt)
    session.add(promptValidated)
    session.commit()
    session.refresh(promptValidated)
    return promptValidated

# @router.put("/{prompt_id}", response_model=DTO.updatePromptResponse)
# async def update_prompt(prompt_id: str, newPrompt: DTO.updatePromptRequest, currentUser = Depends(getAdmin)):
#     return {"message": f"Prompt with ID {prompt_id} updated"}

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str, session: SessionDep, currentUser = Depends(getAdmin)):
    prompt = enforceExisting(Prompt, prompt_id, session)

    session.delete(prompt)
    session.commit()
    return 