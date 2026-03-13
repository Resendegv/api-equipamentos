from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# routers
from app.routers import equipamentos_router
from app.routers import estatisticas_router
from app.routers import auth_router

app = FastAPI(
    title="API Equipamentos",
    description="API para gestão de equipamentos de frota",
    version="1.0.0"
)

# CORS (permite acesso de front-end no futuro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rota inicial
@app.get("/")
def root():
    return {
        "mensagem": "API Equipamentos funcionando 🚜"
    }

# registrar routers
app.include_router(auth_router.router)
app.include_router(equipamentos_router.router)
app.include_router(estatisticas_router.router)