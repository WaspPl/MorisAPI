import uvicorn
from app import app
from scripts.configToObject import loadSettings
from scripts.database import Base, engine
import models.databaseModels

settings = loadSettings("config.yaml")

if __name__ == "__main__":    
        Base.metadata.create_all(bind=engine)
        uvicorn.run("main:app", host=settings.api.host, port=settings.api.port) # type: ignore