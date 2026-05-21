from domain.entities import Artefato
from adapters.outbound.github_extractor import GithubExtractorAdapter
from domain.ports import ArtefatoRepositoryPort, IaClientPort
from datetime import datetime


class ProcessarRepositorioUseCase:
    # 1. Adicionamos o blob_storage no construtor
    def __init__(self, extractor: GithubExtractorAdapter, repository: ArtefatoRepositoryPort, ia_client: IaClientPort,
                 blob_storage):
        self.extractor = extractor
        self.repository = repository
        self.ia_client = ia_client
        self.blob_storage = blob_storage

    async def executar(self, url_repo: str, projeto_id: int, usuario_id: int, token: str = None,
                       sobrescrever: bool = True) -> dict:
        arquivos_repo = self.extractor.extrair_arquivos(url_repo, token)

        if not arquivos_repo:
            return {"repositorio": "Desconhecido", "arquivos_processados": 0, "arquivos_ignorados": 0,
                    "arquivos_antigos_removidos": 0}

        nome_repo = arquivos_repo[0]["nome_repo"]
        arquivos_deletados = 0

        if sobrescrever:
            arquivos_deletados = self.repository.deletar_por_repositorio(projeto_id, nome_repo)
            print(f"Sincronização ativada: {arquivos_deletados} arquivos antigos removidos do banco.")

        salvos = 0
        falhas = 0

        for arq in arquivos_repo:
            texto = arq["conteudo"]
            texto_limpo = texto[:10000]
            nome_arquivo_original = arq["nome_arquivo"]

            try:
                # 2. Faz a IA classificar
                resultado_ia = await self.ia_client.classificar_documento(texto_limpo)

                tags_finais = resultado_ia.get("tags", [])
                tag_repo = f"Repositório - {nome_repo}"
                if tag_repo not in tags_finais:
                    tags_finais.append(tag_repo)

                # 3. MÁGICA FÍSICA: Converte o texto do GitHub em um "arquivo físico" (bytes) e manda pro Azure Blob
                conteudo_bytes = texto.encode('utf-8')
                url_blob = await self.blob_storage.upload_arquivo(conteudo_bytes, nome_arquivo_original)

                # 4. Salva a URL retornada pela Azure no nosso banco PostgreSQL
                novo_artefato = Artefato(
                    nome_arquivo=nome_arquivo_original,
                    conteudo_extraido=texto,
                    projeto_id=projeto_id,
                    usuario_id=usuario_id,
                    url_documento=url_blob,  # <--- AGORA VAI PREENCHER A COLUNA NO BANCO!
                    tipo_classificado=resultado_ia.get("tipo_classificado", "Código-Fonte"),
                    tags=tags_finais,
                    resumo=resultado_ia.get("resumo", "Arquivo de código-fonte.")
                )

                novo_artefato.data_upload = datetime.utcnow()
                self.repository.salvar(novo_artefato)
                salvos += 1

            except Exception as e:
                print(f"🔴 ERRO FATAL ao processar o arquivo {nome_arquivo_original}: {str(e)}")
                falhas += 1

        return {
            "repositorio": nome_repo,
            "arquivos_processados": salvos,
            "arquivos_ignorados": falhas,
            "arquivos_antigos_removidos": arquivos_deletados
        }