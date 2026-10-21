import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client


class FinanceStoreError(RuntimeError):
    pass


class FinanceStore:
    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir).resolve()
        load_dotenv(self.project_dir / ".env")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.production = os.getenv("APP_ENV", "development").lower() == (
            "production"
        )

        if self.production and not (self.supabase_url and self.supabase_key):
            raise FinanceStoreError(
                "Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY "
                "no ambiente de produção."
            )

        self.client: Client | None = None
        self.payload: dict[str, list[dict]] = {}
        self.version = 0

        if self.supabase_url and self.supabase_key:
            self._connect()
            self._load_cloud_state()
        elif self.production:
            raise FinanceStoreError(
                "O armazenamento em nuvem não está configurado."
            )

    @property
    def is_cloud(self) -> bool:
        return self.client is not None

    @property
    def is_empty(self) -> bool:
        return not any(self.payload.values())

    def _connect(self) -> None:
        try:
            self.client = create_client(
                self.supabase_url,
                self.supabase_key,
            )
        except Exception as erro:
            raise FinanceStoreError(
                "Não foi possível configurar a conexão com o Supabase."
            ) from erro

    def _load_cloud_state(self) -> None:
        if self.client is None:
            raise FinanceStoreError("A conexão com o Supabase não foi iniciada.")

        try:
            resposta = (
                self.client.table("finance_state")
                .select("payload, version")
                .eq("id", "shared")
                .maybe_single()
                .execute()
            )
        except Exception as erro:
            raise FinanceStoreError(
                "Não foi possível carregar os dados financeiros do Supabase. "
                "Verifique se aplicou migrations\\finance_state.sql."
            ) from erro

        if resposta.data:
            self.payload = resposta.data["payload"]
            self.version = int(resposta.data["version"])

    def read_csv(
        self,
        arquivo: Path,
        columns: list[str] | None = None,
    ) -> pd.DataFrame:
        if self.is_cloud:
            registros = self.payload.get(arquivo.name, [])
            if registros:
                dados = pd.DataFrame(registros)
                return self._normalize_columns(dados)
            return pd.DataFrame(columns=columns or [])

        if not arquivo.exists():
            return pd.DataFrame(columns=columns or [])

        dados = pd.read_csv(arquivo, encoding="utf-8-sig")
        return self._normalize_columns(dados)

    @staticmethod
    def _normalize_columns(dados: pd.DataFrame) -> pd.DataFrame:
        colunas_normalizadas = [
            str(coluna).lstrip("\ufeff").strip().removeprefix("+")
            for coluna in dados.columns
        ]
        if len(colunas_normalizadas) != len(set(colunas_normalizadas)):
            raise FinanceStoreError(
                "O arquivo contém nomes de colunas duplicados após "
                "normalizar os cabeçalhos."
            )

        dados.columns = colunas_normalizadas
        return dados

    @staticmethod
    def _to_records(dados: pd.DataFrame) -> list[dict]:
        return json.loads(
            dados.to_json(
                orient="records",
                date_format="iso",
                force_ascii=False,
            )
        )

    def save_many(self, atualizacoes: dict[Path, pd.DataFrame]) -> None:
        novo_payload = dict(self.payload)
        for arquivo, dados in atualizacoes.items():
            novo_payload[arquivo.name] = self._to_records(dados)

        if self.is_cloud:
            self._save_cloud_state(novo_payload)
            return

        self._save_local_files(atualizacoes)

    def _save_cloud_state(self, novo_payload: dict[str, list[dict]]) -> None:
        if self.client is None:
            raise FinanceStoreError("A conexão com o Supabase não foi iniciada.")

        try:
            resposta = self.client.rpc(
                "save_finance_state",
                {
                    "p_expected_version": self.version,
                    "p_payload": novo_payload,
                },
            ).execute()
        except Exception as erro:
            mensagem = str(erro).lower()
            if "40001" in mensagem or "finance data changed" in mensagem:
                raise FinanceStoreError(
                    "Os dados foram alterados em outra sessão. "
                    "Atualize a página antes de tentar novamente."
                ) from erro

            raise FinanceStoreError(
                "Não foi possível salvar os dados no Supabase."
            ) from erro

        try:
            self.version = int(resposta.data)
        except (TypeError, ValueError) as erro:
            raise FinanceStoreError(
                "O Supabase não confirmou a versão dos dados salvos."
            ) from erro

        self.payload = novo_payload

    def _save_local_files(
        self,
        atualizacoes: dict[Path, pd.DataFrame],
    ) -> None:
        temporarios: dict[Path, Path] = {}
        originais: dict[Path, bytes | None] = {}
        substituidos: list[Path] = []

        try:
            for arquivo, dados in atualizacoes.items():
                arquivo.parent.mkdir(parents=True, exist_ok=True)
                originais[arquivo] = (
                    arquivo.read_bytes() if arquivo.exists() else None
                )
                temporario = arquivo.with_suffix(
                    arquivo.suffix + ".tmp"
                )
                dados.to_csv(
                    temporario,
                    index=False,
                    encoding="utf-8-sig",
                )
                temporarios[arquivo] = temporario

            for arquivo, temporario in temporarios.items():
                temporario.replace(arquivo)
                substituidos.append(arquivo)
        except OSError:
            for arquivo in reversed(substituidos):
                conteudo_original = originais[arquivo]
                if conteudo_original is None:
                    arquivo.unlink(missing_ok=True)
                else:
                    arquivo.write_bytes(conteudo_original)
            raise
        finally:
            for temporario in temporarios.values():
                temporario.unlink(missing_ok=True)
