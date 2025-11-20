"""
SQS Consumer Worker

Main consumer loop for processing SQS messages
"""
import signal
from loguru import logger

from config import Config
from .task_handler import TaskHandler
from .dependencies import get_sqs_consumer


class SQSConsumer:
    """
    SQS consumer worker

    Polls messages from SQS queue and processes them
    """

    def __init__(self, config: Config):
        """
        Initialize consumer

        Args:
            config: Application configuration

        Note:
            Task handlers must be registered before creating consumer.
            Call register_all_tasks() in worker startup.
        """
        self._config = config
        self._consumer = get_sqs_consumer(config)
        self._handler = TaskHandler()
        self._running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()

    async def start(self) -> None:
        """
        Start consuming messages

        Runs infinite loop polling messages from SQS.
        """
        logger.info("Starting SQS consumer worker")
        logger.info(f"Queue URL: {self._config.sqs_queue_url}")
        logger.info("Processing mode: Single message per poll")
        logger.info(f"Wait time: {self._config.sqs_wait_time_seconds}s")

        self._running = True

        try:
            while self._running:
                await self._poll_and_process()

        except Exception as e:
            logger.exception(f"Fatal error in consumer loop: {e}")
            raise

        finally:
            logger.info("SQS consumer worker stopped")

    async def _poll_and_process(self) -> None:
        """
        Poll and process single message

        Single iteration of consumer loop
        """
        try:
            # Poll and process single message
            await self._consumer.process_message(
                handler=self._handler.handle
            )

        except Exception as e:
            logger.error(f"Error in poll and process: {e}", exc_info=True)
            # Continue loop even if error occurs

    def stop(self) -> None:
        """Stop consuming messages (graceful shutdown)"""
        logger.info("Stopping SQS consumer worker...")
        self._running = False

    def get_queue_stats(self) -> dict:
        """
        Get queue statistics
        """
        try:
            message_count = self._consumer.get_approximate_message_count()
            return {
                "approximate_message_count": message_count,
                "queue_url": self._config.sqs_queue_url
            }
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
