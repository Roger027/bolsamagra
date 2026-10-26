import json
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

PASTA = Path(__file__).resolve().parent

def exigir_variaveis() -> dict[str, str]:
    nomes = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "STREAMLIT_COOKIE_SECRET",
        "AUTHORIZED_EMAILS",
    ]
    
    # 1. Primeiro verifica se alguma variável está faltando no ambiente
    faltantes = [nome for nome in nomes if not os.getenv(nome, "").strip()]
    if faltantes:
        raise RuntimeError(
            f"Configure estas variáveis privadas no Render: {', '.join(faltantes)}"
        )
    
    # 2. Acessa de forma segura pois a checagem acima garante que existe
    string_emails = os.environ.get("AUTHORIZED_EMAILS", "")
    emails = [
        email.strip().lower()
        for email in string_emails.split(",")
        if email.strip()
    ]
    
    if not emails:
        raise RuntimeError(
            "A variável AUTHORIZED_EMAILS existe, mas está vazia ou mal formatada."
        )
        
    return {
        "supabase_url": os.environ["SUPABASE_URL"].strip(),
        # CORREÇÃO AQUI: Coleta o nome correto da variável validada acima
        "supabase_key": os.environ["SUPABASE_SERVICE_ROLE_KEY"].strip(),
        "client_id": os.getenv("GOOGLE_OIDC_CLIENT_ID", "").strip(),
        "client_secret": os.getenv("GOOGLE_OIDC_CLIENT_SECRET", "").strip(),
        "cookie_secret": os.environ["STREAMLIT_COOKIE_SECRET"].strip(),
        "emails": emails,
    }

# CORRIGIDO: Modificado de 'escribir_secrets' para 'escrever_secrets'
def escrever_secrets(configuracao: dict[str, str | list[str]]) -> None:
    conteudo = [
        "[access]",
        f"allowed_emails = {json.dumps(configuracao['emails'])}",
        "",
    ]
    
    external_url = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    client_id = str(configuracao["client_id"])
    client_secret = str(configuracao["client_secret"])
    
    if bool(client_id) != bool(client_secret):
        raise RuntimeError(
            "Configure GOOGLE_OIDC_CLIENT_ID e GOOGLE_OIDC_CLIENT_SECRET juntos."
        )
        
    if client_id and client_secret:
        redirect_uri = os.getenv(
            "OIDC_REDIRECT_URI",
            f"{external_url}/oauth2callback" if external_url else "",
        )
        if not redirect_uri:
            raise RuntimeError(
                "O Render não forneceu RENDER_EXTERNAL_URL; configure OIDC_REDIRECT_URI."
            )
            
        conteudo.extend([
            "[auth]",
            f"redirect_uri = {json.dumps(redirect_uri)}",
            f"cookie_secret = {json.dumps(configuracao['cookie_secret'])}",
            "",
            "[auth.google]",
            f"client_id = {json.dumps(configuracao['client_id'])}",
            f"client_secret = {json.dumps(configuracao['client_secret'])}",
            'server_metadata_url = "https://google.com"',
            "",
        ])
        
    diretorio = PASTA / ".streamlit"
    diretorio.mkdir(exist_ok=True)
    arquivo_secrets = diretorio / "secrets.toml"
    arquivo_secrets.write_text("\n".join(conteudo), encoding="utf-8")

def main() -> int:
    load_dotenv() 
    
    if not os.getenv("APP_ENV"):
        os.environ["APP_ENV"] = "production"
        
    configuracao = exigir_variaveis()
    escrever_secrets(configuracao)
    
    porta = os.getenv("PORT", "8501")
    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PASTA / "dashboard.py"),
        "--server.address=0.0.0.0",
        f"--server.port={porta}",
        "--server.headless=true",
    ]
    return subprocess.call(comando, cwd=PASTA)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as erro:
        print(f"Erro de configuração: {erro}", file=sys.stderr)
        sys.exit(1)
