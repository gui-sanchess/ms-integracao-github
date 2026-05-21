from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Artefato:
    nome_arquivo: str
    conteudo_extraido: str
    projeto_id: int
    usuario_id: int  # <--- O atributo que faltava para a integração não quebrar!
    url_documento: Optional[str] = None  # <--- Adicionado para ficar igual ao Upload
    tipo_classificado: Optional[str] = "Desconhecido"
    tags: List[str] = field(default_factory=list)
    resumo: Optional[str] = "Sem resumo."
    data_upload: datetime = field(default_factory=datetime.utcnow) # utcnow evita conflitos de fuso horário
    id: Optional[int] = None