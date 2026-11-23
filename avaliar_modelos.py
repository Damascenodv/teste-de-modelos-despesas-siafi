import json
import pandas as pd
from src.tcc_mec.backtest import Configuracao, calendario, executar_backtest
from src.tcc_mec.config import pasta_resultados


if __name__ == '__main__':
    pasta = pasta_resultados()
    serie = pd.read_csv(pasta/'serie_mensal_mec.csv', dtype={'mes':'string', 'pagos_centavos':'int64'})
    cfg = Configuracao()
    pred, met, pul = executar_backtest(calendario(serie), cfg)
    pred.to_csv(pasta/'previsoes_backtest.csv',index=False,encoding='utf-8-sig',float_format='%.6f')
    met.to_csv(pasta/'metricas_tabela2.csv',index=False,encoding='utf-8-sig',float_format='%.6f')
    pul.to_csv(pasta/'meses_excluidos_avaliacao.csv',index=False,encoding='utf-8-sig')
    print('\nMETRICAS\n',met.to_string(index=False), '\n',len(pred)//4, 'origens válidas')
    print('\nPULADOS\n',pul.to_string(index=False))
