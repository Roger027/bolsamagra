<<<<<<< HEAD

def calcular_quinzena(receitas, nome):
    # Somar todas as entradas da quinzena
    receita_total = sum(receitas)

    # Metas quinzenais
    transporte = 207.50
    inss = 90.00

    # Reservas efetivamente possíveis nesta quinzena
    transporte_reservado = min(receita_total, transporte)
    restante = receita_total - transporte_reservado

    inss_reservado = min(restante, inss)
    base = restante - inss_reservado

    # Percentuais sobre a base
    bolsa_magra = base * 0.10
    dizimo = base * 0.10
    oferta = base * 0.06
    emergencia = base * 0.01

    livre = base - bolsa_magra - dizimo - oferta - emergencia

    return {
        "quinzena": nome,
        "receita": receita_total,
        "transporte": transporte_reservado,
        "inss": inss_reservado,
        "falta_transporte": transporte - transporte_reservado,
        "falta_inss": inss - inss_reservado,
        "base": base,
        "bolsa_magra": bolsa_magra,
        "dizimo": dizimo,
        "oferta": oferta,
        "emergencia": emergencia,
        "livre": livre,
    }


def exibir_resultado(resultado):
    print(f"\n=== {resultado['quinzena']} ===")

    for chave, valor in resultado.items():
        if chave == "quinzena":
            continue
        print(f"{chave.replace('_', ' ').title()}: R$ {valor:.2f}")


if __name__ == "__main__":
    primeira = calcular_quinzena([5840], "1ª QUINZENA")
    segunda = calcular_quinzena([3000], "2ª QUINZENA")

    for resultado in [primeira, segunda]:
        exibir_resultado(resultado)

    print("\n=== RESUMO MENSAL ===")
    for campo in [
        "receita", "transporte", "inss", "base",
        "bolsa_magra", "dizimo", "oferta",
        "emergencia", "livre"
    ]:
        total = primeira[campo] + segunda[campo]
=======

def calcular_quinzena(receitas, nome):
    # Somar todas as entradas da quinzena
    receita_total = sum(receitas)

    # Metas quinzenais
    transporte = 207.50
    inss = 90.00

    # Reservas efetivamente possíveis nesta quinzena
    transporte_reservado = min(receita_total, transporte)
    restante = receita_total - transporte_reservado

    inss_reservado = min(restante, inss)
    base = restante - inss_reservado

    # Percentuais sobre a base
    bolsa_magra = base * 0.10
    dizimo = base * 0.10
    oferta = base * 0.06
    emergencia = base * 0.01

    livre = base - bolsa_magra - dizimo - oferta - emergencia

    return {
        "quinzena": nome,
        "receita": receita_total,
        "transporte": transporte_reservado,
        "inss": inss_reservado,
        "falta_transporte": transporte - transporte_reservado,
        "falta_inss": inss - inss_reservado,
        "base": base,
        "bolsa_magra": bolsa_magra,
        "dizimo": dizimo,
        "oferta": oferta,
        "emergencia": emergencia,
        "livre": livre,
    }


def exibir_resultado(resultado):
    print(f"\n=== {resultado['quinzena']} ===")

    for chave, valor in resultado.items():
        if chave == "quinzena":
            continue
        print(f"{chave.replace('_', ' ').title()}: R$ {valor:.2f}")


if __name__ == "__main__":
    primeira = calcular_quinzena([5840], "1ª QUINZENA")
    segunda = calcular_quinzena([3000], "2ª QUINZENA")

    for resultado in [primeira, segunda]:
        exibir_resultado(resultado)

    print("\n=== RESUMO MENSAL ===")
    for campo in [
        "receita", "transporte", "inss", "base",
        "bolsa_magra", "dizimo", "oferta",
        "emergencia", "livre"
    ]:
        total = primeira[campo] + segunda[campo]
>>>>>>> 21f50ad74dc42c233a42e2f39767d0a161e7ccec
        print(f"{campo.title()}: R$ {total:.2f}")