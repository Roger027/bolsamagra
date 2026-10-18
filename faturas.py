import pandas as pd

faturas = [
    {
        "nome": "Nubank",
        "valor": 1892.00,
        "vencimento": "21/10/2026",
        "status": "Pendente"
    },
    {
        "nome": "Nubank",
        "valor": 600.00,
        "vencimento": "21/11/2026",
        "status": "Próxima"
    },
    {
        "nome": "Vestcasa",
        "valor": 657.00,
        "vencimento": "10/11/2026",
        "status": "Pendente"
    }
]

df = pd.DataFrame(faturas)

print("=== FATURAS FUTURAS ===")
print(df.to_string(index=False))

print("\n=== TOTAL ===")
print(f"Total: R$ {df['valor'].sum():.2f}")

df.to_csv(
    "faturas.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo faturas.csv criado com sucesso!")