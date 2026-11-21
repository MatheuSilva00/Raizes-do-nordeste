from fastapi import FastAPI
from app.infrastructure.database import Base, engine
from app.infrastructure import models
from app.api.estoques import router as estoques_router
from app.api.unidades import router as unidades_router
from app.api.produtos import router as produtos_router
from app.api.auth import router as auth_router
from app.api.pedidos import router as pedidos_router
from app.api.pagamentos import router as pagamentos_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rede Raízes do Nordeste - API",
    description="API do projeto multidisciplinar de Back-end",
    version="1.0.0",
)

app.include_router(unidades_router)
app.include_router(auth_router)
app.include_router(produtos_router)
app.include_router(estoques_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)
