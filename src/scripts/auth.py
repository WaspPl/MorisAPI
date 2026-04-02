from pwdlib import PasswordHash
from scripts.settings import load_settings
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from typing import Annotated

from scripts.database import SessionDep
from models.databaseModels import User
from sqlmodel import select

settings = load_settings()

token_expire_minutes = settings.auth.token_expire_minutes
secretKey = settings.auth.secret_key
algorithm = settings.auth.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    accessToken: str
    tokenType: str

class TokenData(BaseModel):
    username: str

passwordHash = PasswordHash.recommended()

dummyHash = passwordHash.hash("dummyPasswordLol")

OAuth2Scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str):
    return passwordHash.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return passwordHash.hash(password)

def get_user(username: str, session: SessionDep):
    user = session.exec(select(User).where(User.username == username)).one_or_none()

    return user

def authenticate_user(username: str, password: str, session: SessionDep):
    user = get_user(username, session)
    
    if not user:
        verify_password(password, dummyHash)
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    dataToEncode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes = token_expire_minutes)
    dataToEncode.update({"exp":expire})
    encodedJWT = jwt.encode(dataToEncode, secretKey, algorithm=algorithm)
    return encodedJWT

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],session: SessionDep):
    credentailsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secretKey, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentailsException
        tokenData = TokenData(username = username)
    except InvalidTokenError:
        raise credentailsException
    user = get_user(username= tokenData.username, session = session)
    if user is None:
        raise credentailsException
    return user


def get_admin(token: Annotated[str, Depends(oauth2_scheme)],session: SessionDep):
    user = get_current_user(token, session)
    if user.role_id == 1:
        return user
    
    raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You dont have permission to do that",
    headers={"WWW-Authenticate": "Bearer"},
    )

