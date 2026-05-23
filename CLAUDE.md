# CLAUDE.md — compose-for-agents Codebase Guide

This file provides context for AI assistants working in this repository.

---

## Project Overview

**compose-for-agents** is a collection of self-contained Docker Compose demos, each showcasing a different AI agent framework running locally (or in the cloud). The demos use Docker Model Runner for local models and an MCP Gateway for secure MCP server access.

- **Repository:** `hanyy07/compose-for-agents`
- **Primary branch:** `main`
- **License:** Apache-2.0 OR MIT (dual-licensed); individual demos may carry their own `LICENSE` file
- **Prerequisites:** Docker Desktop 4.43.0+ or Docker Engine; GPU recommended for local models

---

## Repository Layout

```
compose-for-agents/
├── Taskfile.yaml                  # Task runner: lint targets
├── Dockerfile.tools               # Builds markdownlint + yamllint Docker images
├── .markdownlint.yaml             # Markdown lint rules
├── .markdownlint-cli2.yaml        # markdownlint-cli2 config
├── .yamllint                      # YAML lint rules
├── .gitattributes
├── .gitignore
├── LICENSE.APACHE-2
├── LICENSE.MIT
├── README.md
├── .github/
│   ├── actions/
│   │   └── setup-compose/         # Reusable action: install Docker Compose
│   └── workflows/
│       ├── a2a.yaml               # CI for a2a demo
│       ├── adk.yaml               # CI for adk demo
│       ├── adk-cerebras.yaml      # CI for adk-cerebras demo
│       ├── agno.yaml              # CI for agno demo
│       ├── akka.yaml              # CI for akka demo
│       ├── crew-ai.yaml           # CI for crew-ai demo
│       ├── langgraph.yaml         # CI for langgraph demo
│       ├── markdownlint.yaml      # Repo-wide markdown linting
│       └── yamllint.yaml          # Repo-wide YAML linting
├── a2a/                           # A2A Multi-Agent Fact Checker
├── adk/                           # Google ADK Multi-Agent Fact Checker
├── adk-cerebras/                  # ADK + Cerebras Golang Experts
├── adk-sock-shop/                 # ADK Sock Store Agent
├── agno/                          # Agno GitHub Issue Summarizer
├── akka/                          # Akka HelloWorld Agent (Java)
├── crew-ai/                       # CrewAI Marketing Strategy Agent
├── embabel/                       # Embabel Travel Agent
├── langchaingo/                   # LangChainGo DuckDuckGo Search
├── langgraph/                     # LangGraph SQL Agent + PostgreSQL
├── minions/                       # MinionS Local-Remote Collaboration
└── spring-ai/                     # Spring AI Brave Search
```

---

## Demos

| Demo | Agent System | Model(s) | MCPs |
|---|---|---|---|
| `a2a` | A2A Multi-Agent | OpenAI | duckduckgo |
| `adk` | Google ADK Multi-Agent | gemma3-qat (local) | duckduckgo |
| `adk-cerebras` | ADK + Cerebras | qwen3 (local) + llama-4-scout (Cerebras) | — |
| `adk-sock-shop` | Google ADK Multi-Agent | qwen3 (local) | MongoDB, Brave, Curl |
| `agno` | Agno Multi-Agent | qwen3 (local) | github-official |
| `akka` | Akka (Java) | — | — |
| `crew-ai` | CrewAI Multi-Agent | qwen3 (local) | duckduckgo |
| `embabel` | Embabel Multi-Agent | qwen3, Claude 3.7, llama3.2 | brave, github, weather, maps, airbnb |
| `langchaingo` | LangChainGo Single-Agent | gemma3 (local) | duckduckgo |
| `langgraph` | LangGraph Single-Agent | qwen3 (local) | postgres |
| `minions` | MinionS Local-Remote | qwen3 (local) + gpt-4o (remote) | — |
| `spring-ai` | Spring AI Single-Agent | — | duckduckgo |

---

## Running a Demo

Each demo is self-contained. Steps:

```bash
cd <demo-dir>

# (If the demo has a mcp.env.example) create the secrets file:
cp mcp.env.example .mcp.env
# then edit .mcp.env and fill in required API tokens

# Start the demo (builds images automatically):
docker compose up --build
```

### Using OpenAI Instead of Local Models

All demos support OpenAI as a drop-in alternative to Docker Model Runner:

```bash
# 1. Create the API key secret file:
echo "sk-..." > secret.openai-api-key

# 2. Start with the OpenAI overlay:
docker compose -f compose.yaml -f compose.openai.yaml up
```

### Compose File Variants

