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

| Package          | Role                                |
| ---------------- | ----------------------------------- |
| `anthropic`      | LLM client with tool use            |
| `typer`          | CLI interface                       |
| `rich`           | Terminal output formatting          |
| `httpx`          | HTTP client for search requests     |
| `python-dotenv`  | `.env` file management for API keys |
| `pydantic`       | Tool input/output schema validation |
| `pytest`         | Test runner (dev dependency)        |
| `pytest-httpx`   | Mock HTTP calls in tests (dev)      |

---

## App Behaviour

A CLI command accepts a natural language question. The agent uses Anthropic's tool use API implementing the **ReAct pattern** (Reason → Act → Observe → Reason) to decide when to call a web search tool, retrieves results via DuckDuckGo's free endpoint using `httpx`, incorporates the results into its reasoning, and returns a grounded final answer.

Use `rich` for formatted terminal output that visually distinguishes reasoning steps from the final answer.

---

## UV Specifics to Demonstrate

- `uv init` — project scaffolding
- `uv add` — dependency installation (production and dev groups)
- `uv run` — execute the app and tests without manual venv activation
- Show the resulting `pyproject.toml` and `uv.lock` structure in comments or the README

---

## Test Harness

Include a `tests/` directory with a `pytest` suite that covers:

- Pydantic model validation (field defaults and bounds checking)
- `web_search` function with mocked HTTP responses via `pytest-httpx`
- CLI behaviour: missing API key error path, single-turn answer, model flag pass-through, full ReAct cycle (tool call → end turn)

Add `pytest` and `pytest-httpx` as `uv add --dev` dependencies and configure `[tool.pytest.ini_options]` in `pyproject.toml`. Tests should be runnable with `uv run pytest`.

---

## Supporting Files

- `.env.example` — template for required environment variables
- `README.md` — UV-specific setup and run instructions

---

## Deliverable

Create a feature branch, commit all work, and open a pull request against `main` on https://github.com/atiradonet/sample-uv-app with a clear PR description summarising the structure and how to run the app.
