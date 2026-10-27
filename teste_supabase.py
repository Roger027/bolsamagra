import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

st.title("🧪 Diagnóstico do arquivo .env")

# 1. FORÇAR A LOCALIZAÇÃO DO .ENV NA PASTA DO PROJETO
caminho_env = Path('.') / '.env'
st.write(f"Procurando arquivo `.env` em: `{caminho_env.resolve()}`")

if caminho_env.exists():
    st.success("✅ Arquivo `.env` encontrado fisicamente na pasta!")
    # Força o carregamento passando o caminho exato
    load_dotenv(dotenv_path=caminho_env)
else:
    st.error("❌ O arquivo `.env` NÃO foi encontrado nessa pasta!")
    st.info("Garanta que o arquivo se chama exatamente `.env` (sem `.txt` no final e com o ponto na frente).")
    st.stop()

# 2. CAPTURAR E MOSTRAR O RESULTADO
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

st.write("---")
st.write(f"**SUPABASE_URL:** {'✅ Carregada com sucesso' if url else '❌ Vazia / Não encontrada'}")
st.write(f"**SUPABASE_KEY:** {'✅ Carregada com sucesso' if key else '❌ Vazia / Não encontrada'}")

if not url or not key:
    st.warning("💡 Se o arquivo existe mas as variáveis estão vazias, abra o seu arquivo `.env` e verifique se o nome delas está exatamente igual a:")
    st.code("SUPABASE_URL=seu_link_aqui\nSUPABASE_KEY=sua_chave_aqui", language="text")
    st.stop()
else:
    st.success("🎉 Tudo pronto! Agora o Supabase vai conectar.")
    # Aqui você pode colocar o resto do seu código do Supabase...

