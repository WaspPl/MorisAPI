from fastapi import APIRouter, Depends, status, HTTPException
from models.DTOS import spriteDTOS as DTO
from models.databaseModels import Sprite, User
from scripts.database import SessionDep
from scripts.dataValidations import enforce_existing, enforce_unique, enforce_base64_image,  enforce_base64_image_size
from scripts.auth import get_admin, get_current_user
from sqlmodel import select
from scripts.settings import SettingsDep
from typing import Annotated

router = APIRouter(prefix="/sprites",tags=["sprite"])

@router.get("", response_model=list[DTO.getSpriteResponse])
async def get_sprites(session: SessionDep,current_user: Annotated[User,Depends(get_current_user)], limit = 10, offset = 0):
    result = session.exec(select(Sprite).limit(limit).offset(offset)).all()
    return result

@router.get("/{sprite_id}",response_model=DTO.getSpriteDetailsResponse)
async def get_sprite_details(sprite_id: int, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]):
    enforce_existing(Sprite, sprite_id, session)
    result = session.exec(select(Sprite).where(Sprite.id == sprite_id)).first()
    return result

@router.post("", response_model=DTO.createSpriteResponse, status_code=status.HTTP_201_CREATED)
async def create_sprite(new_sprite: DTO.createSpriteRequest, session: SessionDep, settings: SettingsDep, current_user: Annotated[User,Depends(get_admin)]):
    
    enforce_unique(Sprite, Sprite.name, new_sprite.name, session)

    enforce_base64_image(new_sprite.content)
    enforce_base64_image_size(new_sprite.content, settings.display.sprite_height, settings.display.sprite_width, True)
    new_sprite.content = new_sprite.content.split(",")[1] if "," in new_sprite.content else new_sprite.content
    newItem = Sprite.model_validate(new_sprite)
    session.add(newItem)
    session.commit()
    session.refresh(newItem)
    return newItem

@router.put("/{sprite_id}", response_model=DTO.updateSpriteResponse)
async def update_sprite(sprite_id: int, new_sprite: DTO.updateSpriteRequest, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):
    oldItem = enforce_existing(Sprite, sprite_id, session)
    enforce_unique(Sprite, Sprite.name, new_sprite.name, session, sprite_id)

    
    enforce_base64_image(new_sprite.content)
    new_sprite.content = new_sprite.content.split(",")[1] if "," in new_sprite.content else new_sprite.content
    itemDump = new_sprite.model_dump()
    updatedItem = oldItem.sqlmodel_update(itemDump)
    
    session.add(updatedItem)
    session.commit()
    session.refresh(updatedItem)

    return updatedItem

@router.delete("/{sprite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprite(sprite_id: int, session: SessionDep, current_user: Annotated[User,Depends(get_admin)]):
    item = enforce_existing(Sprite, sprite_id, session)

    session.delete(item)
    session.commit()
    return


