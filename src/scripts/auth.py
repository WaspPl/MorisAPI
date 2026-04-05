import uuid

from pwdlib import PasswordHash
from scripts.settings import load_settings
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from typing import Annotated

from scripts.database import SessionDep
from models.databaseModels import RefreshTokens, User
from sqlmodel import select

settings = load_settings()

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

def create_access_token(data: dict, expires_delta: timedelta):
    dataToEncode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta

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


def create_refresh_token(data: dict, expires_delta: timedelta, session: SessionDep, user_id: int):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh", "randomUUID": str(uuid.uuid4)})
    encoded_jwt = jwt.encode(to_encode, secretKey, algorithm=algorithm)
    
    db_token = RefreshTokens(
        user_id=user_id, 
        refresh_token=passwordHash.hash(encoded_jwt)
    )
    session.add(db_token)
    session.commit()
    
    return encoded_jwt

def validate_refresh_token(refresh_token: str, session: SessionDep):
    try:
        payload = jwt.decode(refresh_token, secretKey, algorithms=[algorithm])
        username: str = payload.get("sub")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    payload = jwt.decode(refresh_token, secretKey, algorithms=[algorithm])
    if payload.get('exp') < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Refresh token expired")



    user = get_user(username, session)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    db_tokens = session.exec(select(RefreshTokens).where(RefreshTokens.user_id == user.id)).all()
    
    valid_db_entry = None
    for entry in db_tokens:
        if passwordHash.verify(refresh_token, entry.refresh_token):
            valid_db_entry = entry
            break
            
    if not valid_db_entry:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")

    return user, valid_db_entry