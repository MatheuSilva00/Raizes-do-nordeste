from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import obter_usuario_atual
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Estoque,
    ItemPedido,
    Pedido,
    Produto,
    Unidade,
    Usuario,
)


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


class ItemPedidoRequest(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class PedidoRequest(BaseModel):
    unidade_id: int
    canal_pedido: str = Field(min_length=1, max_length=20)
    itens: list[ItemPedidoRequest] = Field(min_length=1)


@router.post("/", status_code=status.HTTP_201_CREATED)
def criar_pedido(
    dados: PedidoRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    unidade = db.query(Unidade).filter(Unidade.id == dados.unidade_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    if not unidade.ativa:
        raise HTTPException(status_code=409, detail="A unidade está inativa.")

    # Evita incluir o mesmo produto mais de uma vez no mesmo pedido.
    produto_ids = [item.produto_id for item in dados.itens]
    if len(produto_ids) != len(set(produto_ids)):
        raise HTTPException(
            status_code=422,
            detail="Informe cada produto apenas uma vez no pedido.",
        )

    itens_validados = []
    total = 0.0

    # Primeiro valida todos os itens; só depois altera o estoque.
    for item in dados.itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {item.produto_id} não encontrado.",
            )
        if not produto.ativo:
            raise HTTPException(
                status_code=409,
                detail=f"O produto {item.produto_id} está inativo.",
            )

        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.unidade_id == dados.unidade_id,
                Estoque.produto_id == item.produto_id,
            )
            .first()
        )
        if not estoque:
            raise HTTPException(
                status_code=404,
                detail=f"Estoque não cadastrado para o produto {item.produto_id} nesta unidade.",
            )
        if estoque.quantidade < item.quantidade:
            raise HTTPException(
                status_code=409,
                detail=f"Estoque insuficiente para o produto {item.produto_id}.",
            )

        itens_validados.append((item, produto, estoque))
        total += produto.preco * item.quantidade

    pedido = Pedido(
        cliente_id=usuario.id,
        unidade_id=dados.unidade_id,
        canal_pedido=dados.canal_pedido,
        status="AGUARDANDO_PAGAMENTO",
        total=total,
    )
    db.add(pedido)
    db.flush()

    resposta_itens = []

    for item, produto, estoque in itens_validados:
        db.add(
            ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )
        estoque.quantidade -= item.quantidade

        resposta_itens.append(
            {
                "produto_id": produto.id,
                "nome": produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": produto.preco,
            }
        )

    db.commit()
    db.refresh(pedido)

    return {
        "id": pedido.id,
        "cliente_id": pedido.cliente_id,
        "unidade_id": pedido.unidade_id,
        "canal_pedido": pedido.canal_pedido,
        "status": pedido.status,
        "total": pedido.total,
        "itens": resposta_itens,
    }


@router.get("/")
def listar_meus_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.cliente_id == usuario.id)
        .order_by(Pedido.criado_em.desc())
        .all()
    )

    resultado = []

    for pedido in pedidos:
        itens = (
            db.query(ItemPedido)
            .filter(ItemPedido.pedido_id == pedido.id)
            .all()
        )

        resultado.append(
            {
                "id": pedido.id,
                "unidade_id": pedido.unidade_id,
                "canal_pedido": pedido.canal_pedido,
                "status": pedido.status,
                "total": pedido.total,
                "criado_em": pedido.criado_em.isoformat() if pedido.criado_em else None,
                "itens": [
                    {
                        "produto_id": item.produto_id,
                        "quantidade": item.quantidade,
                        "preco_unitario": item.preco_unitario,
                    }
                    for item in itens
                ],
            }
        )

    return resultado