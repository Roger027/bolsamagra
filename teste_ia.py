from openai import OpenAI

client = OpenAI()

resposta = client.responses.create(
    model="gpt-6-luna",
    input="Responda apenas: conexão com a IA funcionando."
)

print(resposta.output_text)
