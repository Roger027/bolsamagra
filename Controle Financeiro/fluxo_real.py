import pandas as pd

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

calendario = []

# Faturas com vencimento no dia 05
for _, conta in contas.iterrows():

    # Peruas já está dentro do transporte
    if conta["nome"] != "Peruas":
        calendario.append({
            "dia": 5,
            "tipo": "SAÍDA",
            "nome": conta["nome"],
            "valor": float(conta["valor"])
        })

# Transporte
calendario.append({
    "dia": 5,
    "tipo": "SAÍDA",
    "nome": "Transporte",
    "valor": 150.00
})

calendario.append({
    "dia": 20,
    "tipo": "SAÍDA",
    "nome": "Transporte",
    "valor": 180.00
})
calendario.append({
    "dia": 30,
    "tipo": "SAÍDA",
    "nome": "Transporte variável",
    "valor": 500.00
})

# Aluguel
calendario.append({
    "dia": 30,
    "tipo": "SAÍDA",
    "nome": "Aluguel",
    "valor": 1000.00
})

# =========================
# FLUXO
# =========================

saldo = 0

print("=== FLUXO FINANCEIRO DE OUTUBRO ===")

for dia in sorted(set(list(receitas.keys()) +
                      [item["dia"] for item in calendario])):

    entrada = receitas.get(dia, 0)

    saidas = [
        item for item in calendario
        if item["dia"] == dia
    ]

    total_saidas = sum(item["valor"] for item in saidas)

    saldo += entrada
    saldo -= total_saidas

    print(f"\n===== DIA {dia:02d}/10 =====")

    if entrada > 0:
        print(f"ENTRADA: R$ {entrada:.2f}")

    for item in saidas:
        print(
            f'SAÍDA - {item["nome"]}: '
            f'R$ {item["valor"]:.2f}'
        )

    print(f"TOTAL SAÍDAS: R$ {total_saidas:.2f}")
    print(f"SALDO ACUMULADO: R$ {saldo:.2f}")

print("\n==============================")
print(f"SALDO FINAL PROJETADO: R$ {saldo:.2f}")
print("==============================")