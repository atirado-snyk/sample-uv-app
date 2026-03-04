"""Tests for the LLM web search agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from httpx import Request, Response
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from main import (
    DUCKDUCKGO_URL,
    SearchInput,
    SearchOutput,
    SearchResult,
    app,
    web_search,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Pydantic model tests
# ---------------------------------------------------------------------------


def test_search_input_defaults():
    inp = SearchInput(query="python uv package manager")
    assert inp.query == "python uv package manager"
    assert inp.max_results == 5


def test_search_input_custom_max_results():
    inp = SearchInput(query="test", max_results=3)
    assert inp.max_results == 3


def test_search_input_max_results_bounds():
    with pytest.raises(Exception):
        SearchInput(query="test", max_results=0)
    with pytest.raises(Exception):
        SearchInput(query="test", max_results=11)


def test_search_result_model():
    r = SearchResult(title="UV Docs", url="https://docs.astral.sh/uv/", snippet="Fast Python package manager")
    assert r.title == "UV Docs"
    assert r.url == "https://docs.astral.sh/uv/"


def test_search_output_model():
    results = [SearchResult(title="T", url="http://example.com", snippet="S")]
    out = SearchOutput(results=results, query="test query")
    assert out.query == "test query"
    assert len(out.results) == 1


# ---------------------------------------------------------------------------
# web_search function tests (mocked HTTP)
# ---------------------------------------------------------------------------

DDGO_RESPONSE_WITH_ABSTRACT = {
    "Heading": "Python (programming language)",
    "AbstractText": "Python is a high-level, general-purpose programming language.",
    "AbstractURL": "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "RelatedTopics": [
        {
            "Text": "Python Software Foundation — The organization behind Python.",
            "FirstURL": "https://www.python.org/psf/",
        },
        {
            "Text": "CPython — The reference implementation of Python.",
            "FirstURL": "https://github.com/python/cpython",
        },
    ],
}

DDGO_RESPONSE_EMPTY = {
    "Heading": "",
    "AbstractText": "",
    "AbstractURL": "",
    "RelatedTopics": [],
}


def test_web_search_with_abstract(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=None,
        method="GET",
        json=DDGO_RESPONSE_WITH_ABSTRACT,
    )
    result = web_search("python programming language")
    assert isinstance(result, SearchOutput)
    assert result.query == "python programming language"
    assert len(result.results) >= 1
    # First result should come from the abstract
    assert "Python" in result.results[0].title
    assert "high-level" in result.results[0].snippet


def test_web_search_empty_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=None,
        method="GET",
        json=DDGO_RESPONSE_EMPTY,
    )
    result = web_search("xyzzy totally unknown query")
    assert isinstance(result, SearchOutput)
    assert result.results == []


def test_web_search_respects_max_results(httpx_mock: HTTPXMock):
    many_topics = [
        {"Text": f"Topic {i}", "FirstURL": f"https://example.com/{i}"}
        for i in range(10)
    ]
    httpx_mock.add_response(
        url=None,
        method="GET",
        json={"Heading": "", "AbstractText": "", "AbstractURL": "", "RelatedTopics": many_topics},
    )
    result = web_search("broad query", max_results=3)
    assert len(result.results) <= 3


def test_web_search_nested_topics(httpx_mock: HTTPXMock):
    response = {
        "Heading": "",
        "AbstractText": "",
        "AbstractURL": "",
        "RelatedTopics": [
            {
                "Topics": [
                    {"Text": "Nested topic A", "FirstURL": "https://example.com/a"},
                    {"Text": "Nested topic B", "FirstURL": "https://example.com/b"},
                ]
            }
        ],
    }
    httpx_mock.add_response(url=None, method="GET", json=response)
    result = web_search("nested topics test")
    assert any("Nested topic" in r.title for r in result.results)


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


def _make_end_turn_response(text: str):
    """Build a minimal mock Anthropic response that simulates end_turn."""
    content_block = MagicMock()
    content_block.type = "text"
    content_block.text = text

    response = MagicMock()
    response.content = [content_block]
    response.stop_reason = "end_turn"
    return response


def test_cli_missing_api_key():
    with patch.dict("os.environ", {}, clear=True):
        # Remove ANTHROPIC_API_KEY from env
        import os
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            result = runner.invoke(app, ["What is the capital of France?"])
    assert result.exit_code == 1
    assert "ANTHROPIC_API_KEY" in result.output


def test_cli_single_turn_answer():
    mock_response = _make_end_turn_response("The capital of France is Paris.")

    with patch("main.Anthropic") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = runner.invoke(app, ["What is the capital of France?"])

    assert result.exit_code == 0
    assert "Paris" in result.output


def test_cli_model_option():
    mock_response = _make_end_turn_response("42")

    with patch("main.Anthropic") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = runner.invoke(app, ["What is the answer?", "--model", "claude-haiku-4-5-20251001"])

    assert result.exit_code == 0
    # Verify the model was passed through
    call_kwargs = mock_client.messages.create.call_args
    assert call_kwargs.kwargs["model"] == "claude-haiku-4-5-20251001"


def test_cli_tool_use_then_answer(httpx_mock: HTTPXMock):
    """Simulate a full ReAct cycle: tool call followed by end_turn."""
    # First response: tool use
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "toolu_01"
    tool_block.name = "web_search"
    tool_block.input = {"query": "latest Python version", "max_results": 5}

    first_response = MagicMock()
    first_response.content = [tool_block]
    first_response.stop_reason = "tool_use"

    # Second response: final answer
    second_response = _make_end_turn_response("The latest Python version is 3.13.")

    httpx_mock.add_response(
        url=None,
        method="GET",
        json=DDGO_RESPONSE_WITH_ABSTRACT,
    )

    with patch("main.Anthropic") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.messages.create.side_effect = [first_response, second_response]

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = runner.invoke(app, ["What is the latest Python version?"])

    assert result.exit_code == 0
    assert "3.13" in result.output
    assert mock_client.messages.create.call_count == 2
