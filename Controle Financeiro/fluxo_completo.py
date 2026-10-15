import pandas as pd

print("=== FLUXO FINANCEIRO COMPLETO ===")

# ==========================================
# RECEITAS
# ==========================================

receitas = pd.DataFrame([
    {"data": "05/10/2026", "descricao": "Receita", "valor": 8040.00},
    {"data": "20/10/2026", "descricao": "Receita", "valor": 4800.00},
    {"data": "30/10/2026", "descricao": "Receita", "valor": 1800.00}
])

receitas["data"] = pd.to_datetime(
    receitas["data"],
    dayfirst=True
)

receitas["tipo"] = "ENTRADA"

# ==========================================
# CONTAS DE OUTUBRO
# ==========================================

contas = pd.read_csv("contas_outubro.csv")

# Peruas NÃO entram aqui porque já estão
# incluídas no transporte mensal de R$830.
contas = contas[contas["nome"] != "Peruas"]

# Corrige o INSS para R$360
contas.loc[
    contas["nome"] == "INSS",
    "valor"
] = 360.00

# As contas cadastradas vencem em 05/10
contas["data"] = pd.to_datetime(
    "05/10/2026",
    dayfirst=True
)

contas = contas.rename(
    columns={
        "nome": "descricao",
        "valor": "valor"
    }
)

contas["tipo"] = "SAÍDA"

contas = contas[
    ["data", "descricao", "valor", "tipo"]
]

# ==========================================
# FATURAS FUTURAS
# ==========================================

faturas = pd.read_csv("faturas.csv")

faturas["data"] = pd.to_datetime(
    faturas["vencimento"],
    dayfirst=True
)

faturas = faturas.rename(
    columns={
        "nome": "descricao",
        "valor": "valor"
    }
)

faturas["tipo"] = "SAÍDA"

faturas = faturas[
    ["data", "descricao", "valor", "tipo"]
]

# ==========================================
# TRANSPORTE
# ==========================================

transporte = pd.DataFrame([
    {
        "data": "05/10/2026",
        "descricao": "Transporte",
        "valor": 150.00,
        "tipo": "SAÍDA"
    },
    {
        "data": "20/10/2026",
        "descricao": "Transporte",
        "valor": 180.00,
        "tipo": "SAÍDA"
    },
    {
        "data": "30/10/2026",
        "descricao": "Transporte variável",
        "valor": 500.00,
        "tipo": "SAÍDA"
    }
])

transporte["data"] = pd.to_datetime(
    transporte["data"],
    dayfirst=True
)

# ==========================================
# ALUGUEL
# ==========================================

aluguel = pd.DataFrame([
    {
        "data": "30/10/2026",
        "descricao": "Aluguel",
        "valor": 1000.00,
        "tipo": "SAÍDA"
    }
])

aluguel["data"] = pd.to_datetime(
    aluguel["data"],
    dayfirst=True
)

# ==========================================
# UNIFICAR TUDO
# ==========================================

movimentos = pd.concat(
    [
        receitas,
        contas,
        faturas,
        transporte,
        aluguel
    ],
    ignore_index=True
)

# Entradas positivas
# Saídas negativas
movimentos.loc[
    movimentos["tipo"] == "SAÍDA",
    "valor"
] *= -1

# Ordenar cronologicamente
movimentos = movimentos.sort_values(
    by=["data", "tipo"]
)

# ==========================================
# SALDO ACUMULADO
# ==========================================

movimentos["saldo"] = movimentos["valor"].cumsum()

# ==========================================
# EXIBIR
# ==========================================

print("\n=== MOVIMENTAÇÃO CRONOLÓGICA ===")

for _, item in movimentos.iterrows():

    valor = item["valor"]

    sinal = "+" if valor >= 0 else ""

    print(
        f'{item["data"].strftime("%d/%m/%Y")} | '
        f'{item["tipo"]:7} | '
        f'{item["descricao"]:22} | '
        f'{sinal}R$ {valor:.2f} | '
        f'Saldo: R$ {item["saldo"]:.2f}'
    )

# ==========================================
# RESUMO
# ==========================================

total_receitas = movimentos.loc[
    movimentos["tipo"] == "ENTRADA",
    "valor"
].sum()

total_saidas = -movimentos.loc[
    movimentos["tipo"] == "SAÍDA",
    "valor"
].sum()

saldo_final = movimentos["valor"].sum()

print("\n=== RESUMO ===")
print(f"Receitas: R$ {total_receitas:.2f}")
print(f"Saídas:   R$ {total_saidas:.2f}")
print(f"Saldo:    R$ {saldo_final:.2f}")
