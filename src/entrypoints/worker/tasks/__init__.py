"""
Task Handlers (Entry Point)

Worker task handlers that delegate to Service Layer.
Similar to FastAPI route handlers that call services.

Auto-discovery: Just add @task decorator to any function in this package.
No need to modify this file when adding new tasks.
"""
import importlib
from pathlib import Path

from loguru import logger


def discover_and_import_tasks() -> None:
    """
    Auto-discover and import all task modules recursively

    Scans all .py files in this package and subpackages.
    @task decorated functions are registered automatically on import.
    """
    tasks_dir = Path(__file__).parent
    package_name = __name__
    _import_modules_recursive(tasks_dir, package_name)


def _import_modules_recursive(directory: Path, package_prefix: str) -> None:
    """
    Recursively import all Python modules in directory

    Args:
        directory: Directory to scan
        package_prefix: Python package prefix for imports
    """
    for item in sorted(directory.iterdir()):
        # Skip __pycache__, hidden files, and dunder modules
        if item.name.startswith(('__', '.')):
            continue

        if item.is_file() and item.suffix == '.py':
            module_name = f"{package_prefix}.{item.stem}"
            try:
                importlib.import_module(module_name)
                logger.debug(f"Imported task module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to import {module_name}: {e}")
                raise

        elif item.is_dir():
            # Check if it's a Python package (has __init__.py)
            init_file = item / "__init__.py"
            if init_file.exists():
                _import_modules_recursive(item, f"{package_prefix}.{item.name}")
