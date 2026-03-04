from sqlmodel import create_engine, Session, SQLModel
from fastapi import Depends
from typing import Annotated


DATABASE_URL = "sqlite:///./moris.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
        
