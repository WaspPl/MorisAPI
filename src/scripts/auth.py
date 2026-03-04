from pwdlib import PasswordHash
from scripts.configToObject import loadSettings
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from typing import Annotated

from scripts.database import SessionDep
from models.databaseModels import Users
from sqlmodel import select

settings = loadSettings("config.yaml")

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

def verifyPassword(plainPassword: str, hashedPassword: str):
    return passwordHash.verify(plainPassword, hashedPassword)

def getPasswordHash(password: str):
    return passwordHash.hash(password)

def getUser(username: str, session: SessionDep):
    user = session.exec(select(Users).where(Users.username == username)).one_or_none()

    return user

def authenticateUser(username: str, password: str, session: SessionDep):
    user = getUser(username, session)
    
    if not user:
        verifyPassword(password, dummyHash)
        return False
    if not verifyPassword(password, user.hashed_password):
        return False
    return user

def createAccessToken(data: dict, expiresDelta: timedelta | None = None):
    dataToEncode = data.copy()
    if expiresDelta:
        expire = datetime.now() + expiresDelta
    else:
        expire = datetime.now() + timedelta(minutes = token_expire_minutes)
    dataToEncode.update({"exp":expire})
    encodedJWT = jwt.encode(dataToEncode, secretKey, algorithm=algorithm)
    return encodedJWT

def getCurrentUser(token: Annotated[str, Depends(oauth2_scheme)]):
    credentailsException = HTTPException(
        status_code=401,
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
    user = getUser(username= tokenData.username)
    if user is None:
        raise credentailsException
    return user


