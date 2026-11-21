from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.models import Estoque, Produto, Unidade


router = APIRouter(prefix="/estoques", tags=["Estoques"])


class EstoqueRequest(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int = Field(ge=0)


@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_estoque(dados: EstoqueRequest, db: Session = Depends(get_db)):
    unidade = db.query(Unidade).filter(Unidade.id == dados.unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")

    produto = db.query(Produto).filter(Produto.id == dados.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    existente = (
        db.query(Estoque)
        .filter(
            Estoque.unidade_id == dados.unidade_id,
            Estoque.produto_id == dados.produto_id,
        )
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Já existe um registro de estoque para este produto nesta unidade.",
        )

    estoque = Estoque(
        unidade_id=dados.unidade_id,
        produto_id=dados.produto_id,
        quantidade=dados.quantidade,
    )

    db.add(estoque)
    db.commit()
    db.refresh(estoque)

    return {
        "id": estoque.id,
        "unidade_id": estoque.unidade_id,
        "produto_id": estoque.produto_id,
        "quantidade": estoque.quantidade,
    }


@router.get("/")
def listar_estoques(db: Session = Depends(get_db)):
    estoques = db.query(Estoque).all()

    return [
        {
            "id": estoque.id,
            "unidade_id": estoque.unidade_id,
            "produto_id": estoque.produto_id,
            "quantidade": estoque.quantidade,
        }
        for estoque in estoques
    ]
