# Task Manager

Aplicação de gerenciamento de tarefas construída com FastAPI, SQLAlchemy assíncrono, PostgreSQL e interface SSR com Jinja2.

O projeto oferece:
- API REST versionada (`/api/v1/tasks`) com CRUD completo
- Filtros por prioridade e status de conclusão
- Interface web server-side para criar, editar, concluir e remover tarefas
- Testes automatizados com `pytest` e `httpx`

## Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2 (async)
- PostgreSQL (asyncpg)
- Jinja2 + CSS estático
- Docker + Docker Compose
- Pytest

## Estrutura do projeto

```text
app/
	api/v1/routes/tasks.py    # Endpoints REST de tarefas
	ui/routes.py              # Rotas da interface web
	models/task.py            # Modelo SQLAlchemy + enum de prioridade
	schemas/task.py           # Schemas Pydantic (create, update, response)
	service/task.py           # Regras de CRUD/acesso a dados
	db/session.py             # Engine e sessão assíncrona
	main.py                   # App FastAPI, static, routers e lifespan
tests/
	conftest.py               # Fixtures de banco/sessão/cliente
	test_tasks.py             # Testes da API de tarefas
```

## Pré-requisitos

- Python 3.12+
- PostgreSQL
- Docker e Docker Compose (opcional, para execução em containers)

## Variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Você pode configurar de duas formas:

1. **Via `DATABASE_URL`** (preferível)
2. **Via variáveis separadas** (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.), que são montadas em runtime

Exemplo de `.env`:

```env
# Opção 1 (direta)
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/taskmanager

# Opção 2 (montada pela aplicação)
POSTGRES_USER=usuario
POSTGRES_PASSWORD=senha
POSTGRES_DB=taskmanager
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

APP_HOST=0.0.0.0
APP_PORT=8000
```

## Rodando localmente (sem Docker)

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure o `.env`.

4. Suba a aplicação:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Acesse:

- UI: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Rodando com Docker Compose

Com `.env` preenchido:

```bash
docker compose up --build
```

Serviços:
- App FastAPI: porta `${APP_PORT}` mapeada para `8000`
- Banco PostgreSQL: porta `5432`

Para parar:

```bash
docker compose down
```

## Rodando testes

Os testes usam `pytest` + `httpx` e cobrem criação, listagem, filtros, busca por ID, atualização e remoção.

```bash
pytest -v
```

### Banco para testes (Docker)

Há um compose dedicado para banco de testes:

```bash
docker compose -f docker-compose.test.yml up -d
```

Ele expõe o PostgreSQL na porta `5433`.

## API REST

Base URL: `/api/v1`

### Endpoints

- `POST /tasks` — cria tarefa
- `GET /tasks` — lista tarefas (com filtros opcionais)
- `GET /tasks/{task_id}` — busca tarefa por ID
- `PUT /tasks/{task_id}` — atualiza tarefa
- `DELETE /tasks/{task_id}` — remove tarefa

### Query params de listagem

- `priority`: `high | medium | low`
- `completed`: `true | false`

Exemplo:

```http
GET /api/v1/tasks?priority=high&completed=false
```

### Exemplo de payloads

Criar tarefa:

```json
{
	"title": "Preparar release",
	"description": "Validar checklist final",
	"priority": "high"
}
```

Atualizar tarefa:

```json
{
	"completed": true
}
```

## Interface Web

A interface SSR está disponível em `/` e permite:
- Criar tarefa
- Filtrar por prioridade/status
- Editar tarefa existente
- Alternar status de conclusão
- Excluir tarefa

## Observações

- As tabelas são criadas automaticamente no startup da aplicação (lifecycle em `app.main`).
- O SQLAlchemy está com `echo=True` em `app/db/session.py` (logs SQL habilitados).