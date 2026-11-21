from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.models import Unidade


router = APIRouter(prefix="/unidades", tags=["Unidades"])


class UnidadeRequest(BaseModel):
    nome: str
    cidade: str
    ativa: bool = True


@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_unidade(dados: UnidadeRequest, db: Session = Depends(get_db)):
    unidade = Unidade(
        nome=dados.nome,
        cidade=dados.cidade,
        ativa=dados.ativa,
    )

    db.add(unidade)
    db.commit()
    db.refresh(unidade)

    return {
        "id": unidade.id,
        "nome": unidade.nome,
        "cidade": unidade.cidade,
        "ativa": unidade.ativa,
    }


@router.get("/")
def listar_unidades(db: Session = Depends(get_db)):
    unidades = db.query(Unidade).order_by(Unidade.id).all()

    return [
        {
            "id": unidade.id,
            "nome": unidade.nome,
            "cidade": unidade.cidade,
            "ativa": unidade.ativa,
        }
        for unidade in unidades
    ]
