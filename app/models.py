from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from datetime import datetime


class StatusEquipamento(str, Enum):
    ativo = "ativo"
    manutencao = "manutencao"
    parado = "parado"


class ManutencaoBase(SQLModel):
    descricao: str
    tecnico: str


class EquipamentoBase(SQLModel):
    nome: str
    serie: str = Field(index=True)
    status: StatusEquipamento = Field(default=StatusEquipamento.ativo)


class Equipamento(EquipamentoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    manutencoes: List["Manutencao"] = Relationship(back_populates="equipamento")


class EquipamentoCreate(EquipamentoBase):
    pass


class StatusUpdate(SQLModel):
    status: StatusEquipamento


class Manutencao(ManutencaoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    equipamento_id: int = Field(foreign_key="equipamento.id")
    data: datetime = Field(default_factory=datetime.utcnow)

    equipamento: Optional[Equipamento] = Relationship(back_populates="manutencoes")


class ManutencaoCreate(ManutencaoBase):
    pass


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str


class UserCreate(SQLModel):
    username: str
    password: str