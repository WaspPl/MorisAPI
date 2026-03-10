from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import yaml
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

class ApiSettings(BaseModel):
    host: str
    port: int

class AuthSettings(BaseModel):
    secret_key: str
    algorithm: str
    token_expire_minutes: int
    default_admin_password: str

class StorageSettings(BaseModel):
    scripts_dir: Path
    database_url: str

class DisplaySettings(BaseModel):
    enabled: bool
    host: str
    sprite_height: int
    sprite_width: int

class Settings(BaseSettings):
    api: ApiSettings
    auth: AuthSettings
    storage: StorageSettings
    display: DisplaySettings


@lru_cache()
def load_settings() -> Settings:
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    
    return Settings(**config_dict)

SettingsDep = Annotated[Settings, Depends(load_settings)]