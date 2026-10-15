import pandas as pd

arquivo = "data/movimentacoes_teste.csv"

df = pd.read_csv(arquivo)

print("\n=== BOLSA MAGRA ===")
print("\nMovimentações:")
print(df)

entradas = df.loc[df["tipo"] == "entrada", "valor"].sum()
saidas = df.loc[df["tipo"] == "saida", "valor"].sum()
saldo = entradas - saidas

print("\n=== RESUMO ===")
print(f"Entradas: R$ {entradas:,.2f}")
print(f"Saídas:   R$ {saidas:,.2f}")
print(f"Saldo:    R$ {saldo:,.2f}")

print("\n=== POR PESSOA ===")
print(
	df.groupby(["pessoa", "tipo"])["valor"]
	.sum()
	.round(2)
)
