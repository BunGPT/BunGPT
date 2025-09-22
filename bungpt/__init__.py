"""
BunGPT - A Python project template for GPT-like applications.

This package provides a comprehensive template and framework for building
GPT-like applications with support for inference, tools, and APIs.
"""

__version__ = "0.1.0"
__author__ = "BunGPT Team"
__email__ = "contact@bungpt.dev"
__license__ = "Apache-2.0"

from bungpt.core.config import Config
from bungpt.core.logger import get_logger

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "Config",
    "get_logger",
]