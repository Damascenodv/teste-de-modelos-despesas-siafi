# Previsão de Despesas Públicas Federais com Séries Temporais e Aprendizado de Máquina

Projeto desenvolvido no contexto do Trabalho de Conclusão de Curso (TCC) em Ciência da Computação da Universidade Tiradentes (UNIT).

O objetivo é desenvolver e comparar modelos de previsão de despesas públicas federais, utilizando dados abertos do Ministério da Educação (MEC), disponibilizados pelo Portal da Transparência do Governo Federal.

## 1. Sobre o projeto

A aplicação utiliza Python para processar arquivos públicos de execução da despesa e construir uma série temporal mensal dos valores efetivamente pagos pelo MEC.

Foram comparados quatro modelos de previsão:

- **Ingênuo:** utiliza como previsão o valor observado no mês anterior.
- **Ingênuo sazonal:** utiliza o valor observado no mesmo mês do ano anterior.
- **SARIMA:** modelo estatístico para dependências temporais e sazonalidade.
- **Random Forest:** algoritmo de aprendizado supervisionado que utiliza pagamentos anteriores e atributos temporais.

O SIAFI é utilizado como referência para a compreensão dos procedimentos de execução orçamentária e financeira. A coleta dos dados foi realizada por meio dos arquivos públicos do Portal da Transparência, sem acesso direto ao ambiente operacional do SIAFI.

## 2. Fonte dos dados

**Fonte oficial:** [Portal da Transparência — Execução da Despesa](https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao)

**Órgão analisado:** Ministério da Educação (MEC)

**Código do órgão superior:** `26000`

**Variável prevista:** `Valor Pago (R$)`

**Período histórico:** janeiro de 2021 a outubro de 2026.

A base utilizada na última execução local apresentou:

| Indicador | Quantidade |
|---|---:|
| Competências mensais | 70 |
| Meses ausentes | 0 |
| Registros de todos os órgãos | 4.496.840 |
| Registros filtrados do MEC | 1.266.834 |
| Registros do MEC com valor pago negativo | 5.594 |
| Competências avaliadas | 34 |
| Modelos comparados | 4 |

Os valores negativos foram preservados durante a agregação. O campo `Valor Restos a Pagar Pagos (R$)` foi mantido separado e não foi somado automaticamente à variável prevista.

Os quantitativos apresentados correspondem à execução local do projeto, realizada com arquivos obtidos pelo estudante.

## 3. Metodologia

Foi utilizada validação temporal com origem móvel (*rolling-origin backtesting*), horizonte de previsão de um mês e janela crescente de treinamento.

A primeira previsão foi realizada para janeiro de 2024, utilizando 36 meses de histórico, de janeiro de 2021 a dezembro de 2023.

A cada nova competência, o histórico disponível aumentou em um mês.

O último período avaliado foi outubro de 2026, utilizando 69 meses de histórico.

A avaliação compreendeu **34 competências consecutivas, de janeiro de 2024 a outubro de 2026**.

### Configuração dos modelos

| Modelo | Configuração |
|---|---|
| Ingênuo | Valor observado em t−1 |
| Ingênuo sazonal | Valor observado em t−12 |
| SARIMA | (1,0,0)(1,1,0)[12] |
| Random Forest | 200 árvores; `min_samples_leaf=2`; `random_state=42` |

A Random Forest utilizou cinco atributos: valor pago no mês anterior, valor pago 12 meses antes, seno e cosseno do mês do ano e índice temporal.

As previsões foram produzidas a partir dos dados históricos disponíveis até a competência anterior ao mês previsto.

## 4. Resultados experimentais

A última execução local reportou os seguintes resultados:

| Modelo | MAE (R$ bilhões) | RMSE (R$ bilhões) | MASE |
|---|---:|---:|---:|
| Ingênuo | 4,153 | 7,046 | 2,114 |
| Ingênuo sazonal | 2,334 | 2,935 | 1,191 |
| SARIMA | 2,024 | 2,963 | 1,042 |
| **Random Forest** | **1,520** | **2,122** | **0,775** |

