"""
Job Handlers (Entry Point)

CLI job handlers that delegate to Service Layer.
Similar to Worker task handlers pattern.

Auto-discovery: Just add @job decorator to any function in this package.
No need to modify this file when adding new jobs.
"""
import importlib
from pathlib import Path

from loguru import logger


def discover_and_import_jobs() -> None:
    """
    Auto-discover and import all job modules recursively

    Scans all .py files in this package and subpackages.
    @job decorated functions are registered automatically on import.
    """
    jobs_dir = Path(__file__).parent
    package_name = __name__
    _import_modules_recursive(jobs_dir, package_name)


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
                logger.debug(f"Imported job module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to import {module_name}: {e}")
                raise

        elif item.is_dir():
            # Check if it's a Python package (has __init__.py)
            init_file = item / "__init__.py"
            if init_file.exists():
                _import_modules_recursive(item, f"{package_prefix}.{item.name}")
