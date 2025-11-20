"""
Application Configuration

Pydantic BaseSettings for environment variable management.
"""
import os
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
from __about__ import __version__, __author__, __app_name__


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(BaseSettings):
    """Application Configuration"""

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application metadata
    app_name: str = __app_name__
    version: str = __version__
    description: str = "VOID is a Vibe-Oriented In-Domain Design framework."
    contact_name: str = __author__
    contact_url: str = "https://github.com/iml1111"
    contact_email: str = "shin10256@gmail.com"

    # Environment
    environment: str = Field("development", validation_alias=AliasChoices('ENV', 'env'))

    # Database
    mongodb_uri: str = Field(..., validation_alias=AliasChoices('MONGODB_URI', 'mongodb_uri'))
    mongodb_name: str = Field(..., validation_alias=AliasChoices('MONGODB_NAME', 'mongodb_name'))

    # AWS
    aws_access_key_id: str = Field(..., validation_alias=AliasChoices('AWS_ACCESS_KEY_ID', 'aws_access_key_id'))
    aws_secret_access_key: str = Field(..., validation_alias=AliasChoices('AWS_SECRET_ACCESS_KEY', 'aws_secret_access_key'))
    aws_region: str = Field("ap-northeast-2", validation_alias=AliasChoices('AWS_REGION', 'aws_region'))

    # AWS SQS (Queue Worker)
    sqs_queue_url: str = Field(..., validation_alias=AliasChoices('SQS_QUEUE_URL', 'sqs_queue_url'))
    sqs_wait_time_seconds: int = 20  # Long polling wait time
