# Viva le Hack Backend

![Champ illustration](./assets/champ-img.png)

Production-ready FastAPI backend with Pydantic validation, Dramatiq workers, and Redis integration.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python dependency manager)
- [ruff](https://docs.astral.sh/ruff/) (linter/formatter)

---

## Environment Setup

1. Copy `.env.template` to `.env` and adjust variables as needed.

---

## Quick Start

### 1. Initialize the environment

```sh
make init
```

### 2. Build Docker containers

```sh
make build
```

### 3. Start all services (FastAPI app, Redis, Dramatiq worker)

```sh
make start
```

- The API will be available at [http://localhost:8688](http://localhost:8688) by default.

### 4. Stop services

```sh
make stop
```

### 5. Clean up containers and volumes

```sh
make clean
```

---

## Code Quality

- Lint and check code:

  ```sh
  make check
  ```

- Format code:

  ```sh
  make format
  ```

## MCP config

```json
{
  "mcpServers": {
    "lab": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/Users/louisbrulenaudet/Documents/Développement informatique/Python/viva-le-hack-backend",
        "run",
        "-m",
        "app.mcp_server"
      ],
      "autoApprove": [
        "get_database_tables",
        "get_database_schema",
        "query_db"
      ]
    }
  }
}
```
