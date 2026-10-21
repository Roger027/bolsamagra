import os

import pytest
import tomllib

import iniciar_producao
from iniciar_producao import exigir_variaveis


def test_exigir_variaveis_normalizes_invited_emails(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "private")
    monkeypatch.setenv("STREAMLIT_COOKIE_SECRET", "random-cookie-secret")
    monkeypatch.setenv(
        "AUTHORIZED_EMAILS",
        " owner@example.com, guest@example.com ",
    )
    monkeypatch.delenv("GOOGLE_OIDC_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_OIDC_CLIENT_SECRET", raising=False)

    config = exigir_variaveis()

    assert config["emails"] == [
        "owner@example.com",
        "guest@example.com",
    ]
    assert config["client_id"] == ""
    assert config["client_secret"] == ""


def test_exigir_variaveis_rejects_missing_database_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("STREAMLIT_COOKIE_SECRET", "random-cookie-secret")
    monkeypatch.setenv("AUTHORIZED_EMAILS", "owner@example.com")

    with pytest.raises(RuntimeError, match="SUPABASE_SERVICE_ROLE_KEY"):
        exigir_variaveis()


def test_escrever_secrets_builds_google_callback_config(tmp_path, monkeypatch):
    monkeypatch.setattr(iniciar_producao, "PASTA", tmp_path)
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://bolsa.onrender.com")

    iniciar_producao.escrever_secrets({
        "supabase_url": "https://example.supabase.co",
        "supabase_key": "private",
        "client_id": "google-client-id",
        "client_secret": "google-client-secret",
        "cookie_secret": "random-cookie-secret",
        "emails": ["owner@example.com"],
    })

    secrets = tomllib.loads(
        (tmp_path / ".streamlit" / "secrets.toml").read_text(
            encoding="utf-8"
        )
    )
    assert secrets["auth"]["redirect_uri"] == (
        "https://bolsa.onrender.com/oauth2callback"
    )
    assert secrets["auth"]["google"]["client_secret"] == (
        "google-client-secret"
    )
    assert secrets["access"]["allowed_emails"] == ["owner@example.com"]


def test_main_defaults_to_production_and_starts_streamlit(tmp_path, monkeypatch):
    monkeypatch.setattr(iniciar_producao, "PASTA", tmp_path)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    (tmp_path / ".env").write_text("PORT=8765\n", encoding="utf-8")
    monkeypatch.setattr(iniciar_producao, "exigir_variaveis", lambda: {})
    monkeypatch.setattr(
        iniciar_producao,
        "escrever_secrets",
        lambda _config: None,
    )
    comandos = []
    monkeypatch.setattr(
        iniciar_producao.subprocess,
        "call",
        lambda comando, cwd: comandos.append((comando, cwd)) or 0,
    )

    assert iniciar_producao.main() == 0
    assert os.environ["APP_ENV"] == "production"
    assert comandos[0][1] == tmp_path
    assert "--server.port=8765" in comandos[0][0]
