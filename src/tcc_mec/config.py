import os
from pathlib import Path

from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")


def caminho_local(nome: str, padrao: str) -> Path:
    valor = Path(os.getenv(nome, padrao)).expanduser()
    return valor if valor.is_absolute() else RAIZ / valor


def pasta_despesas() -> Path:
    return caminho_local("DESPESAS_DIR", "Despesas")


def pasta_resultados() -> Path:
    return caminho_local("RESULTADOS_DIR", "resultados")


def ultimo_mes() -> str:
    return os.getenv("ULTIMO_MES", "2026-10")


def url_banco() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env")
    if url.startswith("jdbc:"):
        raise ValueError("Remova o prefixo 'jdbc:' de DATABASE_URL; use postgresql://")
    if not url.startswith(("postgresql://", "postgres://")):
        raise ValueError("DATABASE_URL deve iniciar com postgresql://")
    return url
