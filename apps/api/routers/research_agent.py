"""Router for research agent using Temporal workflows."""

import logging
import sys
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from temporalio.client import Client
from temporalio.contrib.openai_agents import OpenAIAgentsPlugin

# Add project root to Python path to import temporal module
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from temporal.workflows.research_workflow import (  # type: ignore # noqa: E402
    ResearchRequest as WorkflowResearchRequest,
)
from temporal.workflows.research_workflow import (  # type: ignore # noqa: E402
    ResearchResult,
    ResearchWorkflow,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/research-agent", tags=["research-agent"])

# Global Temporal client (initialized on startup)
_temporal_client: Client | None = None


async def get_temporal_client() -> Client:
    """Get or create Temporal client with OpenAI Agents plugin."""
    global _temporal_client
    if _temporal_client is None:
        import os

        from config import get_settings

        # Ensure OpenAI API key is available in environment for the plugin
        settings = get_settings()
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.openai_model:
            os.environ["OPENAI_MODEL"] = settings.openai_model

        plugin = OpenAIAgentsPlugin()
        _temporal_client = await Client.connect(
            settings.temporal_address,
            namespace=settings.temporal_namespace,
            plugins=[plugin],
        )
    return _temporal_client


class ResearchRequest(BaseModel):
    """Request for research agent."""

    job_title: str = Field(
        ...,
        description="The job title or role name to research",
        min_length=1,
        max_length=50,
    )
    job_url: str | None = Field(
        None,
        description="URL to the job posting (optional)",
        max_length=1000,
    )


class ResearchResponse(BaseModel):
    """Response with workflow ID for tracking."""

    request_id: str
    workflow_id: str
    job_title: str
    job_url: str | None
    status: str


class ResearchStatusResponse(BaseModel):
    """Response with workflow status and results if complete."""

    request_id: str
    workflow_id: str
    job_title: str
    job_url: str | None = None
    status: str
    result: ResearchResult | None = None
    usage: dict[str, int] | None = None
    error: str | None = None


@router.post("/analyze", response_model=ResearchResponse)
async def analyze_role(request: ResearchRequest) -> ResearchResponse:
    """
    Start research workflow using Temporal.

    This endpoint starts a durable Temporal workflow that:
    - Executes the OpenAI agent in a fault-tolerant manner
    - Provides automatic retries on failures
    - Enables progress tracking via Temporal UI
    - Returns immediately with a workflow ID for tracking

    The actual agent execution happens asynchronously in Temporal workers.
    Use the /status/{workflow_id} endpoint to check progress and results.
    """
    request_id = str(uuid.uuid4())
    workflow_id = f"research-{request_id}"

    logger.info(
        f"[{request_id}] Starting research workflow: {request.job_title}"
        + (f" ({request.job_url})" if request.job_url else "")
    )

    try:
        # Get Temporal client
        client = await get_temporal_client()

        # Start workflow (non-blocking)
        workflow_request = WorkflowResearchRequest(
            job_title=request.job_title, job_url=request.job_url
        )
        await client.start_workflow(
            ResearchWorkflow.run,
            workflow_request,
            id=workflow_id,
            task_queue="research-task-queue",
        )

        logger.info(f"[{request_id}] Workflow started: {workflow_id}")

        return ResearchResponse(
            request_id=request_id,
            workflow_id=workflow_id,
            job_title=request.job_title,
            job_url=request.job_url,
            status="running",
        )

    except Exception as e:
        logger.error(f"[{request_id}] Failed to start workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start research workflow: {str(e)}")


@router.get("/status/{workflow_id}", response_model=ResearchStatusResponse)
async def get_workflow_status(workflow_id: str) -> ResearchStatusResponse:
    """
    Get the status and results of a research workflow.

    Returns:
    - status: "running", "completed", or "failed"
    - result: Research results if completed
    - usage: Token usage if completed
    - error: Error message if failed
    """
    # Extract request_id from workflow_id
    request_id = workflow_id.replace("research-", "")

    try:
        # Get Temporal client
        client = await get_temporal_client()

        # Get workflow handle
        handle = client.get_workflow_handle(workflow_id)

        # Check workflow status without blocking
        description = await handle.describe()
        status_name = description.status.name if description.status else "UNKNOWN"

        if status_name == "COMPLETED":
            # Workflow completed - fetch the result
            try:
                result = await handle.result()
                logger.info(f"[{request_id}] Workflow completed successfully")

                return ResearchStatusResponse(
                    request_id=request_id,
                    workflow_id=workflow_id,
                    job_title=result.job_title,
                    job_url=result.job_url,
                    status="completed",
                    result=result.result,
                    usage=result.usage,
                )
            except Exception as e:
                # Result fetch failed, but workflow says completed
                logger.error(f"[{request_id}] Failed to fetch completed workflow result: {str(e)}")
                return ResearchStatusResponse(
                    request_id=request_id,
                    workflow_id=workflow_id,
                    job_title="[Completed]",
                    job_url=None,
                    status="completed",
                    error=f"Failed to retrieve result: {str(e)}",
                )

        elif status_name == "RUNNING":
            # Workflow is still running - return immediately
            return ResearchStatusResponse(
                request_id=request_id,
                workflow_id=workflow_id,
                job_title="[In Progress]",
                job_url=None,
                status="running",
            )

        else:
            # Workflow failed or in another state
            return ResearchStatusResponse(
                request_id=request_id,
                workflow_id=workflow_id,
                job_title="[Failed]",
                job_url=None,
                status="failed",
                error=f"Workflow status: {status_name}",
            )

    except Exception as e:
        logger.error(f"[{request_id}] Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Workflow not found or error: {str(e)}")
