"""Configuration management for BunGPT."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """Main configuration class for BunGPT."""

    # Model configuration
    model_name: str = Field(default="bungpt-default", description="Name of the model")
    model_path: Optional[Path] = Field(default=None, description="Path to model files")
    device: str = Field(default="auto", description="Device to run model on")
    precision: str = Field(default="float16", description="Model precision")
    max_length: int = Field(default=2048, description="Maximum sequence length")
    
    # API configuration
    api_host: str = Field(default="localhost", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_workers: int = Field(default=1, description="Number of API workers")
    
    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    # Tool configuration
    enable_browser_tool: bool = Field(default=False, description="Enable browser tool")
    enable_python_tool: bool = Field(default=False, description="Enable Python tool")
    enable_code_tool: bool = Field(default=False, description="Enable code execution tool")
    
    # Cache configuration
    cache_dir: Path = Field(default=Path("~/.cache/bungpt").expanduser(), description="Cache directory")
    enable_cache: bool = Field(default=True, description="Enable caching")
    
    # Security configuration
    api_key: Optional[str] = Field(default=None, description="API authentication key")
    allowed_hosts: list[str] = Field(default=["*"], description="Allowed hosts for API")
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "BUNGPT_"
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **data: Any) -> None:
        """Initialize configuration."""
        super().__init__(**data)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> "Config":
        """Load configuration from a file."""
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        # This is a simplified version - in practice you'd want to support
        # YAML, TOML, or JSON configuration files
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    def update(self, **kwargs: Any) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config