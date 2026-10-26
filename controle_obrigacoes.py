import pandas as pd
from pathlib import Path

# ==============================
# 1. CONTAS DE OUTUBRO
# ==============================

contas = pd.read_csv("contas_outubro.csv")

# Peruas já está incluído nos R$ 830 de transporte
# Vestcasa de R$ 589,37 não será considerada
contas = contas[
    (contas["nome"] != "Peruas") &
    (contas["nome"] != "Vestcasa")
]

contas["vencimento"] = "05/10/2026"
contas["origem"] = "Conta Outubro"
contas["status"] = "Pendente"

contas = contas[
    ["origem", "nome", "valor", "vencimento", "status"]
]

# ==============================
# 2. FATURAS
# ==============================

faturas = pd.read_csv("faturas.csv")

faturas = faturas[
    ["nome", "valor", "vencimento", "status"]
]

faturas["origem"] = "Fatura"

faturas = faturas[
    ["origem", "nome", "valor", "vencimento", "status"]
]

# ==============================
# 3. OBRIGAÇÕES FIXAS
# ==============================

fixas = pd.DataFrame([
    {
        "origem": "Obrigação Mensal",
        "nome": "Transporte",
        "valor": 830.00,
        "vencimento": "Mensal",
        "status": "Planejado"
    },
    {
        "origem": "Obrigação Mensal",
        "nome": "Aluguel",
        "valor": 1000.00,
        "vencimento": "30/10/2026",
        "status": "Pendente"
    }
])

# ==============================
# 4. UNIFICAR
# ==============================

obrigacoes = pd.concat(
    [contas, faturas, fixas],
    ignore_index=True
)

# Reaplica pagamentos registrados no dashboard quando a tabela é recriada.
arquivo_pagamentos = Path(__file__).resolve().parent / "pagamentos.csv"
if arquivo_pagamentos.exists():
    pagamentos = pd.read_csv(
        arquivo_pagamentos,
        encoding="utf-8-sig"
    )
    colunas_pagamentos = {
        "tipo",
        "origem",
        "nome",
        "vencimento",
        "indice_registro",
        "valor_pago",
        "status_apos",
    }
    faltantes = colunas_pagamentos - set(pagamentos.columns)
    if faltantes:
        raise ValueError(
            "Colunas ausentes em pagamentos.csv: "
            + ", ".join(sorted(faltantes))
        )

    pagamentos_reaplicados = 0
    pagamentos_sem_correspondencia = 0

    for _, pagamento in pagamentos.iterrows():
        if (
            pagamento["tipo"] != "Conta/fatura"
            or pagamento["status_apos"] != "Pago"
        ):
            continue

        indice = int(pagamento["indice_registro"])
        if indice < 0 or indice >= len(obrigacoes):
            pagamentos_sem_correspondencia += 1
            continue

        obrigacao = obrigacoes.loc[indice]
        corresponde = (
            str(obrigacao["origem"]) == str(pagamento["origem"])
            and str(obrigacao["nome"]) == str(pagamento["nome"])
            and str(obrigacao["vencimento"])
            == str(pagamento["vencimento"])
            and round(float(obrigacao["valor"]), 2)
            == round(float(pagamento["valor_pago"]), 2)
        )

        if corresponde:
            obrigacoes.at[indice, "status"] = "Pago"
            pagamentos_reaplicados += 1
        else:
            pagamentos_sem_correspondencia += 1

    print(
        f"Pagamentos reaplicados: {pagamentos_reaplicados}; "
        f"sem correspondência com a tabela recriada: "
        f"{pagamentos_sem_correspondencia}."
    )

# ==============================
# 5. EXIBIR
# ==============================

print("=== CONTROLE DE OBRIGAÇÕES ===\n")

print(obrigacoes.to_string(index=False))

print("\n=== TOTAL DAS OBRIGAÇÕES ===")

total = obrigacoes["valor"].sum()

print(f"Total: R$ {total:.2f}")

# ==============================
# 6. RESUMO POR ORIGEM
# ==============================

print("\n=== RESUMO POR ORIGEM ===")

resumo = obrigacoes.groupby("origem")["valor"].sum()

print(resumo)

# ==============================
# 7. SALVAR
# ==============================

obrigacoes.to_csv(
    "obrigacoes.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo obrigacoes.csv atualizado com sucesso.")