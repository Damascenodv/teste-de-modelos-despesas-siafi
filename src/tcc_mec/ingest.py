"""Ingestão reproduzível dos arquivos mensais de Execução da Despesa da CGU."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import re
import zipfile

import pandas as pd

MES = "Ano e mês do lançamento"
ORGAO = "Código Órgão Superior"
PAGO = "Valor Pago (R$)"
RESTOS = "Valor Restos a Pagar Pagos (R$)"
CAMPOS = [MES, ORGAO, PAGO, RESTOS]
MEC = "26000"
MES_NO_ARQUIVO = re.compile(r"^(\d{6})_Despesas(?:\s*\(\d+\))?\.zip$", re.IGNORECASE)


@dataclass(frozen=True)
class Registro:
    mes: str
    arquivo: str
    sha256: str
    registros_totais: int
    registros_mec: int
    valores_negativos_mec: int
    pagos_centavos: int
    restos_pagos_centavos: int
    divergencias_competencia: int


def centavos(serie: pd.Series) -> pd.Series:
    texto = serie.fillna("0").astype("string").str.strip()
    texto = texto.str.replace(".", "", regex=False).str.replace(",", "", regex=False)
    valido = texto.str.fullmatch(r"[+-]?\d+")
    if not bool(valido.all()):
        raise ValueError(f"Valores monetários inválidos: {texto[~valido].head(3).tolist()}")
    return texto.astype("int64")


def selecionar_arquivos(diretorio: Path) -> tuple[dict[str, Path], list[dict]]:
    encontrados: dict[str, list[Path]] = {}
    for caminho in sorted(diretorio.glob("*Despesas*.zip")):
        match = MES_NO_ARQUIVO.match(caminho.name)
        if match:
            encontrados.setdefault(match.group(1), []).append(caminho)
    escolhidos: dict[str, Path] = {}
    duplicados: list[dict] = []
    for mes, caminhos in sorted(encontrados.items()):
        caminho_principal = min(caminhos, key=lambda p: (len(p.name), p.name))
        digest = sha256(caminho_principal.read_bytes()).hexdigest()
        escolhidos[mes] = caminho_principal
        for outro in caminhos:
            if outro == caminho_principal:
                continue
            igual = sha256(outro.read_bytes()).hexdigest() == digest
            duplicados.append({"mes": mes, "arquivo": outro.name, "igual_ao_principal": igual})
            if not igual:
                raise ValueError(f"ZIP duplicado com conteúdo diferente para {mes}: {outro.name}")
    return escolhidos, duplicados


def ler_mes(caminho: Path, mes_esperado: str, orgao: str = MEC) -> Registro:
    with zipfile.ZipFile(caminho) as arquivo:
        if arquivo.testzip() is not None:
            raise ValueError(f"ZIP corrompido: {caminho.name}")
        csvs = [a for a in arquivo.namelist() if a.lower().endswith(".csv")]
        if len(csvs) != 1:
            raise ValueError(f"ZIP deve conter um único CSV: {caminho.name}")
        totais = 0
        cont_mec = 0
        negativos = 0
        pago = 0
        restos = 0
        divergentes = 0
        with arquivo.open(csvs[0]) as stream:
            for bloco in pd.read_csv(
                stream, sep=";", encoding="latin-1", usecols=CAMPOS,
                dtype="string", chunksize=80_000, keep_default_na=False,
            ):
                totais += len(bloco)
                competencia = bloco[MES].str.replace("/", "", regex=False)
                divergentes += int(competencia.ne(mes_esperado).sum())
                selecionados = bloco.loc[bloco[ORGAO].eq(orgao)]
                if selecionados.empty:
                    continue
                pagos = centavos(selecionados[PAGO])
                res = centavos(selecionados[RESTOS])
                cont_mec += len(selecionados)
                negativos += int((pagos < 0).sum())
                pago += int(pagos.sum())
                restos += int(res.sum())
    if divergentes:
        raise ValueError(f"Competência divergente em {caminho.name}: {divergentes}")
    return Registro(
        mes=f"{mes_esperado[:4]}-{mes_esperado[4:]}", arquivo=caminho.name,
        sha256=sha256(caminho.read_bytes()).hexdigest(),
        registros_totais=totais, registros_mec=cont_mec,
        valores_negativos_mec=negativos, pagos_centavos=pago,
        restos_pagos_centavos=restos, divergencias_competencia=divergentes,
    )


def executar(diretorio: Path, saida: Path, ultimo_mes: str = "2026-10") -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    saida.mkdir(parents=True, exist_ok=True)
    arquivos, duplicados = selecionar_arquivos(diretorio)
    lista = []
    for chave, caminho in arquivos.items():
        mes = f"{chave[:4]}-{chave[4:]}"
        if mes > ultimo_mes:
            continue
        resultado = ler_mes(caminho, chave)
        lista.append(asdict(resultado))
        print(f"{mes} MEC: {resultado.registros_mec:>7,} linhas; R$ {resultado.pagos_centavos/100:>19,.2f}", flush=True)
    auditoria = pd.DataFrame(lista).sort_values("mes").reset_index(drop=True)
    serie = auditoria[["mes", "pagos_centavos"]].copy()
    serie["valor_pago_reais"] = serie["pagos_centavos"] / 100
    serie["fonte"] = "Portal da Transparência Federal - Execução da Despesa (ZIP fornecido pelo estudante)"
    serie["orgao_superior"] = MEC
    auditoria.to_csv(saida / "auditoria_arquivos.csv", index=False, encoding="utf-8-sig")
    serie.to_csv(saida / "serie_mensal_mec.csv", index=False, encoding="utf-8-sig", float_format="%.2f")
    pd.DataFrame(duplicados).to_csv(saida / "duplicados_conferidos.csv", index=False)
    return serie, auditoria, duplicados
