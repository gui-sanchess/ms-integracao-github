import jwt  # <-- Lembre-se de instalar com: pip install PyJWT
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from adapters.outbound.db_repository import PostgresArtefatoRepository
from adapters.outbound.ia_client import HttpIaClientAdapter
from adapters.outbound.github_extractor import GithubExtractorAdapter
from application.use_cases import ProcessarRepositorioUseCase
from typing import Optional
from adapters.outbound.blob_service import AzureBlobStorageAdapter
router = APIRouter()

class RepoRequest(BaseModel):
    url: str
    projeto_id: int
    token: Optional[str] = None
    sobrescrever: bool = True

@router.post("/api/github/conectar")
async def conectar_repositorio(
    request: RepoRequest,
    db: Session = Depends(get_db),
    authorization: str = Header(...)  # <-- Exigindo o token enviado pelo sessao.js
):
    if not request.url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="URL inválida. Deve ser do GitHub.")

    partes_url = request.url.split('/')
    if len(partes_url) >= 5:
        url_limpa = "/".join(partes_url[:5])
    else:
        url_limpa = request.url

    # Extraindo o ID do usuário diretamente do Token JWT
        # Extraindo o ID do usuário diretamente do Token JWT de forma blindada
    try:
        token_puro = authorization.replace("Bearer ", "").strip()
        payload = jwt.decode(token_puro, options={"verify_signature": False})

        # Procura o ID em vários campos possíveis que o grupo de login pode ter usado
        user_id_str = payload.get("sub") or payload.get("user_id") or payload.get("id")

        if not user_id_str:
            raise ValueError(f"ID não encontrado no payload. Conteúdo do token: {payload}")

        usuario_id = int(user_id_str)

    except Exception as e:
        print(f"🔴 ERRO AO LER TOKEN: {str(e)}")  # Vai aparecer na tela preta da Azure
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

    try:
        repository = PostgresArtefatoRepository(db)
        extractor = GithubExtractorAdapter()
        ia_client = HttpIaClientAdapter()
        blob_storage = AzureBlobStorageAdapter()

        use_case = ProcessarRepositorioUseCase(extractor, repository, ia_client, blob_storage)

        # Repassando o usuario_id extraído para o Use Case
        resultado = await use_case.executar(
            url_repo=url_limpa,
            projeto_id=request.projeto_id,
            usuario_id=usuario_id,  # <-- Enviando o ID real
            token=request.token,
            sobrescrever=request.sobrescrever
        )

        return {
            "mensagem": "Repositório processado com sucesso!",
            "estatisticas": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))