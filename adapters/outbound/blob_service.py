import os
import uuid
from azure.storage.blob import BlobServiceClient


class AzureBlobStorageAdapter:
    def __init__(self):
        # Vai puxar as credenciais das variáveis de ambiente da Azure
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME", "documentos")

        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

    async def upload_arquivo(self, conteudo_bytes: bytes, nome_arquivo: str) -> str:
        if not self.connection_string:
            print("AVISO: Credenciais do Azure Blob não configuradas. Pulando upload físico.")
            return None

        # Cria um nome único para não sobrescrever arquivos no Blob
        extensao = f".{nome_arquivo.split('.')[-1]}" if "." in nome_arquivo else ".txt"
        nome_blob = f"{uuid.uuid4()}{extensao}"

        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=nome_blob)

        # Faz o upload dos bytes
        blob_client.upload_blob(conteudo_bytes, overwrite=True)

        # Retorna a URL pública do arquivo
        return blob_client.url