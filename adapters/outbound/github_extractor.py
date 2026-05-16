import os
import tempfile
import git
from pathlib import Path
from typing import List, Dict


class GithubExtractorAdapter:
    def extrair_arquivos(self, url_repo: str, token: str = None) -> List[Dict[str, str]]:
        arquivos_uteis = []
        extensoes_permitidas = ['.md', '.py', '.js', '.java', '.txt', '.html', '.ts']
        nome_repo = url_repo.split("/")[-1].replace(".git", "")

        # MÁGICA DA AUTENTICAÇÃO
        # Se veio um token, nós embutimos ele na URL: https://TOKEN@github.com/usuario/repo
        url_clone = url_repo
        if token:
            url_clone = url_repo.replace("https://", f"https://{token}@")

        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Clonando {nome_repo} em {temp_dir}...")
            # Usa a URL autenticada (ou a normal se for público)
            git.Repo.clone_from(url_clone, temp_dir)

            for root, dirs, files in os.walk(temp_dir):
                if '.git' in root:
                    continue

                for file in files:
                    ext = Path(file).suffix
                    if ext in extensoes_permitidas:
                        caminho_completo = os.path.join(root, file)
                        try:
                            with open(caminho_completo, 'r', encoding='utf-8') as f:
                                conteudo = f.read()
                                if conteudo.strip():
                                    arquivos_uteis.append({
                                        "nome_arquivo": file,
                                        "conteudo": conteudo,
                                        "nome_repo": nome_repo
                                    })
                        except Exception:
                            pass

        return arquivos_uteis