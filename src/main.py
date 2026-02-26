import uvicorn
import os
from app import app
from scripts.configToObject import loadSettings

settings = loadSettings("config.yaml")

if __name__ == "__main__":    
        uvicorn.run("main:app", host=settings.api.host, port=settings.api.port) # type: ignore