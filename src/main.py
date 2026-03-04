import uvicorn
from app import app
from scripts.configToObject import loadSettings
from scripts.database import engine, create_db_and_tables
import models.databaseModels

settings = loadSettings("config.yaml")

if __name__ == "__main__":    
        create_db_and_tables()
        uvicorn.run("main:app", host=settings.api.host, port=settings.api.port, reload=True) # type: ignore