"""
Worker Application Entry Point

SQS Consumer Worker for async task processing
"""
import asyncio
from loguru import logger

from config import Config
from .tasks import register_all_tasks
from .task_registry import TaskRegistry
from .dependencies import WorkerDependencies
from .consumer import SQSConsumer


async def main():
    """Main entry point for worker"""
    logger.info("Initializing VOID SQS Worker")

    # Load configuration
    config = Config()

    # Initialize worker dependencies (Config, MongoDB client)
    WorkerDependencies.initialize(config)
    logger.info("Worker dependencies initialized")

    # Initialize and register all task handlers
    register_all_tasks()
    logger.info(f"Registered task handlers: {TaskRegistry.list_tasks()}")

    # Create and start consumer
    consumer = SQSConsumer(config)

    # Log startup info
    logger.info(f"Environment: {config.environment}")
    logger.info(f"SQS Queue: {config.sqs_queue_url}")
    logger.info(f"AWS Region: {config.aws_region}")

    # Start consuming
    await consumer.start()


if __name__ == "__main__":
    asyncio.run(main())
