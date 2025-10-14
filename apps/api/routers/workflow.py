from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# In-memory workflow state (replace with Temporal in production)
workflow_states: dict[str, dict] = {}


class SubmitEditsRequest(BaseModel):
    run_id: str
    edits: list[dict]


class ResolveSuggestionsRequest(BaseModel):
    run_id: str
    suggestion_ids: list[str]


class ApproveRequest(BaseModel):
    run_id: str


@router.post("/submit_edits")
async def submit_edits(request: SubmitEditsRequest) -> dict:
    """
    Submit user edits and trigger validation workflow.
    Sends signal to Temporal workflow.
    """
    run_id = request.run_id

    if run_id not in workflow_states:
        workflow_states[run_id] = {
            "status": "waiting",
            "edits": [],
            "suggestions_resolved": [],
        }

    # Store edits
    workflow_states[run_id]["edits"].extend(request.edits)
    workflow_states[run_id]["status"] = "validating"

    # In production: send Temporal signal
    # await temporal_client.signal_workflow(
    #     workflow_id=run_id,
    #     signal="submit_edits",
    #     args=[request.edits]
    # )

    return {
        "success": True,
        "run_id": run_id,
        "status": "validating",
        "message": "Edits submitted for validation",
    }


@router.post("/resolve_suggestions")
async def resolve_suggestions(request: ResolveSuggestionsRequest) -> dict:
    """
    Mark suggestions as resolved (accepted or rejected).
    Sends signal to Temporal workflow.
    """
    run_id = request.run_id

    if run_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    # Store resolved suggestions
    workflow_states[run_id]["suggestions_resolved"].extend(request.suggestion_ids)
    workflow_states[run_id]["status"] = "processing"

    # In production: send Temporal signal
    # await temporal_client.signal_workflow(
    #     workflow_id=run_id,
    #     signal="resolve_suggestions",
    #     args=[request.suggestion_ids]
    # )

    return {
        "success": True,
        "run_id": run_id,
        "resolved_count": len(request.suggestion_ids),
        "message": "Suggestions resolved",
    }


@router.post("/approve")
async def approve(request: ApproveRequest) -> dict:
    """
    Approve final version and trigger export.
    Sends signal to Temporal workflow.
    """
    run_id = request.run_id

    if run_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    # Update status
    workflow_states[run_id]["status"] = "approved"

    # In production: send Temporal signal
    # await temporal_client.signal_workflow(
    #     workflow_id=run_id,
    #     signal="approve",
    #     args=[]
    # )

    return {
        "success": True,
        "run_id": run_id,
        "status": "approved",
        "message": "Document approved and exported",
    }


@router.get("/status/{run_id}")
async def get_workflow_status(run_id: str) -> dict:
    """Get current workflow status via Temporal Query."""
    if run_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    state = workflow_states[run_id]

    # In production: query Temporal workflow
    # status = await temporal_client.query_workflow(
    #     workflow_id=run_id,
    #     query="get_status"
    # )

    return {
        "run_id": run_id,
        "status": state["status"],
        "edits_count": len(state.get("edits", [])),
        "suggestions_resolved": len(state.get("suggestions_resolved", [])),
    }
