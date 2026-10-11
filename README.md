# Microsoft Agent Framework Playground

A small playground for [Microsoft Agent Framework](https://github.com/microsoft/agent-framework).

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- A GitHub personal access token with access to GitHub Models

## Setup

```bash
uv sync
uv run pre-commit install
```

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=<your-token>
```

## Run

```bash
uv run python main.py
```

In VS Code, press `F5` to run with the debugger.

## Checks

Every commit runs Ruff (lint and format) and Pyright (type check) automatically.
To run them manually:

```bash
uv run pre-commit run --all-files
```
