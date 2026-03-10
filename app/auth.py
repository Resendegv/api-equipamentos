from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# ⚠️ Troque isso depois por algo forte e secreto
SECRET_KEY = "vini2788teste"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Usuário fixo (por enquanto). Depois a gente põe em banco.
FAKE_USER = {
    "username": "vinicius",
    "password": "1234",
}

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def autenticar_usuario(username: str, password: str) -> bool:
    return username == FAKE_USER["username"] and password == FAKE_USER["password"]

def obter_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise cred_exception
    except JWTError:
        raise cred_exception

    # valida usuário
    if username != FAKE_USER["username"]:
        raise cred_exception

    return {"username": username}