from typing import Optional
from sqlalchemy import asc, desc
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Equipamento, StatusUpdate, StatusEquipamento
from app.auth import obter_usuario_atual

router = APIRouter()


@router.post(
    "/equipamento",
    response_model=Equipamento,
    status_code=status.HTTP_201_CREATED
)
def criar_equipamento(
    equipamento: Equipamento,
    session: Session = Depends(get_session),
    current_user: dict = Depends(obter_usuario_atual)
):
    # impedir série duplicada
    statement = select(Equipamento).where(Equipamento.serie == equipamento.serie)
    existe = session.exec(statement).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Já existe equipamento com essa série"
        )

    session.add(equipamento)
    session.commit()
    session.refresh(equipamento)

    return equipamento


@router.get("/equipamentos", response_model=list[Equipamento])
def listar_equipamentos(
    status: Optional[StatusEquipamento] = None,
    nome: Optional[str] = None,
    serie: Optional[str] = None,
    sort: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(obter_usuario_atual)
):
    statement = select(Equipamento)

    if status:
        statement = statement.where(Equipamento.status == status)

    if nome:
        statement = statement.where(Equipamento.nome.contains(nome))

    if serie:
        statement = statement.where(Equipamento.serie.contains(serie))

    if sort:
        campo = sort.replace("-", "")
        coluna = getattr(Equipamento, campo, None)

        if coluna:
            if sort.startswith("-"):
                statement = statement.order_by(desc(coluna))
            else:
                statement = statement.order_by(asc(coluna))

    statement = statement.offset(offset).limit(limit)

    equipamentos = session.exec(statement).all()

    return equipamentos


@router.get("/equipamento/{equip_id}", response_model=Equipamento)
def buscar_por_id(
    equip_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(obter_usuario_atual)
):
    equipamento = session.get(Equipamento, equip_id)

    if not equipamento:
        raise HTTPException(
            status_code=404,
            detail="Equipamento não encontrado"
        )

    return equipamento


@router.delete("/equipamento/{equip_id}")
def deletar_por_id(
    equip_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(obter_usuario_atual)
):
    equipamento = session.get(Equipamento, equip_id)

    if not equipamento:
        raise HTTPException(
            status_code=404,
            detail="Equipamento não encontrado"
        )

    session.delete(equipamento)
    session.commit()

    return {"mensagem": "Equipamento removido com sucesso"}


@router.put("/equipamento/{equip_id}/status", response_model=Equipamento)
def atualizar_status(
    equip_id: int,
    payload: StatusUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(obter_usuario_atual)
):
    equipamento = session.get(Equipamento, equip_id)

    if not equipamento:
        raise HTTPException(
            status_code=404,
            detail="Equipamento não encontrado"
        )

    equipamento.status = payload.status

    session.add(equipamento)
    session.commit()
    session.refresh(equipamento)

    return equipamento