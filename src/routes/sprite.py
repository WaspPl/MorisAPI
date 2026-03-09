from fastapi import APIRouter, Depends, status, HTTPException
from models.DTOS import spriteDTOS as DTO
from models.databaseModels import Sprite
from scripts.database import SessionDep, enforceExisting, enforceUnique, enforce_base64_image
from scripts.auth import getAdmin, getCurrentUser
from sqlmodel import select
import base64

router = APIRouter(prefix="/sprite",tags=["sprite"])

@router.get("", response_model=list[DTO.getSpriteResponse])
def get_sprites(session: SessionDep, limit = 10, offset = 0, currentUser = Depends(getAdmin)):
    result = session.exec(select(Sprite).limit(limit).offset(offset)).all()
    return result

@router.get("/{sprite_id}",response_model=DTO.getSpriteDetailsResponse)
def get_sprite_details(sprite_id: int, session: SessionDep, currentUser = Depends(getAdmin)):
    enforceExisting(Sprite, sprite_id, session)
    result = session.exec(select(Sprite).where(Sprite.id == sprite_id)).first()
    return result

@router.post("", response_model=DTO.createSpriteResponse, status_code=status.HTTP_201_CREATED)
def create_sprite(newSprite: DTO.createSpriteRequest, session: SessionDep, currentUser=Depends(getAdmin)):
    
    enforceUnique(Sprite, Sprite.name, newSprite.name, session)

    enforce_base64_image(newSprite.content)
    
    newItem = Sprite.model_validate(newSprite)
    session.add(newItem)
    session.commit()
    session.refresh(newItem)
    return newItem

@router.put("/{sprite_id}", response_model=DTO.updateSpriteResponse)
def update_sprite(sprite_id: int, newSprite: DTO.updateSpriteRequest, session: SessionDep, currentUser=Depends(getAdmin)):
    oldItem = enforceExisting(Sprite, sprite_id, session)
    enforceUnique(Sprite, Sprite.name, newSprite.name, session, sprite_id)

    
    enforce_base64_image(newSprite.content)

    itemDump = newSprite.model_dump()
    updatedItem = oldItem.sqlmodel_update(itemDump)
    
    session.add(updatedItem)
    session.commit()
    session.refresh(updatedItem)

    return updatedItem

@router.delete("/{sprite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sprite(sprite_id: int, session: SessionDep, currentUser=Depends(getAdmin)):
    item = enforceExisting(Sprite, sprite_id, session)

    session.delete(item)
    session.commit()
    return