A Random Forest apresentou o menor erro nas três métricas.

Em comparação com o modelo ingênuo sazonal, a Random Forest obteve uma redução de aproximadamente **34,88% no MAE**.

Na comparação mensal, apresentou erro absoluto menor que o ingênuo sazonal em **23 das 34 competências avaliadas**.

Esses resultados se referem ao MEC e ao período analisado. Não representam garantia de superioridade do algoritmo em outros órgãos ou períodos.

### Métricas utilizadas

- **MAE:** média dos erros absolutos entre os valores previstos e observados.
- **RMSE:** raiz do erro quadrático médio, que penaliza mais fortemente os erros elevados.
- **MASE:** erro absoluto escalonado pela variação sazonal histórica, calculado com informações anteriores a cada previsão.

Quanto menores os valores dessas métricas, melhor o desempenho observado no protocolo de avaliação.

## 5. Estrutura do projeto

```text
teste-de-modelos-despesas-siafi/
├── src/
│   └── tcc_mec/
│       ├── config.py
│       ├── ingest.py
│       └── backtest.py
├── sql/
│   └── schema.sql
├── tests/
│   ├── test_config.py
│   └── test_pipeline.py
├── extrair_dados.py
├── avaliar_modelos.py
├── gerar_relatorios.py
├── importar_postgres.py
├── verificar_ambiente.py
├── requirements.txt
├── INSTRUCOES_WINDOWS.md
└── README.md
```

### Responsabilidades

**`ingest.py`** realiza a leitura dos ZIPs, filtra os registros do MEC, converte valores monetários e produz a série mensal.

**`backtest.py`** implementa os quatro modelos e calcula as métricas de avaliação.

**`config.py`** centraliza as configurações do ambiente, incluindo caminhos dos arquivos e conexão PostgreSQL.

**`gerar_relatorios.py`** produz gráficos, arquivos de métricas e informações de auditoria.

**`importar_postgres.py`** permite armazenar a série mensal, as previsões e as métricas em PostgreSQL.

## 6. Instalação e execução

### Requisitos

- Python 3.10 ou superior.
- Bibliotecas listadas em `requirements.txt`.
- Arquivos ZIP mensais da Execução da Despesa.
- PostgreSQL, caso seja utilizada a persistência em banco de dados.

O experimento informado foi executado com Python 3.13.1, pandas 2.3.3, NumPy 2.2.6, scikit-learn 1.9.1 e statsmodels 0.14.6.

### Clonar o projeto

```bash
git clone https://github.com/Damascenodv/teste-de-modelos-despesas-siafi.git
cd teste-de-modelos-despesas-siafi
```

### Instalar as dependências

No terminal do Windows:

```powershell
py -m pip install -r requirements.txt
```

### Preparar os arquivos de entrada

Crie uma pasta chamada `Despesas` na raiz do projeto.

Baixe os arquivos oficiais de janeiro de 2021 a outubro de 2026 e coloque os ZIPs nessa pasta, sem extrair.

Exemplo:

```text
Despesas/
├── 202101_Despesas.zip
├── 202102_Despesas.zip
├── 202103_Despesas.zip
├── ...
└── 202610_Despesas.zip
```

Os arquivos originais não são distribuídos neste repositório. Para reproduzir integralmente a série histórica, é necessário obter as 70 competências na fonte oficial.

### Executar o processamento

Na pasta principal do projeto, execute:

```powershell
py extrair_dados.py
```

Esse comando processa os ZIPs e gera a série histórica mensal.

### Executar os modelos

```powershell
py avaliar_modelos.py
```

O programa realiza o backtesting e calcula as métricas dos quatro modelos.

### Gerar os relatórios

```powershell
py gerar_relatorios.py
```

Os resultados são gravados, por padrão, na pasta `resultados`.

Entre os arquivos produzidos estão:

