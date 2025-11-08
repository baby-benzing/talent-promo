"""Router for research agent using OpenAI Agents SDK."""

import logging
import uuid

from agents import Agent, Runner
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/research", tags=["research"])


class ResearchRequest(BaseModel):
    """Request for research agent."""

    topic: str = Field(
        ...,
        description="The topic or role to research (e.g., job description URL, role title)",
        min_length=1,
        max_length=3000,
    )


class ResearchResult(BaseModel):
    """Structured research output enforced by Agents SDK."""

    role_summary: str = Field(..., description="Summary of the role or topic")
    requirements: list[str] = Field(
        ...,
        description="Key requirements or qualifications",
        min_length=1,
        max_length=15,
    )
    skills: list[str] = Field(
        ...,
        description="Required technical and soft skills",
        min_length=1,
        max_length=15,
    )
    company_context: str | None = Field(None, description="Company information if available")


class ResearchResponse(BaseModel):
    """Response with research results and metadata."""

    request_id: str
    topic: str
    result: ResearchResult
    usage: dict[str, int]


@router.post("/analyze", response_model=ResearchResponse)
async def analyze_role(request: ResearchRequest) -> ResearchResponse:
    """
    Research a role or topic using ResearchAgent.

    Uses OpenAI Agents SDK with structured outputs to analyze:
    - Job descriptions
    - Role requirements
    - Required skills
    - Company context

    Returns structured data ready for resume tailoring.
    """
    request_id = str(uuid.uuid4())
    settings = get_settings()

    logger.info(f"[{request_id}] ResearchAgent starting: {request.topic[:100]}...")

    try:
        # Create ResearchAgent with structured output
        agent = Agent(
            name="ResearchAgent",
            instructions=(
                "You are a research agent specialized in analyzing job descriptions and roles. "
                "Extract key information including role summary, requirements, skills needed, "
                "and company context. Be specific and concise. Focus on actionable details."
            ),
            model=settings.openai_model,
            response_format=ResearchResult,
        )

        # Run agent
        result = await Runner.run(agent, request.topic)

        # Extract structured output
        research_output = result.output

        # Get usage
        usage_info = {
            "prompt_tokens": result.usage.prompt_tokens if result.usage else 0,
            "completion_tokens": result.usage.completion_tokens if result.usage else 0,
            "total_tokens": result.usage.total_tokens if result.usage else 0,
        }

        logger.info(
            f"[{request_id}] ResearchAgent completed - " f"Tokens: {usage_info['total_tokens']}"
        )

        return ResearchResponse(
            request_id=request_id,
            topic=request.topic,
            result=research_output,
            usage=usage_info,
        )

    except Exception as e:
        logger.error(f"[{request_id}] ResearchAgent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Research agent failed: {str(e)}")
