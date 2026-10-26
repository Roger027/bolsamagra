import pandas as pd

print("=== CONTROLE DE CAIXA ===")

# =========================
# RECEITAS
# =========================

receitas = pd.DataFrame([
    {"data": "05/10/2026", "descricao": "Receita", "valor": 8040.00},
    {"data": "20/10/2026", "descricao": "Receita", "valor": 4800.00},
    {"data": "30/10/2026", "descricao": "Receita", "valor": 1800.00}
])

receitas["data"] = pd.to_datetime(
    receitas["data"],
    dayfirst=True
)

# =========================
# FATURAS
# =========================

faturas = pd.read_csv("faturas.csv")

faturas["data"] = pd.to_datetime(
    faturas["vencimento"],
    dayfirst=True
)

faturas = faturas.rename(
    columns={"valor": "valor_saida"}
)

# =========================
# MOVIMENTAÇÕES
# =========================

entradas = receitas[
    ["data", "descricao", "valor"]
].copy()

entradas["tipo"] = "ENTRADA"

entradas = entradas.rename(
    columns={"valor": "valor_movimento"}
)

saidas = faturas[
    ["data", "nome", "valor_saida"]
].copy()

saidas = saidas.rename(
    columns={"nome": "descricao"}
)

saidas["tipo"] = "SAÍDA"
saidas["valor_movimento"] = -saidas["valor_saida"]

saidas = saidas[
    ["data", "descricao", "valor_movimento", "tipo"]
]

movimentos = pd.concat(
    [entradas, saidas],
    ignore_index=True
)

movimentos = movimentos.sort_values("data")

# =========================
# SALDO ACUMULADO
# =========================

movimentos["saldo"] = movimentos["valor_movimento"].cumsum()

print("\n=== MOVIMENTAÇÃO ===")

for _, item in movimentos.iterrows():

    sinal = "+" if item["valor_movimento"] >= 0 else ""

    print(
        f'{item["data"].strftime("%d/%m/%Y")} | '
        f'{item["tipo"]:7} | '
        f'{item["descricao"]:20} | '
        f'{sinal}R$ {item["valor_movimento"]:.2f} | '
        f'Saldo: R$ {item["saldo"]:.2f}'
    )

print("\n=== RESULTADO ===")

print(
    f"Saldo final das movimentações cadastradas: "
    f"R$ {movimentos['saldo'].iloc[-1]:.2f}"
)
