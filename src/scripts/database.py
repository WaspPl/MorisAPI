from sqlmodel import create_engine, Session, SQLModel, select, func
from fastapi import Depends
from typing import Annotated
from models.databaseModels import User, Role
from scripts.settings import load_settings
from sqlalchemy import event, text
from sqlalchemy.engine import Engine 
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

