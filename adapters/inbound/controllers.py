from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from adapters.outbound.db_repository import PostgresArtefatoRepository
from adapters.outbound.ia_client import HttpIaClientAdapter
from adapters.outbound.github_extractor import GithubExtractorAdapter
from application.use_cases import ProcessarRepositorioUseCase
from typing import Optional

router = APIRouter()


class RepoRequest(BaseModel):
    url: str
    projeto_id: int
    token: Optional[str] = None
    sobrescrever: bool = True  # NOVO CAMPO (Padrão é True)


@router.post("/api/github/conectar")
async def conectar_repositorio(request: RepoRequest, db: Session = Depends(get_db)):
    if not request.url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="URL inválida. Deve ser do GitHub.")

    partes_url = request.url.split('/')
    if len(partes_url) >= 5:
        url_limpa = "/".join(partes_url[:5])
    else:
        url_limpa = request.url

    try:
        repository = PostgresArtefatoRepository(db)
        extractor = GithubExtractorAdapter()
        ia_client = HttpIaClientAdapter()

        use_case = ProcessarRepositorioUseCase(extractor, repository, ia_client)

        # Agora repassamos a opção de sobrescrever
        resultado = await use_case.executar(url_limpa, request.projeto_id, request.token, request.sobrescrever)

        return {
            "mensagem": "Repositório processado com sucesso!",
            "estatisticas": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))