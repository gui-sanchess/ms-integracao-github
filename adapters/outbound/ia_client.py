import os
import httpx
from domain.ports import IaClientPort

class HttpIaClientAdapter(IaClientPort):
    def __init__(self):
        # Busca a URL da variável de ambiente da Azure, com fallback para o localhost
        self.ia_service_url = os.getenv("IA_SERVICE_URL", "https://docuia-api-ia.azurewebsites.net/api/analisar")

    async def classificar_documento(self, texto: str) -> dict:
        # Abre um cliente HTTP assíncrono
        async with httpx.AsyncClient() as client:
            try:
                # Envia o texto para a IA
                response = await client.post(
                    self.ia_service_url,
                    json={"texto": texto},
                    timeout=30.0  # Dá até 30 segundos para a IA do Google pensar
                )
                # Se a API der erro (ex: 500), ele levanta uma exceção
                response.raise_for_status()

                # Retorna o JSON com a classificação, tags e resumo
                return response.json()

            except httpx.RequestError as e:
                print(f"Erro ao conectar com o microsserviço de IA: {e}")
                raise Exception("Falha de comunicação com a Inteligência Artificial.")