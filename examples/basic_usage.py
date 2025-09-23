#!/usr/bin/env python3
"""
Basic usage example for BunGPT.

This example demonstrates how to use the BunGPT library for text generation.
"""

import asyncio
from pathlib import Path

from bungpt.core.config import Config
from bungpt.models.inference import InferenceEngine
from bungpt.tools.python_tool import PythonTool
from bungpt.tools.base_tool import get_tool_registry


async def main():
    """Main example function."""
    # Configure BunGPT
    config = Config(
        model_name="example-model",
        device="cpu",  # Use CPU for this example
        log_level="INFO",
    )
    
    # For this example, we'll simulate having a model
    # In practice, you would set config.model_path to your actual model
    print("BunGPT Basic Usage Example")
    print("=" * 40)
    
    # Example 1: Using tools
    print("\n1. Tool Usage Example")
    print("-" * 25)
    
    # Register Python tool
    registry = get_tool_registry()
    python_tool = PythonTool()
    registry.register(python_tool)
    
    # Execute Python code
    result = await python_tool.execute(code="""
# Calculate factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is: {result}")
""")
    
    print("Python tool result:")
    print(result.result if result.success else result.error)
    
    # Example 2: Text processing
    print("\n2. Text Processing Example")
    print("-" * 28)
    
    from bungpt.utils.text import format_text, extract_sentences, count_words
    
    sample_text = """
    This is a sample text that demonstrates the text processing capabilities
    of BunGPT. The text contains multiple sentences and can be processed
    in various ways to extract information or reformat it for different purposes.
    """
    
    # Format text
    formatted = format_text(sample_text.strip(), max_line_length=50)
    print("Formatted text:")
    print(formatted)
    
    # Extract sentences
    sentences = extract_sentences(sample_text)
    print(f"\nExtracted {len(sentences)} sentences:")
    for i, sentence in enumerate(sentences, 1):
        print(f"{i}. {sentence.strip()}")
    
    # Count words
    word_count = count_words(sample_text)
    print(f"\nWord count: {word_count}")
    
    # Example 3: Configuration
    print("\n3. Configuration Example")
    print("-" * 26)
    
    print("Current configuration:")
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    # Example 4: File operations
    print("\n4. File Operations Example")
    print("-" * 28)
    
    from bungpt.utils.files import safe_write_file, safe_read_file
    
    # Create a temporary file
    temp_file = Path("example_output.txt")
    
    # Write content
    content = "This is an example file created by BunGPT.\nIt demonstrates file operations."
    success = safe_write_file(temp_file, content)
    
    if success:
        print(f"Successfully wrote to {temp_file}")
        
        # Read content back
        read_content = safe_read_file(temp_file)
        if read_content:
            print("File content:")
            print(read_content)
        
        # Clean up
        temp_file.unlink()
        print("Temporary file cleaned up")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())