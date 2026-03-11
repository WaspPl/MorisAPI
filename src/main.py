import uvicorn
from app import app
from scripts.configToObject import load_settings, SettingsDep
from scripts.database import engine, create_db_and_tables
import models.databaseModels

if __name__ == "__main__":    
        settings = load_settings()
        create_db_and_tables()
        uvicorn.run("main:app", host=settings.api.host, port=settings.api.port, reload=True) # type: ignore