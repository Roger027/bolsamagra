import pandas as pd

arquivo = "contas_outubro.csv"

df = pd.read_csv(arquivo)

df.loc[df["nome"] == "INSS", "valor"] = 360.00

df.to_csv(
    arquivo,
    index=False,
    encoding="utf-8-sig"
)

print("INSS atualizado para R$ 360,00.")
print("R$ 180,00 - Pessoa 1")
print("R$ 180,00 - Pessoa 2")