from pathlib import Path
import pytest

from src.tcc_mec.config import RAIZ, caminho_local, pasta_despesas, url_banco


def test_pasta_relativa_na_raiz(monkeypatch):
    monkeypatch.setenv("DESPESAS_DIR", "Despesas")
    assert pasta_despesas() == RAIZ / "Despesas"


def test_pasta_absoluta(monkeypatch, tmp_path):
    monkeypatch.setenv("DESPESAS_DIR", str(tmp_path))
    assert pasta_despesas() == tmp_path


def test_url_jdbc_rejeitada(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "jdbc:postgresql://localhost:5432/errorbot")
    with pytest.raises(ValueError, match="jdbc:"):
        url_banco()


def test_url_postgresql_aceita(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:abc@localhost:5432/errorbot")
    assert url_banco().endswith("/errorbot")
