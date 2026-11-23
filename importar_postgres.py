"""Grava as séries e métricas apuradas em um servidor PostgreSQL configurado pelo usuário."""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import pandas as pd
from src.tcc_mec.config import pasta_resultados, url_banco


def conexao():
    import psycopg
    return psycopg.connect(url_banco(), connect_timeout=10)


def importar(pasta: Path):
    a = pd.read_csv(pasta/'auditoria_arquivos.csv')
    p = pd.read_csv(pasta/'previsoes_backtest.csv')
    m = pd.read_csv(pasta/'metricas_tabela2.csv')
    sql = (Path(__file__).parent/'sql'/'schema.sql').read_text(encoding='utf-8')
    with conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            for row in a.itertuples(index=False):
                cur.execute('''
                    INSERT INTO tcc_mec.execucao_mensal
                    (mes, valor_pago, valor_restos_pagar_pagos, total_registros_mec,
                    registros_negativos, arquivo_fonte, sha256_zip)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (mes) DO UPDATE SET
                    valor_pago=EXCLUDED.valor_pago,
                    valor_restos_pagar_pagos=EXCLUDED.valor_restos_pagar_pagos,
                    total_registros_mec=EXCLUDED.total_registros_mec,
                    registros_negativos=EXCLUDED.registros_negativos,
                    arquivo_fonte=EXCLUDED.arquivo_fonte,
                    sha256_zip=EXCLUDED.sha256_zip
                ''',(row.mes+'-01',Decimal(int(row.pagos_centavos)) / 100,
                     Decimal(int(row.restos_pagos_centavos)) / 100,row.registros_mec,
                     row.valores_negativos_mec,row.arquivo,row.sha256))
            for row in p.itertuples(index=False):
                cur.execute('''
                    INSERT INTO tcc_mec.previsao_backtest
                    (mes,modelo,valor_real,valor_previsto,erro_absoluto,mase_erro,historico_observacoes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (mes,modelo) DO UPDATE SET
                    valor_real=EXCLUDED.valor_real, valor_previsto=EXCLUDED.valor_previsto,
                    erro_absoluto=EXCLUDED.erro_absoluto, mase_erro=EXCLUDED.mase_erro,
                    historico_observacoes=EXCLUDED.historico_observacoes
                ''',(row.mes+'-01',row.modelo,Decimal(str(row.real_reais)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                     Decimal(str(row.previsto_reais)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                     Decimal(str(row.erro_absoluto_reais)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                     round(row.erro_absoluto_escalonado,8),row.observacoes_historicas))
            for row in m.itertuples(index=False):
                cur.execute('''
                    INSERT INTO tcc_mec.metricas (modelo,n_meses,mae_reais,rmse_reais,mase)
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT (modelo) DO UPDATE SET
                    n_meses=EXCLUDED.n_meses,mae_reais=EXCLUDED.mae_reais,
                    rmse_reais=EXCLUDED.rmse_reais,mase=EXCLUDED.mase
                ''',(row.modelo,row.n_meses,round(row.MAE_reais,2),
                     round(row.RMSE_reais,2),round(row.MASE,8)))


if __name__ == '__main__':
    importar(pasta_resultados())
