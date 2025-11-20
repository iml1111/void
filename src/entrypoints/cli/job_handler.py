"""
Job Execution Handler

Dispatches job execution to registered handlers.
"""
from loguru import logger

from .job_registry import JobRegistry


class JobHandler:
    """
    Job execution handler using registry-based routing

    Mirrors TaskHandler pattern from Worker entrypoint.
    Dispatches job execution to registered handlers.
    """

    async def execute(self, job_name: str) -> None:
        """
        Execute job by name using registry lookup

        Args:
            job_name: Job identifier (registered function name)
        """
        # Get handler from registry
        handler = JobRegistry.get(job_name)

        if handler is None:
            registered_jobs = JobRegistry.list_jobs()
            raise ValueError(
                f"Unknown job: {job_name}. "
                f"Registered jobs: {', '.join(sorted(registered_jobs))}"
            )

        # Execute handler
        logger.info(f"Executing job: {job_name}")

        try:
            await handler()
            logger.info(f"Job completed successfully: {job_name}")
        except Exception as e:
            logger.error(f"Job execution failed: {job_name}, error: {e}", exc_info=True)
            raise
