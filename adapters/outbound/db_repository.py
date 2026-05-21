from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
from sqlalchemy.orm import Session
from domain.entities import Artefato
from domain.ports import ArtefatoRepositoryPort
from infrastructure.database import Base


# 1. O Modelo do Banco de Dados (ATUALIZADO)
class ArtefatoModel(Base):
    __tablename__ = "artefatos_brutos"
    __table_args__ = {'schema': 'upload'}

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, nullable=False, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)  # <-- FALTAVA!
    nome_arquivo = Column(String, nullable=False)
    conteudo_extraido = Column(Text, nullable=False)
    url_documento = Column(String, nullable=True)             # <-- FALTAVA!
    tipo_classificado = Column(String, nullable=True)
    tags = Column(ARRAY(String), default=[])
    resumo = Column(Text, nullable=True)
    data_upload = Column(DateTime, nullable=False)


# 2. O Adaptador Concreto
class PostgresArtefatoRepository(ArtefatoRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, artefato: Artefato) -> Artefato:
        novo_artefato = ArtefatoModel(
            projeto_id=artefato.projeto_id,
            usuario_id=artefato.usuario_id,   # <-- Passando para o banco
            nome_arquivo=artefato.nome_arquivo,
            conteudo_extraido=artefato.conteudo_extraido,
            url_documento=getattr(artefato, "url_documento", None), # Evita erro se não tiver URL
            tipo_classificado=artefato.tipo_classificado,
            tags=artefato.tags,
            resumo=artefato.resumo,
            data_upload=artefato.data_upload
        )
        self.db.add(novo_artefato)
        self.db.commit()
        self.db.refresh(novo_artefato)
        artefato.id = novo_artefato.id
        return artefato

    def buscar_por_projeto(self, projeto_id: int) -> list[Artefato]:
        modelos = self.db.query(ArtefatoModel).filter(ArtefatoModel.projeto_id == projeto_id).all()

        artefatos = []
        for m in modelos:
            artefatos.append(Artefato(
                id=m.id,
                nome_arquivo=m.nome_arquivo,
                conteudo_extraido=m.conteudo_extraido,
                projeto_id=m.projeto_id,
                usuario_id=m.usuario_id,
                url_documento=m.url_documento,
                tipo_classificado=m.tipo_classificado,
                tags=m.tags,
                resumo=m.resumo,
                data_upload=m.data_upload
            ))
        return artefatos

    def deletar(self, id: int) -> bool:
        artefato = self.db.query(ArtefatoModel).filter(ArtefatoModel.id == id).first()
        if artefato:
            self.db.delete(artefato)
            self.db.commit()
            return True
        return False

    def deletar_por_repositorio(self, projeto_id: int, nome_repo: str) -> int:
        artefatos = self.db.query(ArtefatoModel).filter(ArtefatoModel.projeto_id == projeto_id).all()
        tag_alvo = f"Repositório - {nome_repo}"
        deletados = 0

        for arq in artefatos:
            if tag_alvo in arq.tags:
                self.db.delete(arq)
                deletados += 1

        self.db.commit()
        return deletados