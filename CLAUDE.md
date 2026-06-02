# CLAUDE.md — Compose for Agents Codebase Guide

This file provides context for AI assistants working in this repository.

---

## Project Overview

**Compose for Agents** is a collection of self-contained Docker Compose demos showing how to run popular AI agent frameworks locally (or in the cloud) using Docker. Each demo is independent and lives in its own subdirectory with its own `compose.yaml`.

The project is dual-licensed under Apache 2.0 or MIT.

---

## Repository Layout

```
/
├── CLAUDE.md                  # This file
├── README.md                  # Demo index and prerequisites
├── Taskfile.yaml              # Task runner: lint targets (markdownlint, yamllint)
├── Dockerfile.tools           # Multi-stage image: markdownlint + yamllint
├── .markdownlint.yaml         # Markdownlint rule configuration
├── .markdownlint-cli2.yaml    # Markdownlint CLI2 configuration
├── .yamllint                  # YAML lint configuration
├── .gitignore
├── .gitattributes
├── LICENSE.APACHE-2
├── LICENSE.MIT
├── a2a/                       # A2A Multi-Agent Fact Checker (OpenAI + DuckDuckGo)
├── adk/                       # Google ADK Multi-Agent Fact Checker (gemma3-qat local)
├── adk-cerebras/              # ADK + Cerebras Golang Experts (local + Cerebras remote)
├── adk-sock-shop/             # ADK Sock Store Agent (MongoDB, Brave, Curl)
├── agno/                      # Agno GitHub Issue Summarizer (qwen3 local)
├── akka/                      # Akka demo
├── crew-ai/                   # CrewAI Marketing Strategy Agent (qwen3 local)
├── embabel/                   # Embabel Travel Agent (multi-model, many MCPs)
├── langchaingo/               # LangchainGo DuckDuckGo Search (gemma3 local)
├── langgraph/                 # LangGraph SQL Agent (qwen3 local + postgres MCP)
├── minions/                   # MinionS local-remote collaboration protocol
├── spring-ai/                 # Spring AI Brave Search (DuckDuckGo)
└── vercel/                    # Vercel AI SDK Chat UI (llama3.2/qwen3 local)
```

### Per-Demo Structure

Each demo directory follows this pattern:

```
<demo>/
├── compose.yaml               # Primary Compose file (always present)
├── compose.openai.yaml        # OpenAI model override (optional)
├── compose.offload.yaml       # Docker Offload override (optional)
├── compose.gcloudrun.yaml     # Cloud Run deploy override (optional)
├── mcp.env.example            # Template for secrets — copy to .mcp.env
├── Dockerfile                 # Agent container image (when custom build needed)
├── README.md                  # Demo-specific setup and run instructions
└── <source files>             # Agent implementation (Python, Go, Java, etc.)
```

---

## Prerequisites

- **Docker Desktop 4.43.0+** or Docker Engine with **Docker Compose 2.38.1+**
- A laptop/workstation with a GPU for running open models locally (optional — use [Docker Offload](https://www.docker.com/products/docker-offload/) otherwise)
- On Linux/Windows: GPU support enabled and drivers installed per [Docker Model Runner requirements](https://docs.docker.com/ai/model-runner/)

---

## Running a Demo

```bash
# 1. Change to the demo directory
cd adk

# 2. Copy secrets template if present and fill in tokens
cp mcp.env.example .mcp.env
# edit .mcp.env

# 3. Start with local models (Docker Model Runner)
docker compose up --build

# OR: Start with OpenAI instead
docker compose -f compose.yaml -f compose.openai.yaml up
```

---

## Linting

Lint tooling runs inside Docker containers — no local install needed beyond [Task](https://taskfile.dev/).

```bash
task lint              # Run both markdownlint and yamllint
task lint:markdown     # Lint Markdown files only
task lint:yaml         # Lint YAML files only
task lint:markdown:fix # Auto-fix Markdown issues
```

The lint images are built from `Dockerfile.tools` on first run:
- `markdownlint` stage: uses `markdownlint-cli2`
- `yamllint` stage: uses `yamllint`

Always run `task lint` before opening a PR.

---

## Key Conventions

- **Self-contained demos:** each subdirectory must be runnable standalone with `docker compose up --build`. No source code is shared between demos.
- **Secrets via `.mcp.env`:** never commit tokens or API keys. Demos that need secrets ship an `mcp.env.example`; `.mcp.env` is gitignored.
- **OpenAI override pattern:** `compose.yaml` uses Docker Model Runner (local models); `compose.openai.yaml` overrides to use `secret.openai-api-key`.
- **Markdown style:** follow `.markdownlint.yaml` rules. Run `task lint:markdown:fix` to auto-fix before committing.
- **YAML style:** follow `.yamllint` rules. Run `task lint:yaml` to check.
- **Dual license:** contributions go under Apache 2.0 OR MIT. Per-demo `LICENSE` files reflect third-party requirements for that specific demo.

---

## Adding a New Demo

1. Create `<demo-name>/` at the repo root.
2. Add `<demo-name>/compose.yaml` as the primary Compose file.
3. Add `<demo-name>/README.md` with setup and run instructions.
4. If secrets are needed, add `<demo-name>/mcp.env.example` (never the real `.mcp.env`).
5. Add an entry to the demo table in the root `README.md`.
6. Run `task lint` and fix any warnings.

---

## AI Assistant Conventions

### Do

- **Read before editing:** always read a file before modifying it
- **Minimal changes:** only what the task requires
- **Confirm before destructive actions:** ask before force-push or branch deletion
- **Develop on `claude/claude-md-docs-JOqAm`:** never push directly to `main`
- **Run `task lint`** before finalizing any Markdown or YAML changes

### Do Not

- Commit `.mcp.env` or any file containing real API tokens
- Share source code across demo directories — each must be self-contained
- Add emoji in commit messages or docs unless asked

### GitHub

- Use `mcp__github__*` tools for all GitHub interactions
- Scope is limited to `hanyy07/compose-for-agents`
- Always create a draft PR after pushing a new branch

---

## Key Files

| File | Purpose |
|---|---|
| `README.md` | Demo index and prerequisites |
| `Taskfile.yaml` | Lint task definitions |
| `Dockerfile.tools` | Lint tool container images |
| `.markdownlint.yaml` | Markdown lint rules |
| `.yamllint` | YAML lint rules |
| `CLAUDE.md` | This file |
