# sample-uv-app — LLM Web Search Agent

A CLI agent that answers natural language questions by searching the web using DuckDuckGo and reasoning with Anthropic's Claude via the **ReAct pattern** (Reason → Act → Observe → Reason).

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An [Anthropic API key](https://console.anthropic.com/)

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/atiradonet/sample-uv-app.git
cd sample-uv-app

# 2. Copy and populate the environment file
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your_key_here

# 3. Install dependencies (uv creates the virtualenv automatically)
uv sync
```

---

## Running the Agent

```bash
# Ask a question (uv run handles venv activation automatically)
uv run ask "What is the latest version of Python?"

# With options
uv run ask "Who won the last FIFA World Cup?" --model claude-opus-4-6 --max-iter 5
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--model` / `-m` | `claude-opus-4-6` | Anthropic model to use |
| `--max-iter` | `10` | Maximum ReAct iterations before giving up |

---

## Running Tests

```bash
uv run pytest
```

The test suite covers Pydantic model validation, the `web_search` function (via mocked HTTP with `pytest-httpx`), and CLI behaviour including a full ReAct cycle with mocked Anthropic responses.

---

## UV Workflow Demonstrated

```bash
# Project scaffolding
uv init --no-workspace .

# Production dependencies added one by one (visible in lockfile evolution)
uv add anthropic
uv add typer rich httpx python-dotenv pydantic

# Dev dependencies
uv add --dev pytest pytest-httpx

# Run without manual venv activation
uv run ask "Your question here"

# Run tests
uv run pytest
```

### Project Structure

```
sample-uv-app/
├── main.py              # Agent implementation (ReAct loop + CLI)
├── tests/
│   └── test_agent.py    # pytest test suite
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Pinned lockfile (committed for reproducibility)
├── .env.example         # Environment variable template
└── README.md            # This file
```

### pyproject.toml highlights

```toml
[project]
name = "sample-uv-app"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.84.0",   # LLM client with tool use
    "httpx>=0.28.1",        # HTTP client (bundled via anthropic, also used directly)
    "pydantic>=2.12.5",     # Tool input/output schema validation
    "python-dotenv>=1.2.2", # .env file management
    "rich>=14.3.3",         # Terminal output formatting
    "typer>=0.24.1",        # CLI interface
]

[project.scripts]
ask = "main:app"           # `uv run ask` entrypoint
```

---

## How It Works

1. **CLI** — `typer` parses the user's question and options.
2. **ReAct Loop** — The agent iterates up to `--max-iter` times:
   - Claude reasons about the question and decides whether to search.
   - If a search is needed it calls the `web_search` tool with a query.
   - `httpx` fetches results from DuckDuckGo's instant answer API (no API key required).
   - Results are fed back to Claude as tool output.
   - Claude integrates the findings and either searches again or produces a final answer.
3. **Rich Output** — Each step (reasoning, tool calls, search results, final answer) is displayed in styled panels so you can follow the agent's thought process.

---

## License

MIT
