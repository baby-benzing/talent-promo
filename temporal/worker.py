"""Temporal worker for research workflows."""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root and apps/api to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_API = PROJECT_ROOT / "apps" / "api"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APPS_API) not in sys.path:
    sys.path.insert(0, str(APPS_API))

from config import get_settings  # noqa: E402
from temporalio.client import Client  # noqa: E402
from temporalio.contrib.openai_agents import ModelActivityParameters, OpenAIAgentsPlugin  # noqa: E402
from temporalio.worker import Worker  # noqa: E402

from temporal.workflows import ResearchWorkflow  # noqa: E402

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    """Run the Temporal worker for research workflows."""
    from datetime import timedelta
    
    settings = get_settings()

    # Configure model activity parameters for agent execution
    # Pass OpenAI configuration through environment variables that the plugin will use
    import os
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.openai_model:
        os.environ["OPENAI_MODEL"] = settings.openai_model

    model_params = ModelActivityParameters(
        start_to_close_timeout=timedelta(seconds=settings.openai_timeout),
    )

    # Create OpenAI Agents plugin - this handles all the integration
    plugin = OpenAIAgentsPlugin(model_params=model_params)

    # Connect to Temporal server
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
        plugins=[plugin],
    )

    logger.info(
        f"Starting Temporal worker for research workflows on {settings.temporal_address}..."
    )

    # Create and run worker
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[ResearchWorkflow],
        # Activities are automatically registered by the plugin
    )

    logger.info(f"Worker started on task queue: {settings.temporal_task_queue}")
    await worker.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())

