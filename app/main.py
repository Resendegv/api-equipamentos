from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.db import criar_db_e_tabelas, get_session
from app.routes import router
from app.models import User
from app.auth import criar_token

app = FastAPI(title="API de Equipamentos")


@app.on_event("startup")
def on_startup():
    criar_db_e_tabelas()


@app.get("/")
def home():
    return {"status": "ok", "msg": "API online. Acesse /docs"}


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == form_data.username)
    db_user = session.exec(statement).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    token = criar_token({"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


app.include_router(router)