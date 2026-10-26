import pandas as pd

# ==============================
# DADOS FINANCEIROS
# ==============================

receitas = 14640.00
obrigacoes_outubro = 5660.03
novembro_comprometido = 1257.00
dividas = 2649.00

saldo = receitas - obrigacoes_outubro

# ==============================
# ANÁLISE AUTOMÁTICA
# ==============================

if saldo < 0:
    situacao = "CAIXA NEGATIVO"
elif saldo < 2000:
    situacao = "ATENÇÃO"
else:
    situacao = "CAIXA POSITIVO"

# ==============================
# RELATÓRIO PARA IA
# ==============================

relatorio = f"""
RELATÓRIO FINANCEIRO

Receitas de outubro: R$ {receitas:.2f}

Obrigações de outubro: R$ {obrigacoes_outubro:.2f}

Saldo projetado de outubro: R$ {saldo:.2f}

Obrigações já previstas para novembro: R$ {novembro_comprometido:.2f}

Saldo devedor cadastrado: R$ {dividas:.2f}

Situação do caixa: {situacao}
"""

print(relatorio)

# Salvar para futura integração com IA
with open("relatorio_ia.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write(relatorio)

print("Relatório salvo em relatorio_ia.txt")