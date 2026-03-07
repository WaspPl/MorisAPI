from sqlmodel import create_engine, Session, SQLModel, select, func
from fastapi import Depends, HTTPException, status
from typing import Annotated
from models.databaseModels import User, Role
from scripts.configToObject import loadSettings
from sqlalchemy import event, text
from sqlalchemy.engine import Engine 

DATABASE_URL = "sqlite:///./moris.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

settings = loadSettings('config.yaml')

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


    


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
        session.add(User(id=1, username="admin", hashed_password=getPasswordHash(settings.auth.default_admin_password), roleId=1))
        session.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        populate_tables(session)

    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_user_role_on_delete
            AFTER DELETE ON role
            FOR EACH ROW
            BEGIN
                UPDATE user SET roleId = 2 WHERE roleId = OLD.id;
            END;
        """))
        connection.commit()
    


SessionDep = Annotated[Session, Depends(get_session)]

def enforceExisting(tableModel, id: int, session: SessionDep):
    item = session.get(tableModel, id)
    if not item:
        modelName = tableModel.__name__
        raise HTTPException(
            status_code=404,
            detail=f"{modelName} with ID of {id} could not be found")
    return item

def enforceUnique(tableModel,tableVariable, newVariable, session: SessionDep):
    existingItem = session.exec(select(tableModel).where(tableVariable == newVariable)).first()

    if existingItem:
        columnName = tableVariable.key
        modelName = tableModel.__name__
        
        raise HTTPException(
            status_code=400,
            detail=f"{modelName} with {columnName} '{newVariable}' already exists"
        )
    return

def protectAdminCount(session: SessionDep):
    admin_count = session.exec(select(func.count(User.id)).where(User.roleId == 1)).one()
    if admin_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't remove the only admin"
        )
    return

def protectCoreRoles(role_id: int):
    if role_id in [1,2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Role Admin and User are core to the system and thus cannot be modified"
        )
    return    
