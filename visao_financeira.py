import pandas as pd

# ==============================
# 1. RECEITAS DE OUTUBRO
# ==============================

receitas = pd.DataFrame([
    {"data": "05/10/2026", "valor": 8040.00},
    {"data": "20/10/2026", "valor": 4800.00},
    {"data": "30/10/2026", "valor": 1800.00}
])

total_receitas = receitas["valor"].sum()

# ==============================
# 2. OBRIGAÇÕES
# ==============================

obrigacoes = pd.read_csv("obrigacoes.csv")

# Somente o que pertence a outubro
obrigacoes_outubro = obrigacoes[
    (
        (obrigacoes["vencimento"] == "05/10/2026") |
        (obrigacoes["vencimento"] == "21/10/2026") |
        (obrigacoes["vencimento"] == "30/10/2026")
    )
]

total_outubro = obrigacoes_outubro["valor"].sum()

# ==============================
# 3. NOVEMBRO
# ==============================

obrigacoes_novembro = obrigacoes[
    (
        (obrigacoes["vencimento"] == "10/11/2026") |
        (obrigacoes["vencimento"] == "21/11/2026")
    )
]

total_novembro = obrigacoes_novembro["valor"].sum()

# ==============================
# 4. RESULTADO
# ==============================

saldo_outubro = total_receitas - total_outubro

# ==============================
# 5. DÍVIDAS REAIS
# ==============================

dividas = pd.read_csv("dividas_reais.csv")

saldo_dividas = dividas["saldo_devedor"].sum()

# ==============================
# 6. PAINEL
# ==============================

print("=" * 45)
print("       VISÃO FINANCEIRA")
print("=" * 45)

print("\n=== OUTUBRO ===")
print(f"Receitas:              R$ {total_receitas:,.2f}")
print(f"Obrigações:            R$ {total_outubro:,.2f}")
print(f"Saldo após obrigações: R$ {saldo_outubro:,.2f}")

print("\n=== NOVEMBRO JÁ COMPROMETIDO ===")
print(f"Obrigações:            R$ {total_novembro:,.2f}")

print("\n=== DÍVIDAS REAIS ===")
print(f"Saldo devedor:         R$ {saldo_dividas:,.2f}")

print("\n=== RESUMO ===")
print(f"Dinheiro que entra:    R$ {total_receitas:,.2f}")
print(f"Saídas de outubro:     R$ {total_outubro:,.2f}")
print(f"Saldo projetado:       R$ {saldo_outubro:,.2f}")
print(f"Novembro comprometido: R$ {total_novembro:,.2f}")
print(f"Dívidas cadastradas:   R$ {saldo_dividas:,.2f}")

print("=" * 45)