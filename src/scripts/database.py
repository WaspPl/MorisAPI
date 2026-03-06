from sqlmodel import create_engine, Session, SQLModel, select
from fastapi import Depends
from typing import Annotated
from models.databaseModels import Users, Roles
from scripts.configToObject import loadSettings

DATABASE_URL = "sqlite:///./moris.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

settings = loadSettings('config.yaml')




    


def get_session():
    with Session(engine) as session:
        yield session

def populate_tables(session: Session):
    from scripts.auth import getPasswordHash
    if not session.exec(select(Roles)).first():
        session.add(Roles(id=1,name="admin"))
        session.commit()
    if not session.exec(select(Users)).first():
        session.add(Users(id=1, username="admin", hashed_password=getPasswordHash(settings.auth.default_admin_password), roleId=1))
        session.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        populate_tables(session)


SessionDep = Annotated[Session, Depends(get_session)]
        
