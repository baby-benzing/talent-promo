"""Research workflow using OpenAI Agents SDK with Temporal."""
import logging

from agents import Agent, Runner
from pydantic import BaseModel, Field
from temporalio import workflow

logger = logging.getLogger(__name__)


class ResearchRequest(BaseModel):
    """Input for research workflow."""

    job_title: str = Field(..., description="The job title or role name")
    job_url: str | None = Field(None, description="URL to the job posting (optional)")


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


class ResearchWorkflowResult(BaseModel):
    """Complete workflow result with metadata."""

    job_title: str
    job_url: str | None
    result: ResearchResult
    usage: dict[str, int]


@workflow.defn
class ResearchWorkflow:
    """
    Temporal workflow for researching roles using OpenAI Agents SDK.

    The workflow orchestrates the research agent execution with proper
    error handling, timeouts, and observability through Temporal.
    """

    @workflow.run
    async def run(self, request: ResearchRequest) -> ResearchWorkflowResult:
        """
        Execute research agent workflow.

        This method runs the OpenAI agent within the Temporal workflow context.
        The OpenAIAgentsPlugin automatically converts agent LLM calls into
        Temporal activities, providing:
        - Automatic retries on failures
        - Timeout handling
        - Progress tracking and observability
        - Distributed execution across workers
        """
        workflow.logger.info(f"Starting research workflow for: {request.job_title}")

        # Build the research input
        research_input = f"Job Title: {request.job_title}"
        if request.job_url:
            research_input += f"\nJob URL: {request.job_url}"
            research_input += (
                "\n\nPlease analyze this job posting and extract the key information."
            )
        else:
            research_input += (
                "\n\nPlease research this role and provide typical requirements and skills."
            )

        # Create ResearchAgent with structured output
        # The model will be configured via the OpenAIAgentsPlugin
        # TODO: provide MCP tools for the agent to get the job description and company information
        # TODO: provide a tool to search the web for information when mcp tools are not enough
        # TODO: update prompt to look into company context and role requirements
        agent = Agent(
            name="ResearchAgent",
            instructions=(
                "You are a research agent specialized in analyzing job descriptions and roles. "
                "Extract key information including role summary, requirements, skills needed, "
                "and company context. Be specific and concise. Focus on actionable details. "
                "If a job URL is provided, focus on that specific posting. "
                "If only a job title is provided, research typical requirements for that role."
            ),
            output_type=ResearchResult,
        )

        # Run agent - this is automatically converted to Temporal activities
        # by the OpenAIAgentsPlugin, so it's durable and can be retried
        result = await Runner.run(agent, research_input)

        # Extract structured output
        research_output = result.final_output_as(ResearchResult)

        # Extract usage from raw responses
        total_input_tokens = 0
        total_output_tokens = 0
        for response in result.raw_responses:
            if response.usage:
                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

        usage_info = {
            "prompt_tokens": total_input_tokens,
            "completion_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
        }

        workflow.logger.info(f"Research workflow completed - Tokens: {usage_info['total_tokens']}")

        return ResearchWorkflowResult(
            job_title=request.job_title,
            job_url=request.job_url,
            result=research_output,
            usage=usage_info,
        )

