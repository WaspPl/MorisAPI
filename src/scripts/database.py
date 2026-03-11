from sqlmodel import create_engine, Session, SQLModel, select, func
from fastapi import Depends, HTTPException, status
from typing import Annotated, TypeVar, Type
from models.databaseModels import User, Role
from scripts.configToObject import SettingsDep, load_settings
from sqlalchemy import event, text
from sqlalchemy.engine import Engine 
import base64
from PIL import Image
from io import BytesIO
import re
import os


settings = load_settings()

DATABASE_URL = settings.storage.database_url

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

db_path = DATABASE_URL.replace("sqlite:///", "")

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    # SET UP REGEX
    def regexp(expr, item):
        reg = re.compile(expr)
        return reg.search(item) is not None
    dbapi_connection.create_function("REGEXP", 2, regexp)


    


def get_session():
    with Session(engine) as session:
        yield session

def populate_tables(session: Session):
    from scripts.auth import getPasswordHash
    if not session.exec(select(Role)).first():
        session.add(Role(id=1,name="admin"))
        session.add(Role(id=2,name="user"))
        session.commit()
    if not session.exec(select(User)).first():
        session.add(User(id=1, username="admin", password=getPasswordHash(settings.auth.default_admin_password), role_id=1, llm_prefix=""))
        session.commit()

def create_db_and_tables():
    db_dir = os.path.dirname(db_path)

    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        populate_tables(session)

    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_user_role_on_delete
            AFTER DELETE ON role
            FOR EACH ROW
            BEGIN
                UPDATE user SET role_id = 2 WHERE role_id = OLD.id;
            END;
        """))
        connection.commit()
    


SessionDep = Annotated[Session, Depends(get_session)]


T = TypeVar("T", bound=SQLModel)

def enforceExisting(tableModel: Type[T], id: int, session: SessionDep) -> T:
    item = session.get(tableModel, id)
    if not item:
        modelName = tableModel.__name__
        raise HTTPException(
            status_code=404,
            detail=f"{modelName} with ID of {id} could not be found")
    return item

def enforceUnique(tableModel: Type[T],tableVariable, newVariable, session: SessionDep,  exclude_id: int = None) -> None:
    statement = select(tableModel).where(tableVariable == newVariable)
    
    if exclude_id is not None:
        statement = statement.where(tableModel.id != exclude_id)

    existingItem = session.exec(statement).first()

    if existingItem:
        columnName = tableVariable.key
        modelName = tableModel.__name__
        
        raise HTTPException(
            status_code=400,
            detail=f"{modelName} with {columnName} '{newVariable}' already exists"
        )
    return

def protectAdminCount(session: SessionDep) -> None:
    admin_count = session.exec(select(func.count(User.id)).where(User.role_id == 1)).one()
    if admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't remove the only admin"
        )
    return

def protectCoreRoles(role_id: int) -> None:
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
        print(base64_string)
        image_bytes = base64.b64decode(base64_string, validate=True)
        
        is_image = (
            image_bytes.startswith(b'\x89PNG') or #png
            image_bytes.startswith(b'\xff\xd8\xff') #jpeg
        )
        
        if not is_image:
            raise ValueError("Not a valid image format")
        print('image')
        return True
    except Exception as e:
        print(e)
        return False
def enforce_base64_image(base64_string: str):
    
        if not is_base64_image(base64_string):
        
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content must be a valid Base64 encoded image (PNG)."
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
   