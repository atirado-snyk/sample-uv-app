# Codegen Prompt: LLM Web Search Agent

Build a simple LLM web search agent using the UV package manager. The goal is to exercise UV's dependency and project management capabilities as much as the app itself.

---

## Repo

The GitHub repository is at https://github.com/atiradonet/sample-uv-app and has already been cloned to this workstation. All work should be committed and submitted as a pull request against the `main` branch — do not push directly to `main`.

---

## Project Setup

Use `uv init` to scaffold the project, then `uv add` to install dependencies one by one so the lockfile and `pyproject.toml` evolution is visible.

---

## Dependencies

| Package         | Role                                |
| --------------- | ----------------------------------- |
| `anthropic`     | LLM client with tool use            |
| `typer`         | CLI interface                       |
| `rich`          | Terminal output formatting          |
| `httpx`         | HTTP client for search requests     |
| `python-dotenv` | `.env` file management for API keys |
| `pydantic`      | Tool input/output schema validation |

---

## App Behaviour

A CLI command accepts a natural language question. The agent uses Anthropic's tool use API implementing the **ReAct pattern** (Reason → Act → Observe → Reason) to decide when to call a web search tool, retrieves results via DuckDuckGo's free endpoint using `httpx`, incorporates the results into its reasoning, and returns a grounded final answer.

Use `rich` for formatted terminal output that visually distinguishes reasoning steps from the final answer.

---

## UV Specifics to Demonstrate

- `uv init` — project scaffolding
- `uv add` — dependency installation
- `uv run` — execute the app without manual venv activation
- Show the resulting `pyproject.toml` and `uv.lock` structure in comments or the README

---

## Supporting Files

- `.env.example` — template for required environment variables
- `README.md` — UV-specific setup and run instructions

---

## Deliverable

Create a feature branch, commit all work, and open a pull request against `main` on https://github.com/atiradonet/sample-uv-app with a clear PR description summarising the structure and how to run the app.
