"""
CLI Application Entry Point

Background Jobs and Cronjobs using Click
"""
import click
from loguru import logger

from config import Config
from __about__ import __version__
from .dependencies import CLIDependencies
from .jobs import register_all_jobs
from .job_registry import JobRegistry


# Global state for lazy initialization
_deps_initialized = False


def _init_deps() -> None:
    """Lazy dependency initialization"""
    global _deps_initialized
    if not _deps_initialized:
        app_config = Config()
        CLIDependencies.initialize(app_config)
        logger.info("CLI dependencies initialized")
        _deps_initialized = True


def _cleanup_deps() -> None:
    """Cleanup dependencies"""
    global _deps_initialized
    if _deps_initialized:
        CLIDependencies.clear()
        _deps_initialized = False


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


@job_group.command(name="list")
def list_jobs():
    """
    List all available jobs

    Shows all registered job handlers with their names.
    """
    jobs = JobRegistry.list_jobs()

    if not jobs:
        click.echo("No jobs registered.")
        return

    click.echo("Available jobs:")
    for job_name in sorted(jobs):
        # Display as kebab-case (CLI format)
        cmd_name = job_name.replace('_', '-')
        click.echo(f"  - {cmd_name}")


# Register all jobs at module load time
register_all_jobs(job_group, _init_deps, _cleanup_deps)


if __name__ == "__main__":
    cli()
