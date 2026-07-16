# AI SOC Triage

Sistema de triagem inteligente para alertas do Wazuh utilizando Inteligência Artificial local (Ollama + Gemma), regras customizadas de risco e interface web em FastAPI.

## Demonstração

Dashboard Web

- Dashboard em tempo real
- Estatísticas dos alertas
- Classificação automática de risco
- Pré-triagem utilizando IA Local
- Histórico de eventos
- Busca e filtros

---

# Arquitetura

```
                +------------------+
                | Wazuh Indexer    |
                +--------+---------+
                         |
                         |
               IndexerClient
                         |
               Alert Parser
                         |
              Rules Engine
                         |
              Risk Engine
                         |
                AI Triage (Ollama)
                         |
             Serializer / API
                         |
                  FastAPI Web
                         |
                 Dashboard HTML
```

---

# Tecnologias

- Python 3.10+
- FastAPI
- Jinja2
- Ollama
- Gemma 3 1B
- Wazuh Indexer
- Elasticsearch API
- HTML
- CSS
- JavaScript
- Chart.js

---

# Funcionalidades

## Dashboard

- Total de alertas
- Alertas por criticidade
- Estatísticas
- Distribuição por agente
- Atualização em tempo real

---

## Busca

Permite pesquisar por

- IP
- Usuário
- Rule ID
- Descrição

---

## Filtros

- Risk
- Agent
- MITRE ATT&CK

---

## Histórico

Todos os alertas processados podem ser consultados posteriormente.

---

## Motor de Risco

Cada alerta passa por duas etapas.

### Rules Engine

Aplica regras específicas para identificar comportamentos suspeitos.

Exemplo

- SSH Brute Force
- Múltiplos logins
- Eventos PAM
- Escalação de privilégio

### Risk Engine

Calcula automaticamente:

- LOW
- MEDIUM
- HIGH
- CRITICAL

Além disso gera:

- Score
- Motivos da classificação

---

## IA

A IA recebe:

- Rule ID
- Descrição
- Usuário
- Host
- MITRE
- IP Origem
- Score
- Risco

E gera automaticamente:

- Resumo
- Avaliação da ameaça
- Motivo
- Recomendações

Tudo utilizando um modelo local através do Ollama.

Nenhum dado é enviado para APIs externas.

---

# Estrutura

```
soc-alert-triage/

├── clients/
│   ├── indexer_client.py
│   └── wazuh_api.py
│
├── logs/
│
├── models/
│
├── parsers/
│
├── services/
│   ├── ai_triage.py
│   ├── history_manager.py
│   ├── risk_engine.py
│   └── rules_engine.py
│
├── web/
│   ├── static/
│   ├── templates/
│   ├── serializers/
│   ├── services/
│   └── app.py
│
├── main.py
└── README.md
```

---

# Instalação

## Clone o projeto

```bash
git clone https://github.com/SEU_USUARIO/soc-alert-triage.git

cd soc-alert-triage
```

---

## Criar ambiente virtual

Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Configuração

Edite o arquivo

```
.env
```

Exemplo

```
INDEXER_HOST=https://localhost:9200
INDEXER_USER=admin
INDEXER_PASSWORD=admin
VERIFY_SSL=False
```

---

# Instalando o Ollama

Instale:

https://ollama.com

Depois execute

```bash
ollama pull gemma3:1b
```

Inicie o serviço

```bash
ollama serve
```

Verifique

```bash
ollama list
```

---

# Executando

Modo terminal

```bash
python main.py
```

---

Modo Web

```bash
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

Depois abra

```
http://localhost:8000
```

ou

```
http://IP_DA_VM:8000
```

---

# Fluxo da Aplicação

```
Wazuh

↓

Indexer

↓

Parser

↓

Rules Engine

↓

Risk Engine

↓

IA (Gemma)

↓

Serializer

↓

Dashboard
```

---

# Exemplo de Triagem

```
Rule

5502

Descrição

PAM: Login session closed

↓

Risk

MEDIUM

↓

Score

20

↓

IA

Summary

Sessão PAM encerrada normalmente.

Threat

Baixa

Reason

Evento comum de autenticação.

Recommended Actions

• Validar usuário
• Verificar horário
• Correlacionar com logins anteriores
```

---

# API

## Alertas

```
GET /alerts
```

---

## Estatísticas

```
GET /statistics
```

---

## Histórico

```
GET /history
```

---

## Detalhes

```
GET /alerts/{id}
```

---

## Filtros

```
GET /filters
```

---

## Health

```
GET /health/ollama
```

---

# Objetivo

Este projeto foi desenvolvido para demonstrar conhecimentos em:

- SOC Analyst
- Blue Team
- Detection Engineering
- SIEM
- Wazuh
- Python
- FastAPI
- Inteligência Artificial Local
- MITRE ATT&CK
- Análise de Eventos
- Desenvolvimento Back-end

---

# Autor

**João Vitor Cordeiro Cardoso**

LinkedIn

https://www.linkedin.com/in/joao-vitor-90a5291a4/

GitHub

https://github.com/joaovitorcardoso515-bit