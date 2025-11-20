"""
Config Dependency
"""
from fastapi import Request
from config import Config


def get_config(request: Request) -> Config:
    """Get Config from app state"""
    return request.app.state.config
