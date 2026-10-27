import pandas as pd

print("=== CALENDÁRIO DE VENCIMENTOS ===")

faturas = pd.read_csv("faturas.csv")

# Converte a data para o formato de data
faturas["vencimento"] = pd.to_datetime(
    faturas["vencimento"],
    dayfirst=True
)

# Ordena por vencimento
faturas = faturas.sort_values("vencimento")

print("\n=== FATURAS POR DATA ===")

for data, grupo in faturas.groupby("vencimento"):
    total = grupo["valor"].sum()

    print("\n" + "-" * 40)
    print(f"Vencimento: {data.strftime('%d/%m/%Y')}")

    for _, fatura in grupo.iterrows():
        print(
            f'{fatura["nome"]}: '
            f'R$ {fatura["valor"]:.2f} '
            f'[{fatura["status"]}]'
        )

    print(f"TOTAL DA DATA: R$ {total:.2f}")

print("\n=== TOTAL DAS FATURAS ===")

total_geral = faturas["valor"].sum()

print(f"Total: R$ {total_geral:.2f}")
