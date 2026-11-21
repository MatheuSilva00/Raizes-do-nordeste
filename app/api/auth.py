import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.models import Usuario


router = APIRouter(prefix="/auth", tags=["Autenticação"])
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "chave-temporaria-apenas-para-desenvolvimento")
JWT_ALGORITHM = "HS256"
TOKEN_MINUTES = 60
PBKDF2_ITERATIONS = 310_000


class CadastroRequest(BaseModel):
    nome: str
    email: str
    senha: str


class LoginRequest(BaseModel):
    email: str
    senha: str


def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"{salt.hex()}${derivado.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        salt_hex, hash_armazenado = senha_hash.split("$")
        derivado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(salt_hex),
            PBKDF2_ITERATIONS,
        ).hex()
        return hmac.compare_digest(derivado, hash_armazenado)
    except (ValueError, TypeError):
        return False


def criar_token(usuario: Usuario) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario.id),
        "perfil": usuario.perfil,
        "iat": agora,
        "exp": agora + timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def cadastrar(dados: CadastroRequest, db: Session = Depends(get_db)):
    if "@" not in dados.email:
        raise HTTPException(status_code=422, detail="E-mail inválido.")

    existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existente:
        raise HTTPException(status_code=409, detail="Este e-mail já está cadastrado.")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil="CLIENTE",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
    }


@router.post("/login")
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    return {
        "accessToken": criar_token(usuario),
        "tokenType": "Bearer",
        "expiresIn": TOKEN_MINUTES * 60,
        "user": {
            "id": usuario.id,
            "nome": usuario.nome,
            "perfil": usuario.perfil,
        },
    }


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credenciais.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        usuario_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise erro

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise erro

    return usuario


@router.get("/me")
def meu_perfil(usuario: Usuario = Depends(obter_usuario_atual)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
    }
