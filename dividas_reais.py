import pandas as pd

print("=== ATUALIZAÇÃO DAS DÍVIDAS ===")

df = pd.read_csv("dividas_reais.csv")

for i in range(len(df)):
    print("\n--------------------------------")
    print(f"Dívida: {df.loc[i, 'nome']}")
    
    saldo = float(input("Saldo devedor atual: R$ "))
    parcelas = int(input("Quantas parcelas faltam? "))
    
    df.loc[i, "saldo_devedor"] = saldo
    df.loc[i, "parcelas_restantes"] = parcelas
    df.loc[i, "status"] = "Em andamento"

df.to_csv(
    "dividas_reais.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== DÍVIDAS ATUALIZADAS ===")

print(
    df[
        [
            "nome",
            "saldo_devedor",
            "parcela",
            "parcelas_restantes",
            "status"
        ]
    ].to_string(index=False)
)

print("\nArquivo atualizado com sucesso!")