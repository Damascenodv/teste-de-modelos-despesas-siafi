import argparse
from pathlib import Path

from src.tcc_mec.config import pasta_despesas, pasta_resultados, ultimo_mes
from src.tcc_mec.ingest import executar


def main():
    parser = argparse.ArgumentParser(description="Extrai despesas pagas do MEC de ZIPs mensais")
    parser.add_argument("--entrada", type=Path, default=pasta_despesas())
    parser.add_argument("--saida", type=Path, default=pasta_resultados())
    parser.add_argument("--ultimo-mes", default=ultimo_mes())
    args = parser.parse_args()
    if not args.entrada.is_dir():
        parser.error(f"Pasta de despesas não encontrada: {args.entrada}")
    executar(args.entrada, args.saida, args.ultimo_mes)


if __name__ == "__main__":
    main()
