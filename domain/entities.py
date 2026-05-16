from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Artefato:
    nome_arquivo: str
    conteudo_extraido: str
    projeto_id: int
    tipo_classificado: Optional[str] = "Desconhecido"
    tags: List[str] = field(default_factory=list)
    resumo: Optional[str] = "Sem resumo."
    data_upload: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None