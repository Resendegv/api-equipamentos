from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db import criar_db_e_tabelas
from app.routes import router
from app.auth import autenticar_usuario, criar_access_token

app = FastAPI(title="API de Equipamentos")

@app.on_event("startup")
def on_startup():
    criar_db_e_tabelas()

@app.get("/")
def home():
    return {"status": "ok", "msg": "API online. Acesse /docs"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ok = autenticar_usuario(form_data.username, form_data.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos")

    token = criar_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

app.include_router(router)