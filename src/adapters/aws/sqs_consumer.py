"""
SQS Consumer Adapter

Handles message polling and processing from SQS queue
"""
import json
from typing import Dict, Any, Callable, Optional
from loguru import logger
from .sqs_client import SQSClient


class SQSConsumerAdapter:
    """
    SQS message consumer adapter

    Provides high-level interface for consuming messages from SQS queue
    """

    def __init__(
        self,
        sqs_client: SQSClient,
        queue_url: str,
        wait_time_seconds: int = 20
    ):
        """
        Initialize SQS consumer

        Args:
            sqs_client: SQS client instance
            queue_url: SQS queue URL
            wait_time_seconds: Long polling wait time (0-20)
        """
        self._client = sqs_client
        self._queue_url = queue_url
        self._wait_time_seconds = wait_time_seconds

    def poll(self) -> Optional[Dict[str, Any]]:
        """
        Poll single message from SQS queue

        Uses long polling for efficient message retrieval

        Returns:
            Parsed message dict or None if no messages available
        """
        try:
            raw_message = self._client.receive_message(
                queue_url=self._queue_url,
                wait_time_seconds=self._wait_time_seconds
            )

            if not raw_message:
                return None

            # Parse single message
            try:
                parsed_message = self._parse_message(raw_message)
                logger.info(
                    f"Polled message {parsed_message['message_id']} from SQS",
                    extra={"message_id": parsed_message['message_id']}
                )
                return parsed_message
            except Exception as e:
                logger.error(
                    f"Failed to parse message {raw_message.get('MessageId')}: {e}",
                    extra={"raw_message": raw_message}
                )
                return None

        except Exception as e:
            logger.error(f"Failed to poll message from {self._queue_url}: {e}")
            raise

    def _parse_message(self, raw_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw SQS message

        Args:
            raw_message: Raw message from SQS
        """
        body = raw_message.get('Body', '{}')

        # Parse JSON body
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError:
            # If not JSON, keep as string
            parsed_body = body

        return {
            'body': parsed_body,
            'receipt_handle': raw_message.get('ReceiptHandle'),
            'message_id': raw_message.get('MessageId'),
            'attributes': raw_message.get('Attributes', {}),
            'message_attributes': raw_message.get('MessageAttributes', {})
        }

    def delete_message(self, receipt_handle: str) -> None:
        """
        Delete processed message

        Args:
            receipt_handle: Message receipt handle
        """
        try:
            self._client.delete_message(
                queue_url=self._queue_url,
                receipt_handle=receipt_handle
            )
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise

    async def process_message(
        self,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Poll and process single message with handler function

        Args:
            handler: Message handler function (receives parsed message)

        Note:
            Messages are always deleted after processing (success or failure)
            to prevent infinite retry loops.
        """
        message = self.poll()

        if not message:
            # No message available
            return

        try:
            # Process message
            await handler(message)

            logger.info(
                f"Processed message {message['message_id']}",
                extra={"message_id": message['message_id']}
            )

        except Exception as e:
            logger.error(
                f"Failed to process message {message['message_id']}: {e}",
                extra={
                    "message_id": message['message_id'],
                    "error": str(e)
                }
            )
            # Error notification is already sent by TaskHandler

        finally:
            # Always delete message to prevent infinite retry loop
            self.delete_message(message['receipt_handle'])

    def get_approximate_message_count(self) -> int:
        """
        Get approximate number of messages in queue
        """
        try:
            attributes = self._client.get_queue_attributes(self._queue_url)
            count = int(attributes.get('ApproximateNumberOfMessages', 0))
            return count

        except Exception as e:
            logger.error(f"Failed to get message count: {e}")
            raise
