"""Chat functionality for BunGPT."""

import asyncio
import sys
from typing import List, Optional

from bungpt.core.config import get_config
from bungpt.core.logger import get_logger
from bungpt.models.inference import InferenceEngine
from bungpt.tools.base_tool import get_tool_registry


def main():
    """Main entry point for chat interface."""
    # This is a placeholder for the chat interface
    # The actual implementation is in bungpt.cli.main
    
    print("Please use 'bungpt chat' command to start the chat interface.")
    print("For more information, run: bungpt --help")
    

if __name__ == "__main__":
    main()