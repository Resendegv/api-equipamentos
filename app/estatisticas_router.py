from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Equipamento

router = APIRouter(
    prefix="/estatisticas",
    tags=["Estatisticas"]
)

@router.get("/")
def estatisticas_frota(db: Session = Depends(get_db)):
    total = db.query(Equipamento).count()

    operando = db.query(Equipamento).filter(
        Equipamento.status == "operando"
    ).count()

    manutencao = db.query(Equipamento).filter(
        Equipamento.status == "manutencao"
    ).count()

    parado = db.query(Equipamento).filter(
        Equipamento.status == "parado"
    ).count()

    disponibilidade = 0
    if total > 0:
        disponibilidade = operando / total

    return {
        "total_equipamentos": total,
        "operando": operando,
        "em_manutencao": manutencao,
        "parados": parado,
        "disponibilidade": disponibilidade,
        "disponibilidade_percentual": round(disponibilidade * 100, 2)
    }