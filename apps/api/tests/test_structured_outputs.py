"""Tests for ResearchAgent using Agents SDK."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from main import app
from routers.research_agent import ResearchResult

# Set test environment variables before importing config
os.environ["OPENAI_API_KEY"] = "sk-test-key-12345"
os.environ["OPENAI_MODEL"] = "gpt-5-mini"
os.environ["LOG_LEVEL"] = "DEBUG"

client = TestClient(app)


@pytest.fixture
def mock_research_result() -> MagicMock:
    """Create a mock ResearchAgent result."""
    result = MagicMock()
    # Mock the final_output_as method to return the ResearchResult
    output_data = ResearchResult(
        role_summary="Senior Software Engineer role focusing on backend systems",
        requirements=["5+ years experience", "Python expertise", "System design skills"],
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        company_context="Tech startup building B2B SaaS platform",
    )
    result.final_output_as.return_value = output_data

    # Mock raw_responses with usage information
    mock_response = MagicMock()
    mock_usage = MagicMock()
    mock_usage.input_tokens = 100
    mock_usage.output_tokens = 150
    mock_response.usage = mock_usage
    result.raw_responses = [mock_response]

    return result


def test_research_agent_success(mock_research_result: MagicMock) -> None:
    """Test successful ResearchAgent analysis."""
    with patch("routers.research_agent.Runner") as mock_runner:
        # Mock async run method
        mock_runner.run = AsyncMock(return_value=mock_research_result)

        response = client.post(
            "/api/research/analyze",
            json={"topic": "Senior Software Engineer at TechCorp"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "request_id" in data
        assert "topic" in data
        assert "result" in data
        assert "usage" in data

        # Check result content
        assert "Senior Software Engineer" in data["result"]["role_summary"]
        assert len(data["result"]["requirements"]) == 3
        assert len(data["result"]["skills"]) == 5
        assert data["result"]["company_context"] is not None

        # Check usage
        assert data["usage"]["total_tokens"] == 250

        # Verify Runner was called
        mock_runner.run.assert_called_once()


def test_research_agent_failure() -> None:
    """Test that endpoint fails when agent run fails."""
    with patch("routers.research_agent.Runner") as mock_runner:
        # Mock async run method with exception
        mock_runner.run = AsyncMock(side_effect=Exception("Agent error"))

        response = client.post(
            "/api/research/analyze",
            json={"topic": "Test role"},
        )

        assert response.status_code == 500
        data = response.json()
        assert "Research agent failed" in data["detail"]


def test_research_agent_empty_topic() -> None:
    """Test validation error for empty topic."""
    response = client.post(
        "/api/research/analyze",
        json={"topic": ""},
    )

    assert response.status_code == 422  # Validation error


def test_research_agent_missing_topic() -> None:
    """Test validation error for missing topic."""
    response = client.post(
        "/api/research/analyze",
        json={},
    )

    assert response.status_code == 422  # Validation error


def test_research_result_schema_validation() -> None:
    """Test that ResearchResult schema is validated correctly."""
    # Valid result
    valid = ResearchResult(
        role_summary="Test role",
        requirements=["Req 1"],
        skills=["Skill 1"],
        company_context=None,
    )
    assert valid.role_summary == "Test role"

    # Invalid: empty requirements
    with pytest.raises(ValidationError):
        ResearchResult(
            role_summary="Test",
            requirements=[],
            skills=["Skill 1"],
            company_context=None,
        )

    # Invalid: too many requirements
    with pytest.raises(ValidationError):
        ResearchResult(
            role_summary="Test",
            requirements=["Req"] * 16,  # Max is 15
            skills=["Skill 1"],
            company_context=None,
        )


def test_research_agent_logging(
    mock_research_result: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that proper logging occurs."""
    import logging

    with caplog.at_level(logging.INFO):
        with patch("routers.research_agent.Runner") as mock_runner:
            # Mock async run method
            mock_runner.run = AsyncMock(return_value=mock_research_result)

            response = client.post(
                "/api/research/analyze",
                json={"topic": "Test role"},
            )

            assert response.status_code == 200
            data = response.json()
            request_id = data["request_id"]

            log_messages = [record.message for record in caplog.records]

            # Request ID should appear in logs
            request_id_logs = [msg for msg in log_messages if request_id in msg]
            assert len(request_id_logs) > 0

            # ResearchAgent mentions should be in logs
            agent_logs = [msg for msg in log_messages if "ResearchAgent" in msg]
            assert len(agent_logs) > 0
