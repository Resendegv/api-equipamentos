from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from sqlalchemy import asc, desc

from app.db import engine
from app.models import (
    Equipamento,
    EquipamentoCreate,
    StatusUpdate,
    StatusEquipamento,
    Manutencao,
    ManutencaoCreate,
    User,
    UserCreate
)
from app.auth import get_current_user, criar_token

router = APIRouter()


@router.get("/")
def home():
    return {"mensagem": "API de Equipamentos funcionando"}


@router.post("/users")
def criar_usuario(user: UserCreate):
    with Session(engine) as session:
        existe = session.exec(
            select(User).where(User.username == user.username)
        ).first()

        if existe:
            raise HTTPException(status_code=400, detail="Usuário já existe")

        novo_usuario = User(
            username=user.username,
            hashed_password=user.password
        )

        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

        return novo_usuario


@router.post("/login")
def login(user: UserCreate):
    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()

        if not db_user:
            raise HTTPException(status_code=401, detail="Usuário inválido")

        token = criar_token({"sub": db_user.username})

        return {"access_token": token, "token_type": "bearer"}


@router.get("/equipamentos")
def listar_equipamentos(
    status: Optional[StatusEquipamento] = None,
    nome: Optional[str] = None,
    serie: Optional[str] = None,
    sort: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:

        query = select(Equipamento)

        if status:
            query = query.where(Equipamento.status == status)

        if nome:
            query = query.where(Equipamento.nome.contains(nome))

        if serie:
            query = query.where(Equipamento.serie.contains(serie))

        if sort:
            campo = sort.replace("-", "")
            coluna = getattr(Equipamento, campo, None)

            if coluna is not None:
                if sort.startswith("-"):
                    query = query.order_by(desc(coluna))
                else:
                    query = query.order_by(asc(coluna))

        query = query.offset(offset).limit(limit)

        equipamentos = session.exec(query).all()

        return equipamentos


@router.get("/equipamentos")
def listar_equipamentos(
    status: Optional[StatusEquipamento] = None,
    nome: Optional[str] = None,
    serie: Optional[str] = None,
    sort: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        query = select(Equipamento)

        if status:
            query = query.where(Equipamento.status == status)

        if nome:
            query = query.where(Equipamento.nome.contains(nome))

        if serie:
            query = query.where(Equipamento.serie.contains(serie))

        if sort:
            campo = sort.replace("-", "")
            coluna = getattr(Equipamento, campo, None)

            if coluna is not None:
                if sort.startswith("-"):
                    query = query.order_by(desc(coluna))
                else:
                    query = query.order_by(asc(coluna))

        query = query.offset(offset).limit(limit)

        equipamentos = session.exec(query).all()
        return equipamentos


@router.get("/equipamento/{equip_id}")
def buscar_equipamento(
    equip_id: int,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        equipamento = session.get(Equipamento, equip_id)

        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        manutencoes = session.exec(
            select(Manutencao).where(Manutencao.equipamento_id == equip_id)
        ).all()

        return {
            "id": equipamento.id,
            "nome": equipamento.nome,
            "serie": equipamento.serie,
            "status": equipamento.status,
            "manutencoes": manutencoes
        }


@router.delete("/equipamento/{equip_id}")
def deletar_equipamento(
    equip_id: int,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        equipamento = session.get(Equipamento, equip_id)

        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        session.delete(equipamento)
        session.commit()

        return {"mensagem": "Equipamento removido"}


@router.put("/equipamento/{equip_id}/status")
def atualizar_status(
    equip_id: int,
    status_update: StatusUpdate,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        equipamento = session.get(Equipamento, equip_id)

        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        equipamento.status = status_update.status

        session.add(equipamento)
        session.commit()
        session.refresh(equipamento)

        return equipamento


@router.post("/equipamento/{equip_id}/manutencao")
def criar_manutencao(
    equip_id: int,
    payload: ManutencaoCreate,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        equipamento = session.get(Equipamento, equip_id)

        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        manutencao = Manutencao(
            equipamento_id=equip_id,
            descricao=payload.descricao,
            tecnico=payload.tecnico
        )

        session.add(manutencao)
        session.commit()
        session.refresh(manutencao)

        return manutencao


@router.get("/equipamento/{equip_id}/manutencoes")
def listar_manutencoes(
    equip_id: int,
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        manutencoes = session.exec(
            select(Manutencao).where(Manutencao.equipamento_id == equip_id)
        ).all()

        return manutencoes


@router.get("/dashboard")
def dashboard(
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        equipamentos = session.exec(select(Equipamento)).all()

        total = len(equipamentos)
        ativos = len([e for e in equipamentos if e.status == StatusEquipamento.ativo])
        manutencao = len([e for e in equipamentos if e.status == StatusEquipamento.manutencao])
        parados = len([e for e in equipamentos if e.status == StatusEquipamento.parado])

        total_manutencoes = len(session.exec(select(Manutencao)).all())

        return {
            "total_equipamentos": total,
            "ativos": ativos,
            "em_manutencao": manutencao,
            "parados": parados,
            "total_manutencoes": total_manutencoes
        }
    
@router.get("/estatisticas/manutencoes")
def estatisticas_manutencoes(
    current_user: str = Depends(get_current_user)
):
    with Session(engine) as session:
        manutencoes = session.exec(select(Manutencao)).all()
        equipamentos = session.exec(select(Equipamento)).all()

        total_manutencoes = len(manutencoes)
        total_equipamentos = len(equipamentos)

        contagem_por_equipamento = {}

        for manutencao in manutencoes:
            equip_id = manutencao.equipamento_id
            contagem_por_equipamento[equip_id] = contagem_por_equipamento.get(equip_id, 0) + 1

        equipamento_com_mais_manutencoes = None
        maior_qtd = 0

        for equipamento in equipamentos:
            qtd = contagem_por_equipamento.get(equipamento.id, 0)
            if qtd > maior_qtd:
                maior_qtd = qtd
                equipamento_com_mais_manutencoes = equipamento.nome

        media_manutencoes_por_equipamento = (
            total_manutencoes / total_equipamentos
            if total_equipamentos > 0 else 0
        )

        return {
            "total_manutencoes": total_manutencoes,
            "equipamento_com_mais_manutencoes": equipamento_com_mais_manutencoes,
            "quantidade_do_campeao": maior_qtd,
            "media_manutencoes_por_equipamento": round(media_manutencoes_por_equipamento, 2)
        }