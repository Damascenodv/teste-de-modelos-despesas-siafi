from pathlib import Path
import numpy as np
import pandas as pd
from src.tcc_mec.ingest import centavos, selecionar_arquivos
from src.tcc_mec.backtest import atributos, calendario, dados_treinamento, escala_mase


def test_centavos_preservam_estorno():
    s = pd.Series(['123,45', '-17,30', '1.001,00', '0,00'])
    assert centavos(s).tolist() == [12345,-1730,100100,0]


def test_lags_nao_olham_futuro():
    idx = pd.date_range('2021-01-01',periods=30,freq='MS')
    dados = pd.Series(np.arange(1,31,dtype=float),index=idx)
    instante = pd.Timestamp('2023-01-01')
    historico = dados.loc[:'2022-12-01']
    vet = atributos(historico,instante)
    assert vet[0] == 24.0 and vet[1] == 13.0
    x,y = dados_treinamento(historico,instante)
    assert len(y) == 12 and max(y) == 24


def test_lags_ausentes_rejeitados():
    idx = pd.date_range('2021-01-01',periods=24,freq='MS')
    dados = pd.Series(np.arange(24,dtype=float),index=idx)
    dados.loc['2021-12-01'] = np.nan
    assert atributos(dados,pd.Timestamp('2022-12-01')) is None


def test_calendario_mantem_mes_ausente():
    dados = pd.DataFrame({'mes':['2021-01','2021-03'], 'pagos_centavos':[100,300]})
    s = calendario(dados)
    assert len(s) == 3 and pd.isna(s.iloc[1])


def test_escala_mase_sazonal():
    idx = pd.date_range('2021-01-01',periods=24,freq='MS')
    y = pd.Series([1.0]*12+[2.0]*12,index=idx)
    assert escala_mase(y) == 1.0
