from types import SimpleNamespace
import pandas as pd
import pytest
import modulos.finance_store as finance_store
from modulos.finance_store import FinanceStore, FinanceStoreError


def test_local_store_saves_and_reloads_multiple_csvs(tmp_path, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    store = FinanceStore(tmp_path)

    obligations_path = tmp_path / "obrigacoes.csv"
    debts_path = tmp_path / "dividas_reais.csv"
    store.save_many({
        obligations_path: pd.DataFrame([{
            "nome": "Aluguel",
            "valor": 1000.0,
            "status": "Pendente",
        }]),
        debts_path: pd.DataFrame([{
            "nome": "Cartão",
            "saldo_devedor": 250.0,
        }]),
    })

    reloaded = FinanceStore(tmp_path)
    assert reloaded.read_csv(obligations_path).to_dict("records") == [
        {"nome": "Aluguel", "valor": 1000.0, "status": "Pendente"}
    ]
    assert reloaded.read_csv(debts_path).to_dict("records") == [
        {"nome": "Cartão", "saldo_devedor": 250.0}
    ]


def test_local_store_normalizes_prefixed_csv_column_names(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    obligations_path = tmp_path / "obrigacoes.csv"
    obligations_path.write_text(
        "+origem,nome,valor\nConta,Aluguel,1000\n",
        encoding="utf-8",
    )

    data = FinanceStore(tmp_path).read_csv(obligations_path)

    assert data.columns.tolist() == ["origem", "nome", "valor"]
    assert data.loc[0, "origem"] == "Conta"


def test_to_records_converts_missing_values_to_json_null():
    records = FinanceStore._to_records(
        pd.DataFrame([{"nome": "Conta", "valor": float("nan")}])
    )

    assert records == [{"nome": "Conta", "valor": None}]


def test_store_loads_production_environment_from_project_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    (tmp_path / ".env").write_text(
        "SUPABASE_URL=https://example.supabase.co\n"
        "SUPABASE_SERVICE_ROLE_KEY=test-key\n"
        "APP_ENV=production\n",
        encoding="utf-8",
    )
    created_clients = []
    monkeypatch.setattr(
        finance_store,
        "create_client",
        lambda url, key: created_clients.append((url, key)) or object(),
    )
    monkeypatch.setattr(FinanceStore, "_load_cloud_state", lambda _self: None)

    store = FinanceStore(tmp_path)

    assert store.is_cloud
    assert created_clients == [
        ("https://example.supabase.co", "test-key"),
    ]


def test_development_store_stays_local_with_cloud_credentials(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "private")
    monkeypatch.setattr(
        finance_store,
        "create_client",
        lambda *_args: pytest.fail(
            "development mode must not connect to the shared database"
        ),
    )

    store = FinanceStore(tmp_path)

    assert not store.is_cloud


def test_cloud_store_commits_multiple_files_and_rejects_stale_writes(
    tmp_path,
    monkeypatch,
):
    class FakeQuery:
        def __init__(self, client):
            self.client = client

        def select(self, _columns):
            return self

        def eq(self, _column, _value):
            return self

        def maybe_single(self):
            return self

        def execute(self):
            return SimpleNamespace(data=self.client.database)

    class FakeRpc:
        def __init__(self, client, params):
            self.client = client
            self.params = params

        def execute(self):
            if (
                self.params["p_expected_version"]
                != self.client.database["version"]
            ):
                raise RuntimeError("40001 Finance data changed")

            self.client.database["payload"] = self.params["p_payload"]
            self.client.database["version"] += 1
            return SimpleNamespace(
                data=self.client.database["version"]
            )

    class FakeClient:
        def __init__(self):
            self.database = {
                "id": "shared",
                "payload": {},
                "version": 0,
            }

        def table(self, _name):
            return FakeQuery(self)

        def rpc(self, _name, params):
            return FakeRpc(self, params)

    client = FakeClient()
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "private")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setattr(
        finance_store,
        "create_client",
        lambda _url, _key: client,
    )
    current = FinanceStore(tmp_path)
    stale = FinanceStore(tmp_path)

    current.save_many({
        tmp_path / "obrigacoes.csv": pd.DataFrame([
            {"nome": "Aluguel", "status": "Pago"}
        ]),
        tmp_path / "pagamentos.csv": pd.DataFrame([
            {"nome": "Aluguel", "valor_pago": 1000.0}
        ]),
    })

    assert client.database["version"] == 1
    assert set(client.database["payload"]) == {
        "obrigacoes.csv",
        "pagamentos.csv",
    }
    with pytest.raises(FinanceStoreError, match="outra sessão"):
        stale.save_many({
            tmp_path / "obrigacoes.csv": pd.DataFrame([
                {"nome": "Aluguel", "status": "Pendente"}
            ])
        })
