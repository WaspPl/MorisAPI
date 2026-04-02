from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import yaml
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080

class AuthSettings(BaseModel):
    secret_key: str = "ChangeThisToYourSecretKey"
    algorithm: str = "HS256"
    default_admin_password: str = "admin"

class StorageSettings(BaseModel):
    scripts_dir: Path = "storage/scripts"
    database_url: str = "sqlite:///./storage/moris.db"

class DisplaySettings(BaseModel):
    enabled: bool = True
    use_uds: bool = False
    uds_path: str = "/tmp/morisMALDC.sock"
    route: str = "/display"
    api_url: str = "0.0.0.0:2020"
    sprite_height: int = 8
    sprite_width: int = 8

class LLMSettings(BaseModel):
    api_url: str = "https://api.openai.com/v1/chat/completions"
    auth_token: str = "YouAPITokenGoesHere"
    model: str = 'gpt-5-nano'
    previous_messages_sent: int = 6
    verbosity: str = 'low'

    
class Settings(BaseSettings):
    api: ApiSettings = ApiSettings()
    auth: AuthSettings = AuthSettings()
    storage: StorageSettings = StorageSettings()
    display: DisplaySettings = DisplaySettings()
    LLM: LLMSettings = LLMSettings()


@lru_cache()
def load_settings() -> Settings:
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    
    if not config_path.exists():
        settings = Settings()     
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(settings.model_dump(), f, default_flow_style=False)

    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    
    return Settings(**config_dict)

SettingsDep = Annotated[Settings, Depends(load_settings)]