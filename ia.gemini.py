import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Localiza a pasta principal do projeto
PASTA_PROJETO = Path(__file__).resolve().parent

# Carrega as variáveis do arquivo .env
load_dotenv(PASTA_PROJETO / ".env")

# Recupera a chave
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: Chave GEMINI_API_KEY não encontrada.")
    print("Verifique o arquivo .env na pasta principal.")
    raise SystemExit(1)

print("Chave encontrada. Iniciando conexão...")

# Cria o cliente
client = genai.Client(api_key=api_key)

# Envia uma pergunta de teste
resposta = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=(
        "Você é um assistente financeiro. "
        "Responda em português: "
        "Explique em duas frases o que é uma reserva de emergência."
    )
)

print("\nResposta do Gemini:")
print(resposta.text)