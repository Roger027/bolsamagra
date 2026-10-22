import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Força o carregamento do .env na mesma pasta do app.py
pasta_atual = Path(__file__).resolve().parent
caminho_env = pasta_atual / ".env"
load_dotenv(dotenv_path=caminho_env)

# Captura as variáveis
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Validação de segurança para te ajudar a debugar
if not url or not key:
    raise ValueError(
        f"Erro: Variáveis não encontradas!\n"
        f"Procurando em: {caminho_env}\n"
        f"O arquivo existe? {caminho_env.exists()}"
    )

supabase: Client = create_client(url, key)
print("Conectado ao Supabase com sucesso!")
