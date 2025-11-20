"""
CLI Application Entry Point

Background Jobs and Cronjobs using Click
"""
import asyncio
import click
from loguru import logger

from config import Config
from __about__ import __version__
from .dependencies import CLIDependencies
from .jobs import register_all_jobs
from .job_registry import JobRegistry
from .job_handler import JobHandler


@click.group(name="void")
@click.version_option(version=__version__)
def cli():
    """
    VOID CLI - Background Jobs and Cronjobs

    Command-line interface for executing background jobs, cronjobs,
    and standalone features.
    """
    pass


@cli.group(name="job")
def job_group():
    """Execute background jobs and cronjobs"""
    pass


@job_group.command(name="run")
@click.argument("job_name")
def run_job(job_name: str):
    """
    Run a specific job by name

    JOB_NAME is the name of the registered job (function name).

    Example:
        void job run cleanup_items
    """
    asyncio.run(_execute_job(job_name))


async def _execute_job(job_name: str):
    """
    Execute job with async support

    Args:
        job_name: Job identifier
    """
    logger.info(f"Initializing VOID CLI: job={job_name}")

    # Load configuration from .env
    app_config = Config()

    # Initialize dependencies
    CLIDependencies.initialize(app_config)
    logger.info("CLI dependencies initialized")

    # Register all jobs
    register_all_jobs()
    logger.info(f"Registered jobs: {JobRegistry.list_jobs()}")

    # Execute job
    handler = JobHandler()
    try:
        await handler.execute(job_name)
        logger.info(f"Job completed: {job_name}")
    except Exception as e:
        logger.error(f"Job failed: {job_name}, error: {e}", exc_info=True)
        raise click.ClickException(str(e))
    finally:
        # Cleanup
        CLIDependencies.clear()


@job_group.command(name="list")
def list_jobs():
    """
    List all available jobs

    Shows all registered job handlers with their names.
    """
    # Initialize config (minimal, no external connections needed)
    try:
        config = Config()
        CLIDependencies.initialize(config)
    except Exception as e:
        logger.warning(f"Could not initialize config: {e}")

    # Register all jobs
    register_all_jobs()

    # List jobs
    jobs = JobRegistry.list_jobs()

    if not jobs:
        click.echo("No jobs registered.")
        return

    click.echo("Available jobs:")
    for job in sorted(jobs):
        click.echo(f"  - {job}")


if __name__ == "__main__":
    cli()
