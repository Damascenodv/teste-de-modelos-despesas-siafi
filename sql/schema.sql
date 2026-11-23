CREATE SCHEMA IF NOT EXISTS tcc_mec;

CREATE TABLE IF NOT EXISTS tcc_mec.execucao_mensal (
    mes DATE PRIMARY KEY,
    codigo_orgao_superior VARCHAR(5) NOT NULL DEFAULT '26000',
    valor_pago NUMERIC(22,2) NOT NULL,
    valor_restos_pagar_pagos NUMERIC(22,2) NOT NULL,
    total_registros_mec INTEGER NOT NULL,
    registros_negativos INTEGER NOT NULL,
    arquivo_fonte TEXT NOT NULL,
    sha256_zip CHAR(64) NOT NULL,
    importado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT mec_fixo CHECK (codigo_orgao_superior = '26000')
);

CREATE TABLE IF NOT EXISTS tcc_mec.previsao_backtest (
    mes DATE NOT NULL,
    modelo TEXT NOT NULL,
    valor_real NUMERIC(22,2) NOT NULL,
    valor_previsto NUMERIC(22,2) NOT NULL,
    erro_absoluto NUMERIC(22,2) NOT NULL,
    mase_erro NUMERIC(16,8) NOT NULL,
    historico_observacoes INTEGER NOT NULL,
    PRIMARY KEY (mes,modelo)
);

CREATE TABLE IF NOT EXISTS tcc_mec.metricas (
    modelo TEXT PRIMARY KEY,
    n_meses INTEGER NOT NULL,
    mae_reais NUMERIC(22,2) NOT NULL,
    rmse_reais NUMERIC(22,2) NOT NULL,
    mase NUMERIC(16,8) NOT NULL
);
