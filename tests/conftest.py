"""Pytest configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from bungpt.core.config import Config
from bungpt.tools.base_tool import ToolRegistry


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config(temp_dir: Path) -> Config:
    """Create a test configuration."""
    return Config(
        model_name="test-model",
        model_path=temp_dir / "model",
        device="cpu",
        cache_dir=temp_dir / "cache",
        log_level="DEBUG",
        api_port=8888,
    )


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Create a fresh tool registry for tests."""
    return ToolRegistry()


@pytest.fixture
def sample_text() -> str:
    """Sample text for testing."""
    return """
    This is a sample text for testing purposes. It contains multiple sentences
    and paragraphs to test various text processing functions.
    
    The text includes some formatting and different types of content that
    can be used to validate the behavior of text processing utilities.
    """


@pytest.fixture
def sample_json_data() -> dict:
    """Sample JSON data for testing."""
    return {
        "name": "test",
        "version": "1.0.0",
        "description": "A test configuration",
        "settings": {
            "enabled": True,
            "max_items": 100,
            "allowed_types": ["text", "image", "video"],
        },
        "metadata": {
            "created": "2024-01-01T00:00:00Z",
            "updated": "2024-01-01T12:00:00Z",
        },
    }


@pytest.fixture
def sample_messages() -> list:
    """Sample messages for testing chat functionality."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        {"role": "user", "content": "Can you help me with a Python question?"},
    ]