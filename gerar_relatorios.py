from pathlib import Path
from src.tcc_mec.config import pasta_resultados
import json
import math
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sklearn
import statsmodels

P = pasta_resultados()
series = pd.read_csv(P/'serie_mensal_mec.csv')
pred = pd.read_csv(P/'previsoes_backtest.csv')
met = pd.read_csv(P/'metricas_tabela2.csv')
aud = pd.read_csv(P/'auditoria_arquivos.csv')
all_months = pd.date_range('2021-01-01','2026-10-01',freq='MS').strftime('%Y-%m').tolist()
meses = set(series['mes'])
faltantes = [x for x in all_months if x not in meses]

serie_eixo = pd.Series(series['valor_pago_reais'].to_numpy() / 1e9, index=pd.to_datetime(series['mes']+'-01'))
serie_eixo = serie_eixo.reindex(pd.date_range('2021-01-01','2026-10-01',freq='MS'))
fig,ax=plt.subplots(figsize=(9.4,3.15))
ax.plot(serie_eixo.index,serie_eixo.to_numpy(),marker='o',markersize=2.5,lw=1.3)
ax.set_ylabel('Despesas pagas (R$ bilhões)')
ax.set_xlabel('Mês do lançamento')
ax.grid(alpha=.18)
fig.tight_layout()
fig.savefig(P/'figura_serie_historica.png',dpi=170,bbox_inches='tight')
plt.close(fig)

piv = pred.pivot(index='mes',columns='modelo',values='previsto_reais').sort_index()
real = pred.loc[pred.modelo.eq('Ingênuo')].set_index('mes').sort_index()['real_reais']
x = pd.to_datetime(real.index+'-01')
fig,ax=plt.subplots(figsize=(9.4,3.2))
ax.plot(x,real.values/1e9,'o-',label='Observado',markersize=4,lw=1.8)
ax.plot(x,piv['Random Forest'].values/1e9,'s--',label='Random Forest',markersize=3.2,lw=1.2)
ax.plot(x,piv['Ingênuo sazonal'].values/1e9,'^:',label='Ingênuo sazonal',markersize=3,lw=1.15)
ax.set_ylabel('Pagamentos (R$ bilhões)')
ax.set_xlabel('Competências efetivamente avaliadas (lacunas omitidas no eixo temporal)')
ax.grid(alpha=.17)
ax.legend(ncol=3,fontsize=8,loc='upper left')
fig.tight_layout()
fig.savefig(P/'figura_previsoes_19_origens.png',dpi=170,bbox_inches='tight')
plt.close(fig)

por_ano=pred.copy()
por_ano['ano'] = por_ano.mes.str.slice(0,4)
por_ano.groupby(['ano','modelo']).agg(n=('erro_reais','size'),mae_reais=('erro_absoluto_reais','mean')).to_csv(P/'metricas_por_ano.csv')

comparativo=pred.pivot(index='mes',columns='modelo',values='erro_absoluto_reais')
ganha=(comparativo['Random Forest'] < comparativo['Ingênuo sazonal']).sum()
reducao=100*(1 - met.loc[met.modelo.eq('Random Forest'),'MAE_reais'].iat[0]/met.loc[met.modelo.eq('Ingênuo sazonal'),'MAE_reais'].iat[0])
relatorio = {
 'orgao':'Ministério da Educação', 'codigo_orgao_superior':'26000',
 'meses_recebidos_ate_2026_10':len(series),
 'meses_ausentes_2021_2025':[m for m in faltantes if m[:4] <= '2025'],
 'meses_ausentes_total':faltantes,
 'inicio_serie':series.mes.min(),'fim_serie':series.mes.max(),
 'n_registros_mec':int(aud.registros_mec.sum()),
 'n_registros_todos_orgaos':int(aud.registros_totais.sum()),
 'n_estornos_negativos_mec':int(aud.valores_negativos_mec.sum()),
 'avaliacoes_comparaveis':int(pred.mes.nunique()),
 'meses_avaliados':sorted(pred.mes.unique().tolist()),
 'reducao_mae_random_forest_vs_ingenuo_sazonal_pct':float(reducao),
 'meses_rf_melhor_que_sazonal':int(ganha),
 'versoes':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'scikit-learn':sklearn.__version__,'statsmodels':statsmodels.__version__},
 'protocolo':{
   'periodo_teste':'2024-01 a 2026-10, origens elegíveis (não consecutivas)',
   'horizonte':'1 mês',
   'modelos':['Ingênuo','Ingênuo sazonal','SARIMA(1,0,0)(1,1,0)[12]','RandomForestRegressor(n_estimators=200,min_samples_leaf=2,random_state=42)'],
   'aleatoriedade':'semente=42',
   'variaveis_rf':['valor pago t-1','valor pago t-12','seno mês','cosseno mês','índice temporal'],
   'faltantes':'NaN preservados em SARIMA; lags ausentes excluem origem de avaliação; RF treina apenas com exemplos completos',
   'mase':'erro absoluto dividido pela média sazonal |y_t-y_{t-12}| da amostra disponível até a origem de cada previsão; média das razões',
   'status_postgres':'não executado; falta servidor/credenciais'
 }
}
(P/'resumo_auditoria.json').write_text(json.dumps(relatorio,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(relatorio,ensure_ascii=False,indent=2)[:6000])
