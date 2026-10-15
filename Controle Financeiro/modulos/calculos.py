
from pathlib import Path
import pandas as pd


# Localiza a pasta principal do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO = PASTA_PROJETO / "obrigacoes.csv"


def carregar_obrigacoes():
    """Carrega as obrigações financeiras do CSV."""
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO}"
        )

    df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")

    colunas = {"origem", "nome", "valor", "vencimento", "status"}
    faltantes = colunas - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Colunas ausentes no CSV: {faltantes}"
        )

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    if df["valor"].isna().any():
        raise ValueError("Há valores inválidos no arquivo.")

    return df


def calcular_obrigacoes():
    """Separa obrigações pendentes das previsões de orçamento."""
    df = carregar_obrigacoes()

    pendentes = df[
        df["status"].str.strip().str.lower() == "pendente"
    ]

    planejadas = df[
        df["status"].str.strip().str.lower() == "planejado"
    ]

    total_pendente = pendentes["valor"].sum()
    total_planejado = planejadas["valor"].sum()

    return {
        "quantidade_pendentes": len(pendentes),
        "total_pendente": total_pendente,
        "quantidade_planejadas": len(planejadas),
        "total_planejado": total_planejado,
        "detalhes_pendentes": pendentes,
        "detalhes_planejados": planejadas,
    }


if __name__ == "__main__":
    resultado = calcular_obrigacoes()

    print("\n=== BOLSA MAGRA: OBRIGAÇÕES ===")
    print(
        f"Contas pendentes: "
        f"{resultado['quantidade_pendentes']}"
    )
    print(
        f"Total pendente: "
        f"R$ {resultado['total_pendente']:,.2f}"
    )
    print(
        f"Orçamentos planejados: "
        f"{resultado['quantidade_planejadas']}"
    )
    print(
        f"Total planejado: "
        f"R$ {resultado['total_planejado']:,.2f}"
    )

    print("\n=== DETALHES ===")
    print(
        resultado["detalhes_pendentes"][
            ["nome", "valor", "vencimento"]
        ].to_string(index=False)
    )