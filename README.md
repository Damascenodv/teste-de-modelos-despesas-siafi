# Experimentos reais do TCC — MEC (órgão superior 26000)

**Executado em 11 de novembro de 2026 com arquivos fornecidos pelo estudante.** O pacote contém resultados de um experimento real, e não de dados simulados. A autoria do TCC e a conferência final dos resultados continuam sob responsabilidade do estudante e do orientador; o uso extensivo de IA está declarado no artigo.

## Resultado

Foram lidos **63 ZIPs mensais distintos**, cobrindo janeiro de 2021 a outubro de 2026, com sete arquivos faltantes. Foram examinadas **4.008.994 linhas** de vários órgãos, das quais **1.127.075** pertenciam ao MEC (código 26000); **4.798** registros do MEC tinham pagamentos negativos e foram preservados.

Os quatro métodos foram comparados nas **mesmas 19 origens mensais de previsão**, distribuídas entre janeiro de 2024 e outubro de 2026, com horizonte de **um mês à frente**:

| Modelo | MAE (R$ bilhões) | RMSE (R$ bilhões) | MASE |
| --- | ---: | ---: | ---: |
| Ingênuo | 5,131 | 8,420 | 2,771 |
| Ingênuo sazonal | 2,210 | 2,877 | 1,185 |
| SARIMA(1,0,0)(1,1,0)[12] | 2,378 | 3,277 | 1,276 |
| Random Forest | **1,490** | **2,137** | **0,793** |

A Random Forest teve MAE **32,58% inferior** ao ingênuo sazonal, com erro absoluto menor em **14/19** origens. Isso **não prova superioridade estatística geral**: os meses avaliados não são consecutivos e há lacunas no histórico.

## O que falta

Sete competências de 2021 a 2025 não foram enviadas: **202303, 202412, 202505, 202506, 202507, 202508 e 202509**. O ZIP de **novembro de 2026** foi excluído porque novembro ainda estava em curso na data desta execução. Não se atribuiu zero nem se inventaram valores para essas competências.

O PostgreSQL **não foi executado neste ambiente** por ausência de servidor e acesso. O esquema e o importador estão prontos para execução em uma instância própria. Os hashes SHA-256 verificam a integridade das cópias recebidas, mas **não certificam sua correspondência com um checksum publicado pela CGU**. Recomenda-se confrontar amostras com a consulta oficial antes da defesa.

## Metodologia

- Fonte declarada: Portal da Transparência federal, conjunto "Execução da Despesa", ZIPs mensais fornecidos pelo estudante.
- Unidade mensal: `Ano e mês do lançamento`; filtro: `Código Órgão Superior = 26000`.
- Variável de resposta: soma de `Valor Pago (R$)` com valores convertidos para centavos inteiros. Não adicionar `Valor Restos a Pagar Pagos (R$)`.
- Duplicatas: nove arquivos repetidos tinham SHA-256 idêntico e foram descartados.
- Origem móvel: cada mês `t` é previsto com histórico conhecido até `t−1`; só entram origens com valor real, lag de 1 mês, lag de 12 meses e histórico mínimo de 30 observações.
- SARIMA: (1,0,0)(1,1,0)[12], meses ausentes tratados como NaN na estimação do espaço de estados; sem imputação.
- Random Forest: 200 árvores, mínimo de 2 observações por folha, semente 42; atributos lag 1, lag 12, seno/cosseno do mês e índice temporal. Exemplos com defasagens ausentes são omitidos do treino.
- MASE: média de cada erro absoluto de teste dividido pelo erro sazonal médio `|y_i−y_{i−12}|` estimado exclusivamente no treino até a origem de cada previsão.

## Arquivos principais

- `Artigo_TCC_MEC_Resultados_Experimentais_Reais.docx` / `.pdf`: artigo SBC com Tabela 2 preenchida, gráficos, metodologia e declaração de IA.
- `resultados/serie_mensal_mec.csv`: pagamentos mensais em centavos exatos, fonte e órgão.
- `resultados/auditoria_arquivos.csv`: contagens por arquivo, soma dos valores e SHA-256.
- `resultados/duplicados_conferidos.csv`: ZIPs repetidos descartados.
- `resultados/previsoes_backtest.csv`: **76 previsões** com valores reais, estimados e erros.
- `resultados/metricas_tabela2.csv`: resultados sem arredondamento de apresentação.
- `resultados/meses_excluidos_avaliacao.csv`: meses faltantes ou sem lags elegíveis.
- `resultados/resumo_auditoria.json`: relatório legível por máquinas, configurações e versões.
- `resultados/figura_serie_historica.png`, `resultados/figura_previsoes_19_origens.png`.
- `sql/schema.sql` e `importar_postgres.py`: esquema e carga opcionais em PostgreSQL.

## Como reproduzir

Requisitos: Python 3.10+ e os ZIPs originais numa pasta local (um arquivo `AAAAMM_Despesas.zip` por competência).

```bash
python -m pip install -r requirements.txt
python extrair_dados.py --entrada /caminho/para/os_zips --ultimo-mes 2026-10
python avaliar_modelos.py
python gerar_relatorios.py
python -m pytest -q tests
```

A regeneração do DOCX depende do rascunho anterior usado no desenvolvimento, ainda referenciado por caminho absoluto em `atualizar_artigo.py`; o artigo DOCX e PDF já finalizados encontram-se incluídos no pacote. Os **resultados experimentais** são reproduzíveis apenas com os ZIPs, bibliotecas e scripts de extração/avaliação acima, sem qualquer rascunho.

### Carga posterior no PostgreSQL

1. Disponibilizar um servidor PostgreSQL e criar uma base de dados.
2. Configurar a variável de ambiente `DATABASE_URL` com credenciais **no seu próprio computador**, sem enviá-las pelo chat.
3. Executar `python importar_postgres.py` após gerar os CSVs.

`importar_postgres.py` contém inserções idempotentes (`ON CONFLICT`) e cria o esquema `tcc_mec`. Essa carga **não foi validada contra uma instância PostgreSQL nesta sessão**.

## Limitações acadêmicas

1. Os 19 meses de teste são **não consecutivos**, logo não são equivalentes a um ano de validação completo.
2. A seleção de origens depende da disponibilidade dos ZIPs e das defasagens, podendo afetar a representatividade.
3. Para avaliação de implantação, completar as sete competências, reconciliar totais do portal, realizar o backtest em ano contínuo e examinar intervalos de incerteza.
4. A comparação não é causal e não representa previsão operacional homologada do MEC.
