from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import obter_usuario_atual
from app.infrastructure.database import get_db
from app.infrastructure.models import Pagamento, Pedido, Usuario


router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


@router.post("/{pedido_id}", status_code=status.HTTP_201_CREATED)
def pagar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    pedido = (
        db.query(Pedido)
        .filter(
            Pedido.id == pedido_id,
            Pedido.cliente_id == usuario.id,
        )
        .first()
    )

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    if pedido.status != "AGUARDANDO_PAGAMENTO":
        raise HTTPException(
            status_code=409,
            detail="Este pedido não está aguardando pagamento.",
        )

    pagamento_existente = (
        db.query(Pagamento)
        .filter(Pagamento.pedido_id == pedido_id)
        .first()
    )

    if pagamento_existente:
        raise HTTPException(
            status_code=409,
            detail="Já existe um pagamento para este pedido.",
        )

    pagamento = Pagamento(
        pedido_id=pedido.id,
        forma="MOCK",
        status="APROVADO",
        resposta_mock="Pagamento simulado aprovado.",
    )

    pedido.status = "PAGO"
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)

    return {
        "pagamento_id": pagamento.id,
        "pedido_id": pedido.id,
        "forma": pagamento.forma,
        "status_pagamento": pagamento.status,
        "status_pedido": pedido.status,
        "mensagem": pagamento.resposta_mock,
    }
