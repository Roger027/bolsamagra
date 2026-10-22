<<<<<<< HEAD
import pandas as pd


COLUNAS_HISTORICO_PAGAMENTOS = [
    "data_pagamento",
    "tipo",
    "origem",
    "nome",
    "vencimento",
    "indice_registro",
    "valor_pago",
    "saldo_apos",
    "status_apos",
]


def carregar_historico_pagamentos(armazenamento, arquivo):
    historico = armazenamento.read_csv(
        arquivo,
        columns=COLUNAS_HISTORICO_PAGAMENTOS,
    )
    faltantes = set(COLUNAS_HISTORICO_PAGAMENTOS) - set(historico.columns)
    if faltantes:
        raise ValueError(
            "Colunas ausentes no histórico de pagamentos: "
            + ", ".join(sorted(faltantes))
        )

    return historico[COLUNAS_HISTORICO_PAGAMENTOS]


def ordenar_historico_pagamentos(historico):
    historico_com_data = historico.assign(
        _data_ordenacao=pd.to_datetime(
            historico["data_pagamento"],
            format="%d/%m/%Y",
            errors="coerce",
        )
    )
    return (
        historico_com_data.sort_values(
            "_data_ordenacao",
            ascending=False,
            kind="stable",
        )
        .drop(columns="_data_ordenacao")
    )
=======
import pandas as pd


COLUNAS_HISTORICO_PAGAMENTOS = [
    "data_pagamento",
    "tipo",
    "origem",
    "nome",
    "vencimento",
    "indice_registro",
    "valor_pago",
    "saldo_apos",
    "status_apos",
]


def carregar_historico_pagamentos(armazenamento, arquivo):
    historico = armazenamento.read_csv(
        arquivo,
        columns=COLUNAS_HISTORICO_PAGAMENTOS,
    )
    faltantes = set(COLUNAS_HISTORICO_PAGAMENTOS) - set(historico.columns)
    if faltantes:
        raise ValueError(
            "Colunas ausentes no histórico de pagamentos: "
            + ", ".join(sorted(faltantes))
        )

    return historico[COLUNAS_HISTORICO_PAGAMENTOS]


def ordenar_historico_pagamentos(historico):
    historico_com_data = historico.assign(
        _data_ordenacao=pd.to_datetime(
            historico["data_pagamento"],
            format="%d/%m/%Y",
            errors="coerce",
        )
    )
    return (
        historico_com_data.sort_values(
            "_data_ordenacao",
            ascending=False,
            kind="stable",
        )
        .drop(columns="_data_ordenacao")
    )
>>>>>>> 21f50ad74dc42c233a42e2f39767d0a161e7ccec
