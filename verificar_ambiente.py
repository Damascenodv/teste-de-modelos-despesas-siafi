from pathlib import Path
from urllib.parse import urlsplit

from src.tcc_mec.config import pasta_despesas, pasta_resultados, url_banco


def main():
    entrada = pasta_despesas()
    arquivos = list(entrada.glob("*Despesas*.zip")) if entrada.exists() else []
    print(f"Pasta Despesas: {entrada}")
    print(f"Arquivos ZIP: {len(arquivos)}")
    print(f"Pasta de resultados: {pasta_resultados()}")
    if not arquivos:
        print("ATENÇÃO: não foram encontrados ZIPs na pasta Despesas.")
    try:
        destino = urlsplit(url_banco())
        print(f"PostgreSQL: {destino.hostname}:{destino.port or 5432}/{destino.path.lstrip('/')}")
        import psycopg
        with psycopg.connect(url_banco(), connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_user")
                print(f"Conexão OK: {cur.fetchone()}")
    except Exception as exc:
        print(f"Conexão não estabelecida: {type(exc).__name__}: {exc}")
        print("Verifique se o PostgreSQL está ligado, o banco errorbot existe e a senha está correta.")


if __name__ == "__main__":
    main()
