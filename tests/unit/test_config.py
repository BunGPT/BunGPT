"""Tests for configuration management."""

import pytest
from pathlib import Path

from bungpt.core.config import Config


def test_config_initialization():
    """Test basic config initialization."""
    config = Config()
    
    assert config.model_name == "bungpt-default"
    assert config.device == "auto"
    assert config.log_level == "INFO"
    assert config.api_port == 8000


def test_config_with_custom_values():
    """Test config with custom values."""
    config = Config(
        model_name="custom-model",
        device="cuda",
        api_port=9000,
    )
    
    assert config.model_name == "custom-model"
    assert config.device == "cuda"
    assert config.api_port == 9000


def test_config_update():
    """Test config update functionality."""
    config = Config()
    
    config.update(model_name="updated-model", device="cpu")
    
    assert config.model_name == "updated-model"
    assert config.device == "cpu"


def test_config_update_invalid_key():
    """Test config update with invalid key."""
    config = Config()
    
    with pytest.raises(ValueError):
        config.update(invalid_key="value")


def test_config_to_dict():
    """Test config to dictionary conversion."""
    config = Config(model_name="test-model", device="cpu")
    
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict["model_name"] == "test-model"
    assert config_dict["device"] == "cpu"


def test_config_cache_dir_creation(temp_dir: Path):
    """Test that cache directory is created."""
    cache_dir = temp_dir / "test_cache"
    
    config = Config(cache_dir=cache_dir)
    
    assert cache_dir.exists()
    assert cache_dir.is_dir()