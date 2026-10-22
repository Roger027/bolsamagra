import pandas as pd
import pytest

from modulos.finance_store import FinanceStore
from modulos.pagamentos import (
    COLUNAS_HISTORICO_PAGAMENTOS,
    carregar_historico_pagamentos,
    ordenar_historico_pagamentos,
)


def test_payment_history_is_sorted_newest_first():
    historico = pd.DataFrame([
        {
            "data_pagamento": "04/10/2026",
            "tipo": "Conta/fatura",
            "nome": "Conta antiga",
        },
        {
            "data_pagamento": "21/10/2026",
            "tipo": "Dívida",
            "nome": "Pagamento recente",
        },
        {
            "data_pagamento": "data inválida",
            "tipo": "Dívida",
            "nome": "Data inválida",
        },
    ])

    ordenado = ordenar_historico_pagamentos(historico)

    assert ordenado["nome"].tolist() == [
        "Pagamento recente",
        "Conta antiga",
        "Data inválida",
    ]
    assert "_data_ordenacao" not in ordenado.columns


def test_payment_history_requires_all_expected_columns(tmp_path):
    class Store:
        def read_csv(self, _arquivo, columns=None):
            return pd.DataFrame(columns=columns[:-1])

    with pytest.raises(ValueError, match="status_apos"):
        carregar_historico_pagamentos(Store(), tmp_path / "pagamentos.csv")


def test_payment_and_history_are_saved_together_locally(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    store = FinanceStore(tmp_path)
    arquivo_obrigacoes = tmp_path / "obrigacoes.csv"
    arquivo_pagamentos = tmp_path / "pagamentos.csv"
    obrigacoes = pd.DataFrame([
        {
            "nome": "Conta",
            "valor": 100.0,
            "status": "Pendente",
        }
    ])
    registro = {
        "data_pagamento": "21/10/2026",
        "tipo": "Conta/fatura",
        "origem": "Conta",
        "nome": "Conta",
        "vencimento": "21/10/2026",
        "indice_registro": 0,
        "valor_pago": 100.0,
        "saldo_apos": 0.0,
        "status_apos": "Pago",
    }
    obrigacoes.at[0, "status"] = "Pago"

    store.save_many({
        arquivo_obrigacoes: obrigacoes,
        arquivo_pagamentos: pd.DataFrame(
            [registro],
            columns=COLUNAS_HISTORICO_PAGAMENTOS,
        ),
    })

    recarregado = FinanceStore(tmp_path)
    historico = carregar_historico_pagamentos(
        recarregado,
        arquivo_pagamentos,
    )

    assert recarregado.read_csv(arquivo_obrigacoes).at[0, "status"] == "Pago"
    assert historico.to_dict("records") == [registro]
