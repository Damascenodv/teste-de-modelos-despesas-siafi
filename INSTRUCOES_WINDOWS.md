# Configuração no Windows — MEC e PostgreSQL

Este projeto usa os ZIPs públicos de despesas do Ministério da Educação (órgão 26000).

## 1. Configurar ambiente

Na pasta principal do projeto, copie `.env.example` para `.env` e edite a linha `DATABASE_URL` com a senha do seu usuário PostgreSQL.

```env
DESPESAS_DIR=Despesas
RESULTADOS_DIR=resultados
ULTIMO_MES=2026-10
DATABASE_URL=postgresql://postgres:SUA_SENHA_AQUI@localhost:5432/errorbot
```

**Não use o prefixo `jdbc:` no Python.** O prefixo é de aplicativos Java.
Não envie `.env` por mensagem, não o publique no GitHub e altere a senha padrão do PostgreSQL quando possível.
Se a senha contiver caracteres especiais como `@`, `#`, `/`, `:` ou `?`, codifique-os na URL ou use parâmetros separados.

## 2. Banco de dados

No pgAdmin, confirme a existência do banco `errorbot`. Se ele não existir, conecte-se ao banco `postgres` e execute:

```sql
CREATE DATABASE errorbot;
```

O script `importar_postgres.py` cria automaticamente o esquema `tcc_mec` e suas três tabelas.

## 3. Arquivos de entrada

Coloque os arquivos `AAAAMM_Despesas.zip` dentro da pasta `Despesas`, sem extrair.

## 4. Instalação e execução

Abra o PowerShell na pasta principal (onde estão os arquivos `.py`) e execute:

```powershell
py -m pip install -r requirements.txt
py verificar_ambiente.py
py extrair_dados.py
py avaliar_modelos.py
py gerar_relatorios.py
py importar_postgres.py
```

Os CSVs e gráficos ficam na pasta `resultados`.

## 5. Consultas para conferir no pgAdmin

```sql
SELECT * FROM tcc_mec.execucao_mensal ORDER BY mes DESC LIMIT 10;
SELECT * FROM tcc_mec.metricas ORDER BY mae_reais;
SELECT modelo, count(*) AS previsoes FROM tcc_mec.previsao_backtest GROUP BY modelo;
```

## 6. Variáveis de ambiente em vez de `.env`

Se preferir usar variáveis de ambiente do Windows, configure `DATABASE_URL`, `DESPESAS_DIR`, `RESULTADOS_DIR` e `ULTIMO_MES` no sistema. O Python lê as variáveis do processo e usa `.env` apenas como fallback.
