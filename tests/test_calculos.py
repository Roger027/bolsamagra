import pandas as pd
from modulos.calculos import normalizar_valores_obrigacoes


def test_normalizar_valores_obrigacoes_accepts_brazilian_decimal_values():
    obrigacoes = pd.DataFrame([
        {
            "nome": "Conta decimal",
            "valor": "382,82",
            "status": "Pendente",
        },
        {
            "nome": "Conta com milhares",
            "valor": "1.234,56",
            "status": "Pendente",
        },
    ])

    normalizadas = normalizar_valores_obrigacoes(obrigacoes)
    contas_abertas = normalizadas[
        pd.to_numeric(normalizadas["valor"], errors="coerce") > 0
    ]

    assert normalizadas["valor"].tolist() == [382.82, 1234.56]
    assert contas_abertas["nome"].tolist() == [
        "Conta decimal",
        "Conta com milhares",
    ]
    assert obrigacoes["valor"].tolist() == ["382,82", "1.234,56"]
