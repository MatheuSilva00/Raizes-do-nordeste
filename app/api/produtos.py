from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.models import Produto


router = APIRouter(prefix="/produtos", tags=["Produtos"])


class ProdutoRequest(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float = Field(gt=0)
    ativo: bool = True


@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_produto(dados: ProdutoRequest, db: Session = Depends(get_db)):
    produto = Produto(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        ativo=dados.ativo,
    )

    db.add(produto)
    db.commit()
    db.refresh(produto)

    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco,
        "ativo": produto.ativo,
    }


@router.get("/")
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()

    return [
        {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "preco": produto.preco,
            "ativo": produto.ativo,
        }
        for produto in produtos
    ]
