from abc import ABC, abstractmethod
from typing import List
from domain.entities import Artefato

class ArtefatoRepositoryPort(ABC):
    @abstractmethod
    def salvar(self, artefato: Artefato) -> Artefato:
        pass

    @abstractmethod
    def buscar_por_projeto(self, projeto_id: int) -> List[Artefato]:
        pass

    @abstractmethod
    def deletar(self, id: int) -> bool:
        pass


    @abstractmethod
    def deletar_por_repositorio(self, projeto_id: int, nome_repo: str) -> int:
        pass

class IaClientPort(ABC):
    @abstractmethod
    async def classificar_documento(self, texto: str) -> dict:
        pass