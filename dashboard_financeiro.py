import pandas as pd
import matplotlib.pyplot as plt

obrigacoes = pd.read_csv("obrigacoes.csv")

# ==============================
# RESUMO
# ==============================

receitas = 14640.00
obrigacoes_outubro = 5660.03
novembro = 1257.00
dividas = 2649.00

saldo = receitas - obrigacoes_outubro

# ==============================
# GRÁFICO 1
# ==============================

dados = pd.Series({
    "Receitas": receitas,
    "Obrigações Outubro": obrigacoes_outubro,
    "Saldo Projetado": saldo
})

dados.plot(kind="bar")

plt.title("Visão Financeira - Outubro")
plt.ylabel("Valor (R$)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.show()

# ==============================
# GRÁFICO 2
# ==============================

dados2 = pd.Series({
    "Novembro": novembro,
    "Dívidas": dividas
})

dados2.plot(kind="bar")

plt.title("Compromissos Futuros")
plt.ylabel("Valor (R$)")
plt.xticks(rotation=0)
plt.tight_layout()

plt.show()

print("=== DASHBOARD FINANCEIRO ===")
print(f"Receitas: R$ {receitas:.2f}")
print(f"Obrigações outubro: R$ {obrigacoes_outubro:.2f}")
print(f"Saldo projetado: R$ {saldo:.2f}")
print(f"Novembro comprometido: R$ {novembro:.2f}")
print(f"Dívidas reais: R$ {dividas:.2f}")