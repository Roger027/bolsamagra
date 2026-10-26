
from pathlib import Path
import pandas as pd


def converter_valor_csv(valor):
    """Converte valores numéricos em formato brasileiro ou padrão."""
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return float(texto)


def normalizar_valores_obrigacoes(obrigacoes):
    obrigacoes = obrigacoes.copy()
    obrigacoes["valor"] = obrigacoes["valor"].map(converter_valor_csv)
    return obrigacoes


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

    if df["valor"].isna().any():
        raise ValueError("Há valores inválidos no arquivo.")

    try:
        return normalizar_valores_obrigacoes(df)
    except (TypeError, ValueError) as erro:
        raise ValueError("Há valores inválidos no arquivo.") from erro


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