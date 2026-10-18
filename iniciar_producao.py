import json
import os
import subprocess
import sys
from pathlib import Path


PASTA = Path(__file__).resolve().parent


def exigir_variaveis() -> dict[str, str]:
    nomes = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "STREAMLIT_COOKIE_SECRET",
        "AUTHORIZED_EMAILS",
    ]
    faltantes = [nome for nome in nomes if not os.getenv(nome, "").strip()]
    if faltantes:
        raise RuntimeError(
            "Configure estas variáveis privadas no Render: "
            + ", ".join(faltantes)
        )

    emails = [
        email.strip().lower()
        for email in os.environ["AUTHORIZED_EMAILS"].split(",")
        if email.strip()
    ]
    if not emails:
        raise RuntimeError(
            "AUTHORIZED_EMAILS precisa conter ao menos um e-mail autorizado."
        )

    return {
        "supabase_url": os.environ["SUPABASE_URL"].strip(),
        "supabase_key": os.environ["SUPABASE_SERVICE_ROLE_KEY"].strip(),
        "client_id": os.getenv("GOOGLE_OIDC_CLIENT_ID", "").strip(),
        "client_secret": os.getenv("GOOGLE_OIDC_CLIENT_SECRET", "").strip(),
        "cookie_secret": os.environ["STREAMLIT_COOKIE_SECRET"].strip(),
        "emails": emails,
    }

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
            "Configure GOOGLE_OIDC_CLIENT_ID e "
            "GOOGLE_OIDC_CLIENT_SECRET juntos."
        )

    if client_id and client_secret:
        redirect_uri = os.getenv(
            "OIDC_REDIRECT_URI",
            f"{external_url}/oauth2callback" if external_url else "",
        )
        if not redirect_uri:
            raise RuntimeError(
                "O Render não forneceu RENDER_EXTERNAL_URL; "
                "configure OIDC_REDIRECT_URI."
            )

        conteudo.extend([
            "[auth]",
            f"redirect_uri = {json.dumps(redirect_uri)}",
            f"cookie_secret = {json.dumps(configuracao['cookie_secret'])}",
            "",
            "[auth.google]",
            f"client_id = {json.dumps(configuracao['client_id'])}",
            f"client_secret = {json.dumps(configuracao['client_secret'])}",
            (
                'server_metadata_url = '
                '"https://accounts.google.com/.well-known/'
                'openid-configuration"'
            ),
            "",
        ])

    diretorio = PASTA / ".streamlit"
    diretorio.mkdir(exist_ok=True)
    arquivo_secrets = diretorio / "secrets.toml"
    arquivo_secrets.write_text("\n".join(conteudo), encoding="utf-8")


def main() -> int:
    if os.getenv("APP_ENV", "").lower() != "production":
        raise RuntimeError("APP_ENV precisa estar configurado como production.")

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
        raise SystemExit(main())
    except RuntimeError as erro:
        print(f"Erro de configuração: {erro}", file=sys.stderr)
        raise SystemExit(1) from erro
