"""Tests for ResearchAgent using Temporal workflows."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to Python path to import temporal module
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import ValidationError  # noqa: E402
from temporal.workflows.research_workflow import (  # type: ignore # noqa: E402
    ResearchResult,
    ResearchWorkflowResult,
)

from main import app  # noqa: E402

# Set test environment variables before importing config
os.environ["OPENAI_API_KEY"] = "sk-test-key-12345"
os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
os.environ["LOG_LEVEL"] = "DEBUG"

client = TestClient(app)


@pytest.fixture
def mock_workflow_result() -> ResearchWorkflowResult:
    """Create a mock workflow result."""
    research_result = ResearchResult(
        role_summary="Senior Software Engineer role focusing on backend systems",
        requirements=["5+ years experience", "Python expertise", "System design skills"],
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        company_context="Tech startup building B2B SaaS platform",
    )

    return ResearchWorkflowResult(
        job_title="Senior Software Engineer",
        job_url="https://example.com/jobs/123",
        result=research_result,
        usage={
            "prompt_tokens": 100,
            "completion_tokens": 150,
            "total_tokens": 250,
        },
    )


def test_research_agent_start_workflow(mock_workflow_result: ResearchWorkflowResult) -> None:
    """Test starting a research workflow."""
    with patch("routers.research_agent.get_temporal_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock workflow start
        mock_client.start_workflow = AsyncMock()

        response = client.post(
            "/api/research-agent/analyze",
            json={
                "job_title": "Senior Software Engineer",
                "job_url": "https://example.com/jobs/123",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "request_id" in data
        assert "workflow_id" in data
        assert "job_title" in data
        assert "job_url" in data
        assert "status" in data

        assert data["status"] == "running"
        assert data["job_title"] == "Senior Software Engineer"
        assert data["job_url"] == "https://example.com/jobs/123"
        assert data["workflow_id"].startswith("research-")


def test_research_agent_get_completed_status(
    mock_workflow_result: ResearchWorkflowResult,
) -> None:
    """Test getting status of a completed workflow."""
    with patch("routers.research_agent.get_temporal_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock workflow handle with describe showing COMPLETED status
        mock_handle = AsyncMock()
        mock_description = MagicMock()
        mock_description.status.name = "COMPLETED"
        mock_handle.describe = AsyncMock(return_value=mock_description)
        mock_handle.result = AsyncMock(return_value=mock_workflow_result)
        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        response = client.get("/api/research-agent/status/research-test-123")

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert data["status"] == "completed"
        assert data["workflow_id"] == "research-test-123"
        assert data["job_title"] == "Senior Software Engineer"
        assert data["job_url"] == "https://example.com/jobs/123"
        assert "result" in data
        assert "usage" in data

        # Check result content (the actual research output)
        assert "Senior Software Engineer" in data["result"]["role_summary"]
        assert len(data["result"]["requirements"]) == 3
        assert len(data["result"]["skills"]) == 5
        assert data["result"]["company_context"] is not None

        # Check usage
        assert data["usage"]["total_tokens"] == 250


def test_research_agent_get_running_status() -> None:
    """Test getting status of a running workflow."""
    with patch("routers.research_agent.get_temporal_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock workflow handle that's still running
        mock_handle = AsyncMock()
        mock_description = MagicMock()
        mock_description.status.name = "RUNNING"
        mock_handle.describe = AsyncMock(return_value=mock_description)

        mock_client.get_workflow_handle = MagicMock(return_value=mock_handle)

        response = client.get("/api/research-agent/status/research-test-123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["workflow_id"] == "research-test-123"


def test_research_agent_workflow_not_found() -> None:
    """Test getting status of a non-existent workflow."""
    with patch("routers.research_agent.get_temporal_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Mock workflow handle that doesn't exist
        mock_client.get_workflow_handle.side_effect = Exception("Workflow not found")

        response = client.get("/api/research-agent/status/nonexistent-id")

        assert response.status_code == 404


def test_research_agent_empty_job_title() -> None:
    """Test validation error for empty job title."""
    response = client.post(
        "/api/research-agent/analyze",
        json={"job_title": ""},
    )

    assert response.status_code == 422  # Validation error


def test_research_agent_missing_job_title() -> None:
    """Test validation error for missing job title."""
    response = client.post(
        "/api/research-agent/analyze",
        json={},
    )

    assert response.status_code == 422  # Validation error


def test_research_agent_without_url() -> None:
    """Test that job URL is optional."""
    with patch("routers.research_agent.get_temporal_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        mock_client.start_workflow = AsyncMock()

        response = client.post(
            "/api/research-agent/analyze",
            json={"job_title": "Data Scientist"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["job_title"] == "Data Scientist"
        assert data["job_url"] is None


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
