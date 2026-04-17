# AGENTS.md

## Dev Setup (3 terminals required)

```bash
# Terminal 1: Tailwind watcher
cd theme/static_src && npm run start

# Terminal 2: Django dev server  
source .venv/bin/activate
python manage.py runserver

# Terminal 3: Background worker (required for posts to publish)
source .venv/bin/activate
python manage.py process_tasks
```

## Commands

```bash
# Test single app
pytest apps/<app_name>/

# Lint + format fix
ruff check --fix .
ruff format .

# Type check
mypy apps/ config/ providers/ --ignore-missing-imports

# Run with coverage
pytest --cov=apps --cov-report=term-missing
```

## CI Pipeline Order

`ruff check` → `ruff format --check` → `mypy` → `pytest` → `Docker build` → `gitleaks`

## Key Facts

- **Python**: 3.12+ required
- **Database**: SQLite for local dev, PostgreSQL for tests/prod
- **Test settings**: Uses `config.settings.test` (set via `DJANGO_SETTINGS_MODULE`)
- **Mypy config**: Django plugin enabled via `config.settings.development`
- **Background tasks**: django-background-tasks (no Redis required)
- **CodeGraph**: Available - use `codegraph_search`, `codegraph_callers`, `codegraph_callees` for exploration

## Environment

- Copy `.env.example` to `.env` before running
- Key vars: `SECRET_KEY`, `DEBUG=true`, `DATABASE_URL=sqlite:///db.sqlite3` (local)