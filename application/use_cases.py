from domain.entities import Artefato
from adapters.outbound.github_extractor import GithubExtractorAdapter
from domain.ports import ArtefatoRepositoryPort, IaClientPort


class ProcessarRepositorioUseCase:
    def __init__(self, extractor: GithubExtractorAdapter, repository: ArtefatoRepositoryPort, ia_client: IaClientPort):
        self.extractor = extractor
        self.repository = repository
        self.ia_client = ia_client

    async def executar(self, url_repo: str, projeto_id: int, token: str = None, sobrescrever: bool = True) -> dict:
        arquivos_repo = self.extractor.extrair_arquivos(url_repo, token)

        if not arquivos_repo:
            return {"repositorio": "Desconhecido", "arquivos_processados": 0, "arquivos_ignorados": 0, "deletados": 0}

        nome_repo = arquivos_repo[0]["nome_repo"]
        arquivos_deletados = 0

        # MÁGICA DA SINCRONIZAÇÃO AQUI!
        if sobrescrever:
            arquivos_deletados = self.repository.deletar_por_repositorio(projeto_id, nome_repo)
            print(f"Sincronização ativada: {arquivos_deletados} arquivos antigos removidos do banco.")

        salvos = 0
        falhas = 0

        for arq in arquivos_repo:
            texto = arq["conteudo"]
            texto_limpo = texto[:10000]

            try:
                resultado_ia = await self.ia_client.classificar_documento(texto_limpo)

                tags_finais = resultado_ia.get("tags", [])
                tag_repo = f"Repositório - {nome_repo}"
                if tag_repo not in tags_finais:
                    tags_finais.append(tag_repo)

                novo_artefato = Artefato(
                    nome_arquivo=arq["nome_arquivo"],
                    conteudo_extraido=texto,
                    projeto_id=projeto_id,
                    usuario_id=1,  # <--- ADICIONADO PARA O BANCO ACEITAR (Modo Demo)
                    tipo_classificado=resultado_ia.get("tipo_classificado", "Código-Fonte"),
                    tags=tags_finais,
                    resumo=resultado_ia.get("resumo", "Arquivo de código-fonte.")
                )

                # Para evitar conflito, repassamos a data atual se a entidade exigir
                from datetime import datetime
                novo_artefato.data_upload = datetime.utcnow()

                self.repository.salvar(novo_artefato)
                salvos += 1

            except Exception as e:
                # <--- AGORA ELE GRITA O ERRO NO CONSOLE DA AZURE!
                print(f"🔴 ERRO FATAL ao processar o arquivo {arq['nome_arquivo']}: {str(e)}")
                falhas += 1

        return {
            "repositorio": nome_repo,
            "arquivos_processados": salvos,
            "arquivos_ignorados": falhas,
            "arquivos_antigos_removidos": arquivos_deletados
        }