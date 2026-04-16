# Meet Check-in App

Aplicação em Streamlit rodando no Databricks para controle de presença em reuniões via link dinâmico.

## Funcionalidades

* Check-in via link único (`token`)
* Validação de CPF
* Controle de acesso por horário (5 min antes até 1h depois)
* Expiração e desativação de links
* Registro em tabela Delta (Databricks)
* Redirecionamento automático para Google Meet
* Prevenção de acessos fora da janela permitida

## Arquitetura

* **Frontend:** Streamlit (Databricks Apps)
* **Backend:** Databricks SQL Warehouse
* **Storage:** Delta Tables
* **Autenticação:** Token via query param (`hash_link`)

## Estrutura do Projeto

```
.
├── app.py                # Aplicação principal
├── requirements.txt     # Dependências
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_seed_data.sql
│   ├── 03_views.sql
```

## Como executar

1. Criar as tabelas:

```sql
-- rodar arquivos em /sql
```

2. Deploy no Databricks Apps

3. Acessar via:

```
https://<app-url>/?token=<hash_link>
```

## Segurança

* Links controlados por `hash_link`
* Possibilidade de expiração (`expira_em`)
* Desativação manual (`ativo = false`)
* Validação dupla de horário (frontend + ação)

## Próximos passos

* Dashboard de presença
* Controle de duplicidade por CPF
* Envio automático de links


## Autora

Larissa Borges
