import uvicorn
from app import app
from scripts.configToObject import load_settings, SettingsDep
from scripts.database import engine, create_db_and_tables
import models.databaseModels

settings = load_settings()
if __name__ == "__main__":    
        create_db_and_tables()
        uvicorn.run("main:app", host=settings.api.host, port=settings.api.port, reload=True) # type: ignore