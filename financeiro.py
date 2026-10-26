import pandas as pd

print("=== SISTEMA FINANCEIRO ===")

# =========================
# RECEITAS
# =========================

receitas = {
    5: 8040.00,
    20: 4800.00,
    30: 1800.00
}

# =========================
# CONTAS
# =========================

contas = pd.read_csv("contas_outubro.csv")

# Classificação das contas
tipos = {
    "Cartão Neon": "Dívida/Cartão",
    "Cartão Atacadão": "Dívida/Cartão",
    "Cartão Bradesco": "Dívida/Cartão",
    "Cartão Dibs": "Dívida/Cartão",
    "Cartão Mais": "Dívida/Cartão",
    "Vestcasa": "Dívida/Compra",
    "Shopee": "Dívida/Compra",
    "Amil": "Fixa",
    "Internet": "Fixa",
    "Água": "Fixa",
    "Energia": "Fixa",
    "INSS": "Fixa"
}

contas["tipo"] = contas["nome"].map(tipos).fillna("Outros")

# =========================
# TRANSPORTE E MORADIA
# =========================

extras = pd.DataFrame([
    {
        "nome": "Transporte dia 05",
        "valor": 150.00,
        "categoria": "Transporte",
        "tipo": "Fixa"
    },
    {
        "nome": "Transporte dia 20",
        "valor": 180.00,
        "categoria": "Transporte",
        "tipo": "Fixa"
    },
    {
        "nome": "Transporte variável",
        "valor": 500.00,
        "categoria": "Transporte",
        "tipo": "Variável"
    },
    {
        "nome": "Aluguel",
        "valor": 1000.00,
        "categoria": "Moradia",
        "tipo": "Fixa"
    }
])

# Remover Peruas porque já está incluída no transporte
contas = contas[contas["nome"] != "Peruas"]

# =========================
# JUNTAR TUDO
# =========================

dados = pd.concat([
    contas[["nome", "valor", "categoria", "tipo"]],
    extras
], ignore_index=True)

# =========================
# ANÁLISE
# =========================

print("\n=== RESUMO POR TIPO ===")

resumo = dados.groupby("tipo")["valor"].sum()

for tipo, valor in resumo.items():
    print(f"{tipo}: R$ {valor:.2f}")

print("\n=== RESUMO POR CATEGORIA ===")

categorias = dados.groupby("categoria")["valor"].sum()

for categoria, valor in categorias.items():
    print(f"{categoria}: R$ {valor:.2f}")

# =========================
# RECEITA
# =========================

receita_total = sum(receitas.values())
despesas_total = dados["valor"].sum()

saldo = receita_total - despesas_total

print("\n=== RESULTADO ===")
print(f"Receita total: R$ {receita_total:.2f}")
print(f"Despesas cadastradas: R$ {despesas_total:.2f}")
print(f"Saldo: R$ {saldo:.2f}")

# =========================
# MAIORES DESPESAS
# =========================

print("\n=== MAIORES DESPESAS ===")

maiores = dados.sort_values(
    by="valor",
    ascending=False
).head(5)

for _, item in maiores.iterrows():
    print(
        f'{item["nome"]}: '
        f'R$ {item["valor"]:.2f} '
        f'[{item["tipo"]}]'
    )