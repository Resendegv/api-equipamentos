from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class StatusEquipamento(str, Enum):
    ativo = "ativo"
    manutencao = "manutencao"
    parado = "parado"


class Equipamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    serie: str
    status: StatusEquipamento


class StatusUpdate(SQLModel):
    status: StatusEquipamento