- `serie_mensal_mec.csv`
- `auditoria_arquivos.csv`
- `previsoes_backtest.csv`
- `metricas_tabela2.csv`
- `meses_excluidos_avaliacao.csv`
- `resumo_auditoria.json`
- Gráficos da série e das previsões.

### Executar os testes automatizados

```powershell
py -m pytest -q tests
```

Os testes verificam funções de processamento dos dados e construção dos atributos temporais.

## 7. Configuração do PostgreSQL

O armazenamento em PostgreSQL é uma etapa opcional do pipeline experimental.

Crie um arquivo `.env` na pasta principal do projeto:

```env
DESPESAS_DIR=Despesas
RESULTADOS_DIR=resultados
ULTIMO_MES=2026-10
DATABASE_URL=postgresql://postgres:SUA_SENHA_LOCAL@localhost:5432/errorbot
```

Substitua `SUA_SENHA_LOCAL` pela senha configurada no PostgreSQL.

O banco utilizado nesse exemplo chama-se `errorbot`, mas o projeto permite alterar o nome na URL.

**O arquivo `.env` contém configurações locais e não deve ser publicado no GitHub.**

Para verificar a conexão:

```powershell
py verificar_ambiente.py
```

Para importar os resultados:

```powershell
py importar_postgres.py
```

O importador utiliza o esquema `tcc_mec`, definido em `sql/schema.sql`.

Exemplo de consulta SQL:

```sql
SELECT *
FROM tcc_mec.metricas
ORDER BY mae_reais;
```

A execução dos experimentos não depende da disponibilidade do PostgreSQL. A persistência no banco pode ser realizada posteriormente.

## 8. Reprodutibilidade e limitações

O projeto disponibiliza o código-fonte, as dependências, os testes e os comandos necessários para reproduzir o processamento e a avaliação.

A reprodução dos mesmos resultados depende da utilização dos arquivos oficiais correspondentes às competências analisadas, da configuração dos modelos e de versões compatíveis das bibliotecas.

Os arquivos podem ser atualizados ou retificados pelo órgão responsável, ocasionando diferenças em execuções posteriores.

As principais limitações são o estudo de um único órgão superior, a utilização de valores nominais e a ausência de variáveis externas, como mudanças orçamentárias, decisões administrativas e informações macroeconômicas.

O estudo avalia a capacidade de previsão no período observado. Não estabelece relações causais nem constitui uma ferramenta homologada para tomada automática de decisões orçamentárias.

**Observação técnica:** a versão atualmente publicada de `gerar_relatorios.py` ainda possui descrições fixas referentes a uma execução anterior, com meses não consecutivos e 19 origens. Esses textos e nomes de arquivos devem ser atualizados para refletir os 34 meses consecutivos da execução mais recente. Isso não altera, por si só, os valores calculados pelos modelos.

## 9. Uso de inteligência artificial

Ferramentas de inteligência artificial generativa foram utilizadas como apoio à organização da pesquisa, à elaboração e revisão de código, à documentação, à explicação de conceitos e à revisão textual.

A obtenção dos arquivos de dados e a execução local dos experimentos foram realizadas pelo estudante.

A interpretação, a revisão crítica, a validação dos procedimentos e a responsabilidade acadêmica pelo trabalho permanecem sob responsabilidade do estudante.

## 10. Referências principais

- BRASIL. Controladoria-Geral da União. [Portal da Transparência — Execução da Despesa](https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao).
- BRASIL. Secretaria do Tesouro Nacional. [SIAFI](https://www.gov.br/tesouronacional/pt-br/siafi).
- HYNDMAN, R. J.; ATHANASOPOULOS, G. [Forecasting: Principles and Practice](https://otexts.com/fpp3/). 3ª edição, 2021.
- BREIMAN, L. [Random Forests](https://doi.org/10.1023/A:1010933404324). Machine Learning, 2001.
- PEDREGOSA, F. et al. [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html). Journal of Machine Learning Research, 2011.

---

**Projeto acadêmico — Ciência da Computação — Universidade Tiradentes (UNIT).**
