

import pandas as pd

contas = pd.read_csv("contas_outubro.csv")

# Faturas do dia 05, exceto Peruas,
# que já faz parte do transporte
calendario = []

for _, conta in contas.iterrows():
    if conta["nome"] != "Peruas":
        calendario.append({
            "dia": 5,
            "nome": conta["nome"],
            "valor": float(conta["valor"])
        })

# Transporte com datas conhecidas e aluguel
calendario.extend([
    {"dia": 5, "nome": "Transporte", "valor": 150.00},
    {"dia": 20, "nome": "Transporte", "valor": 180.00},
    {"dia": 30, "nome": "Aluguel", "valor": 1000.00}
])

# Saldo inicial disponível em 01/10
saldo = float(input("Dinheiro disponível em 01/10: R$ "))

print("\n=== SALDO POR VENCIMENTO ===")

total_compromissos = 0

for dia in sorted(set(item["dia"] for item in calendario)):
    itens = [item for item in calendario if item["dia"] == dia]
    subtotal = sum(item["valor"] for item in itens)

    total_compromissos += subtotal
    saldo -= subtotal

    print(f"\nDia {dia:02d}/10")
    for item in itens:
        print(f'{item["nome"]}: R$ {item["valor"]:.2f}')

    print(f"Total do dia: R$ {subtotal:.2f}")
    print(f"Compromissos acumulados: R$ {total_compromissos:.2f}")
    print(f"Saldo projetado: R$ {saldo:.2f}")

print("\n=== RESUMO ===")
print(f"Total agendado: R$ {total_compromissos:.2f}")
print("Transporte variável pendente: R$ 500.00")
print("Não foram consideradas receitas futuras por data.")

#O que esperamos aprender com isso:

#iterrows() percorre as linhas do CSV.

#extend() acrescenta compromissos ao calendário.

#sort() organiza os pagamentos por data.

#set() evita repetir a impressão dos mesmos dias.