| File | Purpose |
|---|---|
| `compose.yaml` | Default — local models via Docker Model Runner |
| `compose.openai.yaml` | Override to use OpenAI instead of local models |
| `compose.dmr.yaml` | Docker Model Runner explicit config |
| `compose.offload.yaml` | Docker Offload (GPU-less environments) |
| `compose.gcloud.yaml` / `compose.gcloudrun.yaml` | Google Cloud Run deployment |

---

## Python Project Conventions

Python-based demos use **UV** as the package manager (faster than pip, lock-file based).

### Toolchain

| Tool | Purpose |
|---|---|
| `uv` | Package management, virtual env, running scripts |
| `ruff` | Formatter + linter (replaces black + flake8) |
| `pyright` | Static type checker |

### Key Config Files

- `pyproject.toml` — project metadata, dependencies, dev dependencies
- `uv.lock` — pinned dependency graph (commit this file)
- `.ruff.toml` — ruff configuration (line length, rules)

### Standard `pyproject.toml` Structure

```toml
[project]
requires-python = ">=3.13"
dependencies = [...]

[dependency-groups]
dev = ["ruff>=...", "pyright>=...", ...]
```

### Lint + Type Check Commands (Python demos)

```bash
uv run ruff format --check    # Check formatting
uv run ruff format            # Fix formatting
uv run ruff check             # Lint
uv run ruff check --fix       # Fix lint issues
uv run pyright                # Type check
```

---

## Non-Python Demos

| Demo | Language | Build Tool |
|---|---|---|
| `akka` | Java | Maven (`pom.xml`) |
| `langchaingo` | Go | Go modules (`go.mod`) |
| `spring-ai` | Java | Maven |
| `embabel` | Java/Kotlin | Maven |

---

## Linting (Repo-Wide)

Uses [Task](https://taskfile.dev) as the task runner. Linters run inside Docker.

```bash
task lint              # Run markdown + YAML lint
task lint:markdown     # Markdown only
task lint:markdown:fix # Markdown + auto-fix
task lint:yaml         # YAML only
```

The `task build:markdownlint` and `task build:yamllint` targets build the Docker images that the lint tasks run in (pulled from `Dockerfile.tools`). These run automatically as dependencies.

---

## CI/CD

Each demo has a dedicated GitHub Actions workflow in `.github/workflows/<demo>.yaml`.

**Trigger pattern** (example from `langgraph.yaml`):
```yaml
on:
  push:
    paths:
      - .github/workflows/langgraph.yaml
      - langgraph/**
    branches: [main]
  pull_request:
    paths:
      - .github/workflows/langgraph.yaml
      - langgraph/**
```

**Standard CI jobs for Python demos:**
1. **Format & Type Check** — installs UV, runs `ruff format --check`, `ruff check`, `pyright`
2. **Build** — runs `docker compose build`

Repo-wide linting runs in `markdownlint.yaml` and `yamllint.yaml`.

---

## Secrets and Environment Variables

| Secret/File | Purpose |
|---|---|
| `.mcp.env` | MCP-specific tokens (copy from `mcp.env.example`) — gitignored |
| `secret.openai-api-key` | OpenAI API key (plain text file) — gitignored |

Never commit either of these files. Both are listed in `.gitignore`.

---

## Adding a New Demo

1. Create a new directory at the repo root: `<demo-name>/`
2. Add a `compose.yaml` with services for your agent and any MCPs it needs
3. Add `mcp.env.example` if the demo requires secrets
4. For Python: initialize with `uv init`, add `ruff` and `pyright` to `[dependency-groups] dev`
5. Add a `README.md` explaining what the demo does and how to run it
6. Add a CI workflow at `.github/workflows/<demo-name>.yaml` following the trigger pattern above
7. Add a row to the demo table in the root `README.md`

---

## Key Conventions

- **One demo = one directory** — each demo is fully self-contained with its own `compose.yaml`
- **No shared runtime dependencies** across demos — each has its own `pyproject.toml` / `go.mod`
- **ESM port standards:** MCP Gateway runs on `8811`; agent APIs typically on `8001` or `8080`
- **Python 3.13+** for all Python demos
- **Commit `uv.lock`** — do not gitignore lock files in Python demos
- **Dual license header:** new files in the repo root should carry `SPDX-License-Identifier: Apache-2.0 OR MIT`

---

## AI Assistant Rules

### Do

- **Read before editing** — always read a file before modifying it
- **Minimal changes** — do only what the task requires
- **Confirm before destructive actions** — ask before force push, branch deletion
- **Commit to the designated branch** — currently `claude/claude-md-docs-g4eAV`

### Do Not

- Push to `main`
- Modify multiple unrelated demos in one commit
- Commit `.mcp.env` or `secret.openai-api-key`
- Add `# TODO` or `# FIXME` comments — open a GitHub issue instead

---

## Updating This File

Update CLAUDE.md whenever:
- A new demo is added or removed
- The Python toolchain or conventions change
- New compose file variants are introduced
- CI patterns change
