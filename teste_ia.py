import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY não encontrada. Configure-a no arquivo .env."
    )

client = OpenAI(api_key=api_key)

resposta = client.responses.create(
    model="gpt-4.1-mini",
    input="Responda apenas: conexão com a IA funcionando."
)

print(resposta.output_text)
