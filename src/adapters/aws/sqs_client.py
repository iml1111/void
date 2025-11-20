"""
AWS SQS Client Wrapper

Infrastructure adapter for AWS SQS SDK
"""
import uuid
from typing import Dict, List, Any, Optional
import boto3
from botocore.exceptions import ClientError
from loguru import logger


class SQSClient:
    """
    AWS SQS client wrapper

    Wraps boto3 SQS client with common error handling
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = "ap-northeast-2"
    ):
        """
        Initialize SQS client

        Args:
            aws_access_key_id: AWS IAM access key
            aws_secret_access_key: AWS IAM secret key
            region_name: AWS region (default: ap-northeast-2)
        """
        self._client = boto3.client(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self._region = region_name

    @property
    def client(self):
        """Get boto3 SQS client instance"""
        return self._client

    @property
    def region(self) -> str:
        """Get AWS region"""
        return self._region

    def receive_message(
        self,
        queue_url: str,
        wait_time_seconds: int = 20,
        message_attribute_names: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Receive single message from SQS queue (long polling)

        Args:
            queue_url: SQS queue URL
            wait_time_seconds: Long polling wait time (0-20 seconds)
            message_attribute_names: Message attribute names to retrieve

        Returns:
            Single message dict or None if no messages available

        Note:
            - Always retrieves exactly 1 message (MaxNumberOfMessages=1)
            - Visibility timeout uses queue's default configuration
        """
        try:
            params = {
                'QueueUrl': queue_url,
                'MaxNumberOfMessages': 1,
                'WaitTimeSeconds': wait_time_seconds,
                'AttributeNames': ['All']
            }

            if message_attribute_names:
                params['MessageAttributeNames'] = message_attribute_names

            response = self._client.receive_message(**params)
            messages = response.get('Messages', [])
            return messages[0] if messages else None

        except ClientError as e:
            logger.error(f"Failed to receive message from {queue_url}: {e}")
            raise

    def delete_message(self, queue_url: str, receipt_handle: str) -> None:
        """
        Delete message from SQS queue

        Args:
            queue_url: SQS queue URL
            receipt_handle: Message receipt handle
        """
        try:
            self._client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

        except ClientError as e:
            logger.error(f"Failed to delete message from {queue_url}: {e}")
            raise

    def send_message(
        self,
        queue_url: str,
        message_body: str,
        message_group_id: str,
        message_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message to SQS FIFO queue

        Args:
            queue_url: SQS FIFO queue URL (must end with .fifo)
            message_body: Message body (string)
            message_group_id: Message group ID (required for FIFO)
            message_attributes: Message attributes (optional)

        Note:
            - FIFO queues do not support DelaySeconds
            - MessageDeduplicationId is automatically generated as UUID4
            - Content-Based Deduplication must be disabled on the queue
        """
        try:
            params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body,
                'MessageGroupId': message_group_id,
                'MessageDeduplicationId': str(uuid.uuid4())
            }

            if message_attributes:
                params['MessageAttributes'] = message_attributes

            response = self._client.send_message(**params)
            return response

        except ClientError as e:
            logger.error(f"Failed to send message to {queue_url}: {e}")
            raise

    def get_queue_attributes(self, queue_url: str) -> Dict[str, str]:
        """
        Get queue attributes

        Args:
            queue_url: SQS queue URL
        """
        try:
            response = self._client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )
            return response.get('Attributes', {})

        except ClientError as e:
            logger.error(f"Failed to get queue attributes for {queue_url}: {e}")
            raise
