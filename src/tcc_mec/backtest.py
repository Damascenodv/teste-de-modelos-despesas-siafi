"""Backtest cronológico de um mês à frente sem vazamento temporal."""
from __future__ import annotations

from dataclasses import dataclass
import math
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX

ESCALA = 1_000_000_000.0
MODELOS = ("Ingênuo", "Ingênuo sazonal", "SARIMA", "Random Forest")


@dataclass(frozen=True)
class Configuracao:
    inicio_teste: str = "2024-01"
    fim_teste: str = "2026-10"
    min_observacoes: int = 30
    semente: int = 42
    arvores: int = 200


def calendario(serie: pd.DataFrame) -> pd.Series:
    dados = serie.copy()
    dados["mes"] = pd.to_datetime(dados["mes"] + "-01", errors="raise")
    if dados["mes"].duplicated().any():
        raise ValueError("Datas mensais duplicadas")
    if (dados["pagos_centavos"].isna()).any():
        raise ValueError("Há valores mensais nulos em registros presentes")
    datas = pd.date_range(dados["mes"].min(), dados["mes"].max(), freq="MS")
    s = pd.Series(dados["pagos_centavos"].to_numpy(dtype="float64") / 100 / ESCALA,
                  index=pd.DatetimeIndex(dados["mes"])).reindex(datas)
    return s


def atributos(historico: pd.Series, instante: pd.Timestamp):
    anterior = instante - pd.DateOffset(months=1)
    anual = instante - pd.DateOffset(months=12)
    lag1 = historico.get(anterior, np.nan)
    lag12 = historico.get(anual, np.nan)
    if not (np.isfinite(lag1) and np.isfinite(lag12)):
        return None
    mes = instante.month
    return [lag1, lag12, math.sin(2 * math.pi * mes / 12),
            math.cos(2 * math.pi * mes / 12),
            (instante.year - 2021) * 12 + mes]


def dados_treinamento(historico: pd.Series, instante: pd.Timestamp):
    x, y = [], []
    for data, valor in historico.items():
        if data >= instante:
            break
        if pd.isna(valor):
            continue
        feats = atributos(historico, data)
        if feats is not None:
            x.append(feats)
            y.append(float(valor))
    return np.asarray(x, dtype="float64"), np.asarray(y, dtype="float64")


def escala_mase(historico: pd.Series) -> float:
    diferencas = (historico - historico.shift(12)).abs().dropna()
    if diferencas.empty or not np.isfinite(diferencas.mean()) or diferencas.mean() <= 0:
        raise ValueError("MASE sazonal indefinido para o histórico disponível")
    return float(diferencas.mean())


def prever_random_forest(historico: pd.Series, instante: pd.Timestamp, cfg: Configuracao) -> tuple[float, int]:
    x, y = dados_treinamento(historico, instante)
    if len(y) < 10:
        raise ValueError("Random Forest precisa de pelo menos 10 exemplos históricos completos")
    f = atributos(historico, instante)
    if f is None:
        raise ValueError("Faltam lags do mês-alvo para Random Forest")
    modelo = RandomForestRegressor(
        n_estimators=cfg.arvores, max_features=1.0, min_samples_leaf=2,
        random_state=cfg.semente, n_jobs=1,
    )
    modelo.fit(x, y)
    return float(modelo.predict([f])[0]), len(y)


def prever_sarima(historico: pd.Series) -> tuple[float, bool]:
    with warnings.catch_warnings(record=True) as alertas:
        warnings.simplefilter("always")
        mod = SARIMAX(
            historico, order=(1, 0, 0), seasonal_order=(1, 1, 0, 12),
            trend="n", enforce_stationarity=False,
            enforce_invertibility=False,
        )
        ajuste = mod.fit(disp=False, maxiter=100)
        previsto = float(ajuste.get_forecast(steps=1).predicted_mean.iloc[-1])
        convergiu = bool(ajuste.mle_retvals.get("converged", True))
    if not np.isfinite(previsto):
        raise ValueError("Previsão SARIMA não finita")
    return previsto, convergiu


def executar_backtest(serie: pd.Series, cfg: Configuracao) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    previsoes = []
    pulados = []
    inicio = pd.Timestamp(cfg.inicio_teste + "-01")
    fim = pd.Timestamp(cfg.fim_teste + "-01")
    for instante in serie.index:
        if instante < inicio or instante > fim:
            continue
        valor = serie.loc[instante]
        hist = serie.loc[: instante - pd.DateOffset(months=1)]
        motivo = None
        if not np.isfinite(valor):
            motivo = "Arquivo mensal não enviado"
        elif len(hist.dropna()) < cfg.min_observacoes:
            motivo = "Histórico insuficiente"
        elif atributos(hist, instante) is None:
            motivo = "Lag 1 ou lag 12 ausente"
        if motivo:
            pulados.append({"mes": instante.strftime("%Y-%m"), "motivo": motivo})
            continue
        denominador = escala_mase(hist)
        preds = {
            "Ingênuo": (float(hist.iloc[-1]), True),
            "Ingênuo sazonal": (float(hist.loc[instante - pd.DateOffset(months=12)]), True),
        }
        falhas = []
        try:
            sarima, ok = prever_sarima(hist)
            if not ok:
                falhas.append("SARIMA não convergiu")
            preds["SARIMA"] = (sarima, ok)
        except Exception as erro:
            falhas.append(f"SARIMA: {erro}")
        try:
            rf, exemplos = prever_random_forest(hist, instante, cfg)
            preds["Random Forest"] = (rf, True)
        except Exception as erro:
            falhas.append(f"Random Forest: {erro}")
        if falhas:
            pulados.append({"mes": instante.strftime("%Y-%m"), "motivo": "; ".join(falhas)})
        if set(preds) != set(MODELOS) or not all(p[1] for p in preds.values()):
            continue
        for nome, (estimativa, _) in preds.items():
            erro = estimativa - valor
            previsoes.append({
                "mes": instante.strftime("%Y-%m"), "modelo": nome,
                "real_reais": float(valor * ESCALA),
                "previsto_reais": float(estimativa * ESCALA),
                "erro_reais": float(erro * ESCALA),
                "erro_absoluto_reais": float(abs(erro) * ESCALA),
                "erro_absoluto_escalonado": abs(erro) / denominador,
                "observacoes_historicas": len(hist.dropna()),
                "historico_inicio": hist.index[0].strftime("%Y-%m"),
                "historico_fim": hist.index[-1].strftime("%Y-%m"),
                "meses_ausentes_no_treino": int(hist.isna().sum()),
                "rf_exemplos_treino": exemplos,
            })
        print(f"Avaliado {instante.strftime('%Y-%m')} em quatro modelos (histórico {len(hist.dropna())} meses)", flush=True)
    tabela = pd.DataFrame(previsoes)
    if tabela.empty:
        raise ValueError("Nenhuma origem de previsão válida foi avaliada")
    metricas = []
    for nome in MODELOS:
        reg = tabela.loc[tabela.modelo.eq(nome)]
        e = reg.erro_reais.to_numpy()
        metricas.append({
            "modelo": nome,
            "n_meses": len(reg),
            "MAE_reais": float(np.mean(np.abs(e))),
            "RMSE_reais": float(np.sqrt(np.mean(e**2))),
            "MASE": float(reg.erro_absoluto_escalonado.mean()),
            "viés_medio_reais": float(np.mean(e)),
            "mes_inicial": reg.mes.min(),
            "mes_final": reg.mes.max(),
        })
    return tabela, pd.DataFrame(metricas), pd.DataFrame(pulados)
