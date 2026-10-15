import pandas as pd

print("=== ANÁLISE DAS DÍVIDAS ===")

df = pd.read_csv("dividas_reais.csv")

# Total da dívida
total = df["saldo_devedor"].sum()

# Total das parcelas mensais
parcelas = df["parcela"].sum()

print(f"\nSaldo total das dívidas: R$ {total:.2f}")
print(f"Parcelas/faturas cadastradas: R$ {parcelas:.2f}")

print("\n=== PARTICIPAÇÃO DE CADA DÍVIDA ===")

df["percentual"] = (df["saldo_devedor"] / total) * 100

df = df.sort_values(
    by="saldo_devedor",
    ascending=False
)

for _, divida in df.iterrows():
    print(
        f'{divida["nome"]}: '
        f'R$ {divida["saldo_devedor"]:.2f} '
        f'({divida["percentual"]:.1f}%)'
    )

print("\n=== MAIOR SALDO ===")

maior = df.iloc[0]

print(f'Credor: {maior["nome"]}')
print(f'Saldo: R$ {maior["saldo_devedor"]:.2f}')
print(f'Parcela: R$ {maior["parcela"]:.2f}')

print("\n=== DÍVIDAS COM SALDO ZERO ===")

zeradas = df[df["saldo_devedor"] == 0]

for _, divida in zeradas.iterrows():
    print(divida["nome"])