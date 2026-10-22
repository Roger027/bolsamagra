import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


PASTA_PROJETO = Path(__file__).resolve().parents[1]
load_dotenv(PASTA_PROJETO / ".env")


# Recupera a chave do Gemini
api_key = os.getenv("GEMINI_API_KEY")


# Verifica se a chave existe
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY não encontrada. "
        "Verifique o arquivo .env."
    )


# Cria o cliente Gemini
client = genai.Client(api_key=api_key)


# Faz um teste simples
resposta = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Responda somente: TESTE DO BOLSA MAGRA FUNCIONANDO."
)


print(resposta.text)