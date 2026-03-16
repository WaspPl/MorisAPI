import base64
from PIL import Image
from io import BytesIO
from typing import TypeVar, Type
from sqlmodel import SQLModel, select, func
from fastapi import HTTPException, status
from scripts.database import SessionDep
from models.databaseModels import User
import logging

T = TypeVar("T", bound=SQLModel)

def enforce_existing(table_model: Type[T], id: int, session: SessionDep) -> T:
    item = session.get(table_model, id)
    if not item:
        modelName = table_model.__name__
        raise HTTPException(
            status_code=404,
            detail=f"{modelName} with ID of {id} could not be found")
    return item

def enforce_unique(table_model: Type[T],table_variable, new_variable, session: SessionDep,  exclude_id: int = None) -> None:
    statement = select(table_model).where(table_variable == new_variable)
    
    if exclude_id is not None:
        statement = statement.where(table_model.id != exclude_id)

    existingItem = session.exec(statement).first()

    if existingItem:
        columnName = table_variable.key
        modelName = table_model.__name__
        
        raise HTTPException(
            status_code=400,
            detail=f"{modelName} with {columnName} '{new_variable}' already exists"
        )
    return

def protect_admin_count(session: SessionDep) -> None:
    admin_count = session.exec(select(func.count(User.id)).where(User.role_id == 1)).one()
    if admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't remove the only admin"
        )
    return

def protect_core_roles(role_id: int) -> None:
    if role_id in [1,2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Role Admin and User are core to the system and thus cannot be modified"
        )
    return    

def is_base64_image(base64_string: str) -> bool:
    base64_string = base64_string.strip()
    if "," in base64_string:
            base64_string = base64_string.split(",")[1]
    try:
        image_bytes = base64.b64decode(base64_string, validate=True)
        
        is_image = (
            image_bytes.startswith(b'\x89PNG') or #png
            image_bytes.startswith(b'\xff\xd8\xff') #jpeg
        )
        
        if not is_image:
            return False
        return True
    except Exception:
        return False
def enforce_base64_image(base64_string: str):
    
        if not is_base64_image(base64_string):
        
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content must be a valid Base64 encoded image (PNG, JPEG)."
            )
        
def enforce_base64_image_size(base64_string: str, height: int, width: int, is_witdth_factor: bool = True):
    if "," in base64_string:
        b64_string = base64_string.split(",")[1]
    imgData = base64.b64decode(b64_string)
    img = Image.open(BytesIO(imgData))
    imgWidth, imgHeight = img.size

    if imgHeight != height:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Sprite must have a height of {height}px")
    if is_witdth_factor and imgWidth % width != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Sprite must have a width divisible by {width}")
    if not is_witdth_factor and imgWidth != width:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Sprite must have a width of {width}px")
   