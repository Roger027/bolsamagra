from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from modulos.finance_store import FinanceStore, FinanceStoreError


PASTA = Path(__file__).resolve().parent
load_dotenv(PASTA / ".env")

ARQUIVOS = [
    "obrigacoes.csv",
    "dividas_reais.csv",
    "faturas.csv",
    "receitas_lancadas.csv",
    "saidas.csv",
    "pagamentos.csv",
]


def main() -> None:
    armazenamento = FinanceStore(PASTA)
    if not armazenamento.is_cloud:
        raise FinanceStoreError(
            "Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no .env local."
        )
    if not armazenamento.is_empty:
        raise FinanceStoreError(
            "O banco já contém dados. A migração foi cancelada para "
            "evitar sobrescrever registros."
        )

    atualizacoes = {}
    for nome in ARQUIVOS:
        caminho = PASTA / nome
        if caminho.exists():
            atualizacoes[caminho] = pd.read_csv(
                caminho,
                encoding="utf-8-sig",
            )
        else:
            atualizacoes[caminho] = pd.DataFrame()

    obrigacoes = atualizacoes[PASTA / "obrigacoes.csv"]
    dividas = atualizacoes[PASTA / "dividas_reais.csv"]
    if obrigacoes.empty or dividas.empty:
        raise FinanceStoreError(
            "obrigacoes.csv e dividas_reais.csv precisam existir e "
            "conter dados antes da migração."
        )

    armazenamento.save_many(atualizacoes)
    print(
        "Migração concluída sem exibir os valores financeiros. "
        f"Arquivos carregados: {len(atualizacoes)}."
    )


if __name__ == "__main__":
    try:
        main()
    except (FinanceStoreError, OSError, pd.errors.ParserError) as erro:
        raise SystemExit(f"Falha na migração: {erro}") from erro
