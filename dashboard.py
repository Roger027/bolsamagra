#1 configuração do Streamlit e demais ferramentas
from pathlib import Path
import os
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
from google import genai
from dotenv import load_dotenv
from modulos.finance_store import FinanceStore, FinanceStoreError

def converter_valor_csv(valor):
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return float(texto)


def carregar_historico_pagamentos(armazenamento, arquivo):
    colunas = [
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

    historico = armazenamento.read_csv(arquivo, columns=colunas)
    faltantes = set(colunas) - set(historico.columns)
    if faltantes:
        raise ValueError(
            "Colunas ausentes no histórico de pagamentos: "
            + ", ".join(sorted(faltantes))
        )

    return historico[colunas]


def exigir_acesso():
    if os.getenv("APP_ENV", "development").lower() != "production":
        return

    try:
        st.secrets["auth"]["google"]["client_id"]
        st.secrets["auth"]["google"]["client_secret"]
        emails_configurados = st.secrets["access"]["allowed_emails"]
    except KeyError:
        st.error(
            "Login Google ainda não foi configurado no servidor. "
            "Configure as credenciais OIDC e os e-mails autorizados."
        )
        st.stop()

    if not st.user.is_logged_in:
        st.title("🔐 Bolsa Magra — acesso privado")
        st.write("Entre com uma conta Google autorizada para continuar.")
        if st.button("Entrar com Google", type="primary"):
            st.login("google")
        st.stop()

    try:
        emails_autorizados = {
            str(email).strip().lower()
            for email in emails_configurados
            if str(email).strip()
        }
    except TypeError:
        st.error("A lista de usuários autorizados está inválida.")
        st.stop()

    email_usuario = str(st.user.get("email", "")).strip().lower()
    if not email_usuario or email_usuario not in emails_autorizados:
        st.error(
            "Esta conta não foi convidada para acessar os dados financeiros."
        )
        if st.button("Sair"):
            st.logout()
        st.stop()

    st.sidebar.caption(f"Acesso: {email_usuario}")
    if st.sidebar.button("Sair da conta"):
        st.logout()
        st.stop()


#2 configuração da pasta
PASTA = Path(__file__).resolve().parent
load_dotenv(PASTA / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
 

#3 configuração da IA e chave

if GEMINI_API_KEY:
    cliente_gemini = genai.Client(
        api_key=GEMINI_API_KEY
    )
else:
    cliente_gemini = None


#4 Configuração da página
st.set_page_config(
    page_title="Bolsa Magra",
    page_icon="💰",
    layout="wide"
)

exigir_acesso()

try:
    armazenamento = FinanceStore(PASTA)
except FinanceStoreError as erro:
    st.error(str(erro))
    st.stop()

if armazenamento.is_cloud and armazenamento.is_empty:
    st.error(
        "O banco Supabase ainda está vazio. Execute "
        "migrar_para_supabase.py no computador que contém os CSVs."
    )
    st.stop()

#5 Configuração do Calendário


st.sidebar.header("📅 Calendário")

data_selecionada = st.sidebar.date_input(
    "Selecione uma data",
    value=datetime.now().date(),
    format="DD/MM/YYYY"
)

st.sidebar.write(
    f"Data selecionada: **{data_selecionada.strftime('%d/%m/%Y')}**"
)


#Passo 6: Localizar os arquivos
arquivo = PASTA / "obrigacoes.csv"
arquivo_dividas = PASTA / "dividas_reais.csv"
arquivo_pagamentos = PASTA / "pagamentos.csv"

st.title("💰 Bolsa Magra")
st.subheader("Painel de controle financeiro")

#Passo 7: Carregar os dados
try:
    obrigacoes = armazenamento.read_csv(
        arquivo,
        columns=["origem", "nome", "valor", "vencimento", "status"],
    )
    historico_pagamentos = carregar_historico_pagamentos(
        armazenamento,
        arquivo_pagamentos,
    )
    dividas = armazenamento.read_csv(
        arquivo_dividas,
        columns=[
            "nome",
            "tipo",
            "saldo_devedor",
            "parcela",
            "juros_mensal",
            "parcelas_restantes",
            "status",
        ],
    )
    historico_receitas = armazenamento.read_csv(
        PASTA / "receitas_lancadas.csv",
        columns=["data", "pessoa", "valor", "tipo_entrada"],
    )
    historico_saidas = armazenamento.read_csv(
        PASTA / "saidas.csv",
        columns=["data", "pessoa", "valor", "categoria", "descricao"],
    )
except (
    FinanceStoreError,
    OSError,
    ValueError,
    pd.errors.ParserError,
) as erro:
    st.error(f"Não foi possível carregar os dados financeiros: {erro}")
    st.stop()

if obrigacoes.empty:
    st.error(
        "Não há obrigações carregadas. Confira o banco compartilhado "
        "e importe os CSVs antes de continuar."
    )
    st.stop()

# Gerenciamento de pagamentos
st.header("💳 Pagamentos de contas, faturas e dívidas")
aba_contas, aba_dividas = st.tabs(["Contas e faturas", "Dívidas"])

with aba_contas:
    contas_abertas = obrigacoes[
        obrigacoes["status"].astype(str).str.strip().str.lower()
        == "pendente"
    ].copy()
    contas_abertas = contas_abertas[
        pd.to_numeric(contas_abertas["valor"], errors="coerce") > 0
    ]

    if contas_abertas.empty:
        st.info("Não há contas ou faturas pendentes para registrar.")
    else:
        indices_contas = [int(indice) for indice in contas_abertas.index]
        rotulos_contas = {
            indice: (
                f"{obrigacoes.at[indice, 'origem']} — "
                f"{obrigacoes.at[indice, 'nome']} — "
                f"R$ {float(obrigacoes.at[indice, 'valor']):,.2f} — "
                f"venc. {obrigacoes.at[indice, 'vencimento']} "
                f"(registro {indice + 1})"
            )
            for indice in indices_contas
        }

        with st.form("form_pagamento_conta"):
            indice_conta = st.selectbox(
                "Conta ou fatura",
                options=indices_contas,
                format_func=lambda indice: rotulos_contas[indice],
            )
            data_pagamento_conta = st.date_input(
                "Data do pagamento",
                value=datetime.now().date(),
                format="DD/MM/YYYY",
            )
            confirmar_conta = st.form_submit_button(
                "Confirmar pagamento e marcar como pago"
            )

        if confirmar_conta:
            conta = obrigacoes.loc[indice_conta]
            valor_pago = float(conta["valor"])
            registro = pd.DataFrame([{
                "data_pagamento": data_pagamento_conta.strftime("%d/%m/%Y"),
                "tipo": "Conta/fatura",
                "origem": conta["origem"],
                "nome": conta["nome"],
                "vencimento": conta["vencimento"],
                "indice_registro": indice_conta,
                "valor_pago": valor_pago,
                "saldo_apos": 0.0,
                "status_apos": "Pago",
            }])

            try:
                nova_obrigacoes = obrigacoes.copy()
                nova_obrigacoes.at[indice_conta, "status"] = "Pago"
                novo_historico = pd.concat(
                    [historico_pagamentos, registro],
                    ignore_index=True,
                )
                armazenamento.save_many({
                    arquivo: nova_obrigacoes,
                    arquivo_pagamentos: novo_historico,
                })
            except (FinanceStoreError, OSError) as erro:
                st.error(f"Não foi possível salvar o pagamento: {erro}")
            else:
                st.success(
                    f"Pagamento de {rotulos_contas[indice_conta]} "
                    "registrado."
                )
                st.rerun()

with aba_dividas:
    erro_dividas = None
    try:
        for coluna in ("saldo_devedor", "parcela", "juros_mensal"):
            dividas[coluna] = dividas[coluna].map(converter_valor_csv)
        dividas["saldo_devedor"] = dividas["saldo_devedor"].round(2)
    except (KeyError, ValueError) as erro:
        erro_dividas = f"Dados inválidos em dividas_reais.csv: {erro}"

    if erro_dividas:
        st.error(erro_dividas)
    else:
        dividas_abertas = dividas[
            pd.to_numeric(dividas["saldo_devedor"], errors="coerce") > 0
        ].copy()

        if dividas_abertas.empty:
            st.info("Não há saldo devedor em aberto.")
        else:
            indices_dividas = [
                int(indice) for indice in dividas_abertas.index
            ]
            rotulos_dividas = {
                indice: (
                    f"{dividas.at[indice, 'nome']} — "
                    f"saldo R$ "
                    f"{float(dividas.at[indice, 'saldo_devedor']):,.2f} "
                    f"(registro {indice + 1})"
                )
                for indice in indices_dividas
            }

            with st.form("form_pagamento_divida"):
                indice_divida = st.selectbox(
                    "Dívida",
                    options=indices_dividas,
                    format_func=lambda indice: rotulos_dividas[indice],
                )
                saldo_divida = float(
                    dividas.at[indice_divida, "saldo_devedor"]
                )
                valor_pagamento_divida = st.number_input(
                    "Valor pago (R$)",
                    min_value=0.01,
                    max_value=saldo_divida,
                    value=saldo_divida,
                    step=10.0,
                    format="%.2f",
                )
                data_pagamento_divida = st.date_input(
                    "Data do pagamento",
                    value=datetime.now().date(),
                    format="DD/MM/YYYY",
                )
                confirmar_divida = st.form_submit_button(
                    "Confirmar pagamento e atualizar saldo"
                )

            if confirmar_divida:
                saldo_restante = round(
                    saldo_divida - valor_pagamento_divida,
                    2,
                )
                status_divida = (
                    "Quitada" if saldo_restante == 0 else "Em andamento"
                )
                divida = dividas.loc[indice_divida]
                registro = pd.DataFrame([{
                    "data_pagamento": (
                        data_pagamento_divida.strftime("%d/%m/%Y")
                    ),
                    "tipo": "Dívida",
                    "origem": "",
                    "nome": divida["nome"],
                    "vencimento": "",
                    "indice_registro": indice_divida,
                    "valor_pago": valor_pagamento_divida,
                    "saldo_apos": saldo_restante,
                    "status_apos": status_divida,
                }])

                novas_dividas = dividas.copy()
                novas_dividas.at[
                    indice_divida, "saldo_devedor"
                ] = saldo_restante
                novas_dividas.at[
                    indice_divida, "status"
                ] = status_divida
                novo_historico = pd.concat(
                    [historico_pagamentos, registro],
                    ignore_index=True,
                )

                try:
                    armazenamento.save_many({
                        arquivo_dividas: novas_dividas,
                        arquivo_pagamentos: novo_historico,
                    })
                except (FinanceStoreError, OSError) as erro:
                    st.error(
                        f"Não foi possível salvar o pagamento da dívida: "
                        f"{erro}"
                    )
                else:
                    st.success(
                        f"Pagamento de R$ {valor_pagamento_divida:,.2f} "
                        f"registrado. Saldo restante: "
                        f"R$ {saldo_restante:,.2f}."
                    )
                    st.rerun()

#Passo 8: Separar os dados
pendentes = obrigacoes[
    obrigacoes["status"] == "Pendente"
].copy()

planejadas = obrigacoes[
    obrigacoes["status"] == "Planejado"
].copy()

#Passo 9: Indicadores
total_pendente = pendentes["valor"].sum()
total_planejado = planejadas["valor"].sum()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Contas pendentes",
    f"R$ {total_pendente:,.2f}"
)

col2.metric(
    "Contas planejadas",
    f"R$ {total_planejado:,.2f}"
)

col3.metric(
    "Quantidade de pendências",
    len(pendentes)
)

#Passo 10: Gráfico por origem

st.subheader("Despesas por origem")


if not pendentes.empty:
    resumo = (
        pendentes.groupby("origem", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

    grafico = px.bar(
        resumo,
        x="origem",
        y="valor",
        text_auto=".2f",
        title="Obrigações pendentes por origem"
    )

    st.plotly_chart(grafico, width="stretch")
else:
    st.info("Não há obrigações pendentes.")

#Passo 11: Tabela
st.subheader("Detalhamento das obrigações")
st.dataframe(pendentes, width="stretch")

st.subheader("Histórico de pagamentos")
if historico_pagamentos.empty:
    st.info("Nenhum pagamento foi registrado ainda.")
else:
    historico_com_data = historico_pagamentos.assign(
        _data_ordenacao=pd.to_datetime(
            historico_pagamentos["data_pagamento"],
            format="%d/%m/%Y",
            errors="coerce",
        )
    )
    st.dataframe(
        historico_com_data.sort_values(
            "_data_ordenacao",
            ascending=False,
        ).drop(columns="_data_ordenacao"),
        width="stretch",
    )

#Passo 12: Preparar os vencimentos
obrigacoes["data_vencimento"] = pd.to_datetime(
    obrigacoes["vencimento"],
    format="%d/%m/%Y",
    errors="coerce"
)

#Passo 13: Criar opções de mês disponíveis
meses = (
    obrigacoes["data_vencimento"]
    .dropna()
    .dt.to_period("M")
    .drop_duplicates()
    .sort_values()
)

opcoes = ["Todos"] + [
    mes.strftime("%m/%Y") for mes in meses
]

mes_selecionado = st.selectbox(
    "Selecione o mês",
    opcoes
)

#Passo 14: Filtrar por mês
if mes_selecionado == "Todos":
    dados_mes = obrigacoes.copy()
else:
    mes_num, ano = mes_selecionado.split("/")
    dados_mes = obrigacoes[
        (obrigacoes["data_vencimento"].dt.month == int(mes_num)) &
        (obrigacoes["data_vencimento"].dt.year == int(ano))
    ].copy()

#Passo 15: Separar pendências e planejamentos
pendentes = dados_mes[
    dados_mes["status"] == "Pendente"
].copy()

planejadas = dados_mes[
    dados_mes["status"] == "Planejado"
].copy()

#Passo 16: Receitas e contribuições individuais
st.subheader("Receitas e contribuições")

pessoa = st.selectbox(
    "Selecione a pessoa",
    ["Rogério", "Tatiana", "Júlia"]
)

receita = st.number_input(
    "Receita mensal (R$)",
    min_value=0.0,
    value=0.0,
    step=100.0
)
tipo_entrada = st.selectbox(
    "Tipo de recebimento",
    [
        "5º dia útil",
        "Vale dia 20",
        "Entrada extra"
    ]
)


#Passo 17: Regras financeiras individuais?


#Passo 18: Reserva aplicável por tipo de entrada
if pessoa in ["Rogério", "Tatiana"] and tipo_entrada in [
    "5º dia útil", "Vale dia 20"
]:
    reserva_transporte_alvo = 207.50
    reserva_inss_alvo = 90.00
else:
    reserva_transporte_alvo = 0.00
    reserva_inss_alvo = 0.00

#Passo 19: Não reservar mais do que o valor recebido
reserva_alvo = reserva_transporte_alvo + reserva_inss_alvo
reserva_aplicada = min(receita, reserva_alvo)

#Passo 20: Distribuir proporcionalmente se o recebimento for insuficiente
if reserva_alvo > 0:
    transporte = reserva_aplicada * (
        reserva_transporte_alvo / reserva_alvo
    )
    inss = reserva_aplicada * (
        reserva_inss_alvo / reserva_alvo
    )
else:
    transporte = 0.0
    inss = 0.0

base_calculo = receita - reserva_aplicada

#Passo 21: Regras individuais
if pessoa == "Rogério":
    bolsa = base_calculo * 0.10
    dizimo = base_calculo * 0.10
    oferta = base_calculo * 0.06
    emergencia = base_calculo * 0.01

elif pessoa == "Tatiana":
    bolsa = 0.0
    dizimo = base_calculo * 0.10
    oferta = base_calculo * 0.05
    emergencia = 0.0

else:
    bolsa = 0.0
    dizimo = 0.0
    oferta = 0.0
    emergencia = 0.0

total_contribuicoes = bolsa + dizimo + oferta + emergencia

saldo_apos_contribuicoes = (
    base_calculo - total_contribuicoes
)

col1, col2, col3 = st.columns(3)

col1.metric("Receita", f"R$ {receita:,.2f}")
col2.metric(
    "Contribuições",
    f"R$ {total_contribuicoes:,.2f}"
)
col3.metric(
    "Saldo após contribuições",
    f"R$ {saldo_apos_contribuicoes:,.2f}"
)

st.write("### Detalhamento")

st.write(f"Bolsa Magra: R$ {bolsa:,.2f}")
st.write(f"Dízimo: R$ {dizimo:,.2f}")
st.write(f"Oferta: R$ {oferta:,.2f}")
st.write(f"Emergência: R$ {emergencia:,.2f}")


if pessoa in ["Rogério", "Tatiana"]:
    st.write(
        f"Reserva mensal de transporte: R$ {transporte:,.2f}"
    )
    st.write(f"Reserva mensal de INSS: R$ {inss:,.2f}")
    st.write(f"Base de cálculo: R$ {base_calculo:,.2f}")

   
#Passo 22: Arquivo permanente de receitas
arquivo_receitas = PASTA / "receitas_lancadas.csv"

if st.button("Registrar receita"):
    if receita <= 0:
        st.warning("Informe um valor maior que zero.")
    else:
        agora = datetime.now()

        historico_existente = historico_receitas.copy()

        # Passo 22b: Garantir que registros antigos tenham a coluna
        if "tipo_entrada" not in historico_existente.columns:
            historico_existente["tipo_entrada"] = ""

        # Passo 22c: Converter datas existentes
        if not historico_existente.empty:
            historico_existente["data"] = pd.to_datetime(
                historico_existente["data"],
                format="%d/%m/%Y %H:%M",
                errors="coerce"
            )

        # Passo 22d: Verificar duplicidade das duas entradas mensais
        entrada_mensal = tipo_entrada in [
            "5º dia útil",
            "Vale dia 20"
        ]

        if entrada_mensal and not historico_existente.empty:

            mesmo_mes = (
                historico_existente["data"].dt.to_period("M")
                == pd.Period(agora, freq="M")
            )

            mesmo_usuario = (
                historico_existente["pessoa"] == pessoa
            )

            mesmo_tipo = (
                historico_existente["tipo_entrada"]
                == tipo_entrada
            )

            duplicado = not historico_existente[
                mesmo_mes & mesmo_usuario & mesmo_tipo
            ].empty

            if duplicado:
                st.error(
                    f"{pessoa} já possui uma entrada "
                    f"'{tipo_entrada}' registrada neste mês."
                )
                st.stop()

        # Passo 22e: Criar novo lançamento
        novo_lancamento = pd.DataFrame([{
    "data": agora.strftime("%d/%m/%Y %H:%M"),
    "pessoa": pessoa,
    "valor": receita,
    "tipo_entrada": tipo_entrada,
    "transporte": transporte,
    "inss": inss,
    "base_calculo": base_calculo,
    "bolsa_magra": bolsa,
    "dizimo": dizimo,
    "oferta": oferta,
    "emergencia": emergencia,
    "saldo_apos_contribuicoes": saldo_apos_contribuicoes
}])

        try:
            armazenamento.save_many({
                arquivo_receitas: pd.concat(
                    [historico_existente, novo_lancamento],
                    ignore_index=True,
                )
            })
        except (FinanceStoreError, OSError) as erro:
            st.error(f"Não foi possível registrar a receita: {erro}")
        else:
            st.success(
                f"Receita de R$ {receita:,.2f} registrada para {pessoa}."
            )
            st.rerun()

# Passo 23: Histórico de receitas
if historico_receitas.empty:
    st.info("Nenhuma receita foi registrada ainda.")
else:
    historico = historico_receitas.copy()
    if "tipo_entrada" not in historico.columns:
        historico["tipo_entrada"] = ""

    historico["data"] = pd.to_datetime(
        historico["data"],
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )
    mes_atual = pd.Timestamp.now().to_period("M")
    receitas_mes = historico[
        historico["data"].dt.to_period("M") == mes_atual
    ].copy()

    st.subheader("Histórico de receitas do mês")
    if not receitas_mes.empty:
        resumo_receitas = receitas_mes.groupby(
            "pessoa",
            as_index=False,
        )["valor"].sum()
        st.dataframe(resumo_receitas, width="stretch")

        fig_receitas = px.bar(
            resumo_receitas,
            x="pessoa",
            y="valor",
            color="pessoa",
            text_auto=".2f",
            title="Receitas registradas por pessoa",
        )
        fig_receitas.update_layout(
            xaxis_title="Pessoa",
            yaxis_title="Receita (R$)",
            showlegend=False,
        )
        st.plotly_chart(fig_receitas, width="stretch")
        st.metric(
            "Total de receitas registradas no mês",
            f"R$ {receitas_mes['valor'].sum():,.2f}",
        )
    else:
        st.info("Nenhuma receita foi registrada neste mês.")

    with st.expander("Ver todos os lançamentos"):
        st.dataframe(
            historico.sort_values("data", ascending=False),
            width="stretch",
        )

   
# Passo 24: LANÇAMENTOS DA DATA SELECIONADA

if not historico_receitas.empty:

    historico_calendario = historico_receitas.copy()
    historico_calendario["data"] = pd.to_datetime(
        historico_calendario["data"],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    lancamentos_dia = historico_calendario[
        historico_calendario["data"].dt.date == data_selecionada
    ].copy()

    st.sidebar.subheader("💰 Recebimentos do dia")

    if not lancamentos_dia.empty:

        st.sidebar.write(
            f"**{len(lancamentos_dia)} lançamento(s)**"
        )

        total_dia = lancamentos_dia["valor"].sum()

        st.sidebar.metric(
            "Total recebido",
            f"R$ {total_dia:,.2f}"
        )

        for _, lancamento in lancamentos_dia.iterrows():

            st.sidebar.write(
                f"**{lancamento['pessoa']}** — "
                f"R$ {lancamento['valor']:,.2f}"
            )

            if "tipo_entrada" in lancamento:
                st.sidebar.caption(
                    lancamento["tipo_entrada"]
                )

    else:

        st.sidebar.info(
            "Nenhum recebimento registrado nesta data."
        )

      
# Passo 25: SISTEMA DE SAÍDAS


arquivo_saidas = PASTA / "saidas.csv"

st.header("💸 Sistema de saídas")

col1, col2, col3 = st.columns(3)

with col1:
    pessoa_saida = st.selectbox(
        "Responsável pela saída",
        ["Rogério", "Tatiana", "Júlia"],
        key="pessoa_saida"
    )

with col2:
    valor_saida = st.number_input(
        "Valor da saída (R$)",
        min_value=0.0,
        step=10.0,
        key="valor_saida"
    )

with col3:
    categoria_saida = st.selectbox(
        "Categoria",
        [
            "Alimentação",
            "Transporte",
            "Moradia",
            "Saúde",
            "Educação",
            "Trabalho",
            "Dívida",
            "Lazer",
            "Outros"
        ],
        key="categoria_saida"
    )

descricao_saida = st.text_input(
    "Descrição da saída",
    key="descricao_saida"
)

if st.button("Registrar saída", type="primary"):

    if valor_saida <= 0:
        st.warning("Informe um valor maior que zero.")

    else:

        nova_saida = pd.DataFrame([{
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "pessoa": pessoa_saida,
            "valor": valor_saida,
            "categoria": categoria_saida,
            "descricao": descricao_saida
        }])

        try:
            armazenamento.save_many({
                arquivo_saidas: pd.concat(
                    [historico_saidas, nova_saida],
                    ignore_index=True,
                )
            })
        except (FinanceStoreError, OSError) as erro:
            st.error(f"Não foi possível registrar a saída: {erro}")
        else:
            st.success(f"Saída de R$ {valor_saida:,.2f} registrada.")
            st.rerun()

# Passo 25a: HISTÓRICO DE SAÍDAS

if not historico_saidas.empty:

    historico_saidas["data"] = pd.to_datetime(
        historico_saidas["data"],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    st.subheader("📚 Histórico de saídas")

    st.dataframe(
        historico_saidas.sort_values(
            "data",
            ascending=False
        ),
        width="stretch"
    )

    total_saidas = historico_saidas["valor"].sum()

    st.metric(
        "Total de saídas registradas",
        f"R$ {total_saidas:,.2f}"
    )

    resumo_saidas = (
        historico_saidas
        .groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

    grafico_saidas = px.bar(
        resumo_saidas,
        x="categoria",
        y="valor",
        text_auto=".2f",
        title="Saídas por categoria"
    )

    st.plotly_chart(
        grafico_saidas,
        width="stretch"
    )

else:

    st.info(
        "Nenhuma saída foi registrada ainda."
    )
    
       
# Organização assistida dos pagamentos
st.header("🤖 Organização de pagamentos com IA")
st.caption(
    "Ao solicitar uma análise, somente obrigações pendentes, saldos de "
    "dívidas e histórico de pagamentos são enviados ao Google Gemini. "
    "A IA apenas sugere; não altera arquivos nem efetua pagamentos."
)

pedido_organizacao = st.text_area(
    "O que você quer organizar?",
    value=(
        "Organize uma ordem prática para priorizar minhas contas e dívidas, "
        "considerando vencimentos, valores e saldos. Aponte os dados que "
        "faltam e não invente informações."
    ),
    key="pedido_organizacao_pagamentos",
)

if st.button("Organizar pagamentos com IA"):
    if not pedido_organizacao.strip():
        st.warning("Descreva como você quer organizar os pagamentos.")
    elif cliente_gemini is None:
        st.error("GEMINI_API_KEY não configurada.")
    elif erro_dividas:
        st.error(
            "Corrija o arquivo de dívidas antes de pedir a organização "
            "por IA."
        )
    else:
        contas_ia = obrigacoes[
            obrigacoes["status"].astype(str).str.strip().str.lower()
            == "pendente"
        ][["origem", "nome", "valor", "vencimento", "status"]]

        dividas_ia = dividas[
            [
                "nome",
                "saldo_devedor",
                "parcela",
                "juros_mensal",
                "parcelas_restantes",
                "status",
            ]
        ]
        historico_ia = historico_pagamentos.drop(
            columns=["indice_registro"]
        )

        contexto_organizacao = f"""
Você é o assistente financeiro do projeto Bolsa Magra.
Responda em português brasileiro usando somente os dados abaixo.
Não invente valores, datas, juros ou informações que não estejam nos dados.
Não tome decisões nem altere arquivos. Apresente sugestões para confirmação
do usuário e sinalize claramente qualquer informação ausente.

CONTAS E FATURAS PENDENTES:
{contas_ia.to_string(index=False)}

DÍVIDAS E SALDOS:
{dividas_ia.to_string(index=False)}

HISTÓRICO DE PAGAMENTOS:
{historico_ia.to_string(index=False)}

SOLICITAÇÃO:
{pedido_organizacao}
"""

        try:
            resposta_organizacao = (
                cliente_gemini.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=contexto_organizacao,
                )
            )
        except Exception as erro:
            st.error(f"Erro ao consultar a IA: {erro}")
        else:
            st.subheader("Sugestão de organização")
            st.write(resposta_organizacao.text)

# Passo 26: IA FINANCEIRA   
   

st.header("🤖 Assistente Financeiro")

pergunta = st.text_area(
    "Pergunte sobre sua situação financeira",
    placeholder=(
        "Ex.: Onde estou gastando mais este mês?"
    )
)

if st.button("Perguntar à IA"):

    if not pergunta.strip():
        st.warning("Digite uma pergunta.")

    elif cliente_gemini is None:
        st.error(
            "GEMINI_API_KEY não configurada."
        )

    else:

        # Passo 26a: Dados das receitas
        dados_receitas = historico_receitas

        # Passo 26b: Dados das saídas
        dados_saidas = historico_saidas

        contexto = f"""

Você é o assistente financeiro do sistema Bolsa Magra.

Analise os dados fornecidos e responda em português brasileiro.

REGRAS:
- Não invente valores.
- Use somente os dados fornecidos.
- Seja objetivo.
- Identifique riscos financeiros.
- Sugira ações práticas.
- Não tome decisões automaticamente.
- Quando faltar informação, diga claramente.

RECEITAS:
{dados_receitas.to_string(index=False)}

SAÍDAS:
{dados_saidas.to_string(index=False)}

PERGUNTA DO USUÁRIO:
{pergunta}
"""

        try:

            resposta = cliente_gemini.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=contexto
            )

            st.subheader("💡 Análise")

            st.write(resposta.text)

        except Exception as erro:

            st.error(
                f"Erro ao consultar a IA: {erro}"
            )