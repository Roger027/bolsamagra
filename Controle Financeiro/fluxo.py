

import pandas as pd

print("=== FLUXO DE CAIXA ===")

# Faturas de outubro
contas = pd.read_csv("contas_outubro.csv")
total_faturas = contas["valor"].sum()

# Despesas recorrentes ainda não incluídas nas faturas
despesas_fixas = {
    "Aluguel": 1000.00,
    "Transporte": 830.00
}

total_fixas = sum(despesas_fixas.values())

# Receitas
print("\n--- RECEITAS ---")
trabalho = float(input("Receita do trabalho: R$ "))
esposa = float(input("Receita da esposa: R$ "))
outras = float(input("Outras receitas: R$ "))

receita_total = trabalho + esposa + outras

# Cálculos
total_despesas = total_faturas + total_fixas
saldo = receita_total - total_despesas

print("\n--- DESPESAS FIXAS ---")
for nome, valor in despesas_fixas.items():
    print(f"{nome}: R$ {valor:.2f}")

print(f"\nFaturas: R$ {total_faturas:.2f}")
print(f"Despesas fixas: R$ {total_fixas:.2f}")
print(f"Total de despesas: R$ {total_despesas:.2f}")

print("\n=== RESULTADO ===")
print(f"Receita total: R$ {receita_total:.2f}")
print(f"Saldo preliminar: R$ {saldo:.2f}")

if saldo < 0:
    print("ATENÇÃO: despesas superiores às receitas.")
else:
    print("Saldo positivo antes das despesas não cadastradas.")

    # Faturas de outubro
contas = pd.read_csv("contas_outubro.csv")

# Peruas já está incluída no transporte mensal
total_faturas = contas.loc[
    contas["nome"] != "Peruas", "valor"
].sum()

# Despesas recorrentes
despesas_fixas = {
    "Aluguel": 1000.00,
    "Transporte total": 830.00
}

total_fixas = sum(despesas_fixas.values())

# Cálculo
total_despesas = total_faturas + total_fixas
saldo = receita_total - total_despesas

print("\n=== FLUXO CORRIGIDO ===")
print(f"Faturas sem Peruas: R$ {total_faturas:.2f}")
print(f"Aluguel e transporte: R$ {total_fixas:.2f}")
print(f"Total de despesas: R$ {total_despesas:.2f}")
print(f"Receitas: R$ {receita_total:.2f}")
print(f"Saldo preliminar: R$ {saldo:.2f}")