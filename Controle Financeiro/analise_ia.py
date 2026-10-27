# ==============================
# LER RELATÓRIO FINANCEIRO
# ==============================


from pathlib import Path

PASTA = Path(__file__).resolve().parent
arquivo_relatorio = PASTA / "relatorio_ia.txt"
arquivo_prompt = PASTA / "prompt_ia.txt"

if not arquivo_relatorio.exists():
    raise FileNotFoundError(
        f"Relatório não encontrado: {arquivo_relatorio}"
    )

relatorio = arquivo_relatorio.read_text(encoding="utf-8")

prompt = f"""
Você é um assistente de análise financeira do projeto Bolsa Magra.

REGRAS:
- Não invente valores nem complete lacunas com suposições.
- Não crie dívidas que não estejam informadas.
- Não trate saldo devedor como saída de caixa automática.
- Diferencie dinheiro disponível, obrigações futuras e dívidas.
- Se faltar informação, declare explicitamente o que falta.
- Preserve os valores e as datas presentes no relatório.

Analise:
1. Situação do caixa.
2. Obrigações futuras.
3. Saldo devedor.
4. Pontos de atenção.
5. Inconsistências e dados ausentes.
6. Perguntas necessárias para melhorar o controle.

DADOS DO RELATÓRIO:
{relatorio}
"""

arquivo_prompt.write_text(prompt, encoding="utf-8")

print("Relatório encontrado:", arquivo_relatorio)
print("Tamanho do relatório:", len(relatorio), "caracteres")
print("Linhas do relatório:", len(relatorio.splitlines()))
print("Tamanho do prompt:", len(prompt), "caracteres")
print("Prompt salvo em:", arquivo_prompt)
print("O relatório está vazio:", not bool(relatorio.strip()))