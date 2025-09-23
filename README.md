# BunGPT

<p align="center">
  <strong>A comprehensive Python project template for GPT-like applications</strong>
</p>

<p align="center">
  <a href="#features"><strong>Features</strong></a> ·
  <a href="#installation"><strong>Installation</strong></a> ·
  <a href="#quick-start"><strong>Quick Start</strong></a> ·
  <a href="#documentation"><strong>Documentation</strong></a>
</p>

<br>

Welcome to BunGPT, a comprehensive Python project template inspired by OpenAI's gpt-oss repository. This template provides a solid foundation for building GPT-like applications with modern Python practices, comprehensive tooling, and extensible architecture.

## Features

### 🚀 **Core Functionality**
- **Modern Python Packaging**: Built with `pyproject.toml` and follows Python packaging best practices
- **Inference Engine**: PyTorch-based inference with Transformers library support
- **Flexible Configuration**: Pydantic-based configuration management with environment variable support
- **Comprehensive Logging**: Structured logging with configurable levels and outputs

### 🛠️ **Built-in Tools**
- **Python Tool**: Safe code execution with security restrictions
- **Browser Tool**: Web browsing and search capabilities
- **Code Tool**: File management and multi-language code execution
- **Extensible Architecture**: Easy to add custom tools

### 🌐 **API & Interfaces**
- **FastAPI Server**: OpenAI-compatible API endpoints
- **CLI Interface**: Comprehensive command-line tools
- **Streaming Support**: Real-time response streaming
- **Authentication**: API key-based security

### 🧪 **Development & Testing**
- **Comprehensive Test Suite**: Unit and integration tests with pytest
- **Code Quality Tools**: Black, isort, flake8, and mypy integration
- **Type Hints**: Full type annotation support
- **Documentation**: Example code and configuration templates

## Installation

### From PyPI (when published)
```bash
pip install bungpt
```

### From Source
```bash
git clone https://github.com/BunGPT/BunGPT.git
cd BunGPT
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/BunGPT/BunGPT.git
cd BunGPT
pip install -e ".[dev]"
```

## Quick Start

### 1. Basic Text Generation
```python
from bungpt.models.inference import InferenceEngine

engine = InferenceEngine(
    model_path="your-model-path",  # Local path or HuggingFace model ID
    device="auto"
)

engine.load_model()
response = engine.generate(
    prompt="Hello, how are you?",
    max_length=100,
    temperature=0.7
)
print(response)
```

### 2. Using Tools
```python
import asyncio
from bungpt.tools.python_tool import PythonTool

async def main():
    tool = PythonTool()
    result = await tool.execute(code="print('Hello from BunGPT!')")
    print(result.result)

asyncio.run(main())
```

### 3. CLI Usage
```bash
# Start interactive chat
bungpt chat --model-path /path/to/model --enable-python --enable-browser

# Generate text from command line
bungpt generate "What is the meaning of life?" --model-path /path/to/model

# Start API server
bungpt serve --host 0.0.0.0 --port 8000 --model-path /path/to/model

# Test tools
bungpt test-tool python "print('Hello, World!')"
```

### 4. API Server
```bash
# Start the server
bungpt serve --model-path /path/to/model

# Make requests
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bungpt",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7
  }'
```

## Project Structure

```
BunGPT/
├── bungpt/                 # Main package
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   ├── logger.py      # Logging setup
│   │   └── base.py        # Base classes
│   ├── models/            # Model implementations
│   │   ├── inference.py   # Inference engine
│   │   └── tokenizer_utils.py
│   ├── tools/             # Tool implementations
│   │   ├── base_tool.py   # Tool framework
│   │   ├── python_tool.py # Python execution
│   │   ├── browser_tool.py # Web browsing
│   │   └── code_tool.py   # Code management
│   ├── api/               # API server
│   │   ├── server.py      # FastAPI application
│   │   └── models.py      # API data models
│   ├── cli/               # Command-line interface
│   └── utils/             # Utility functions
├── examples/              # Example scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── configs/               # Configuration examples
└── pyproject.toml         # Project configuration
```

## Configuration

BunGPT uses a flexible configuration system that supports:

- **Environment Variables**: Prefix with `BUNGPT_`
- **Configuration Files**: YAML, JSON, or Python files
- **Programmatic Configuration**: Direct Python object configuration

### Example Configuration

```python
from bungpt.core.config import Config

config = Config(
    model_name="my-gpt-model",
    model_path="/path/to/model",
    device="cuda",
    api_port=8000,
    enable_python_tool=True,
    enable_browser_tool=True,
    log_level="INFO"
)
```

Or using environment variables:
```bash
export BUNGPT_MODEL_PATH="/path/to/model"
export BUNGPT_DEVICE="cuda"
export BUNGPT_API_PORT=8000
export BUNGPT_LOG_LEVEL="INFO"
```

## Tools

### Python Tool
Execute Python code safely with security restrictions:

```python
from bungpt.tools.python_tool import PythonTool

tool = PythonTool()
result = await tool.execute(code="""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(f"Fibonacci(10) = {fibonacci(10)}")
""")
```

### Browser Tool
Search the web and browse pages:

```python
from bungpt.tools.browser_tool import BrowserTool

tool = BrowserTool()

# Search the web
result = await tool.execute(action="search", query="Python programming")

# Open a specific URL
result = await tool.execute(action="open", url="https://python.org")

# Find text on current page
result = await tool.execute(action="find", text="download")
```

### Code Tool
Manage and execute code files:

```python
from bungpt.tools.code_tool import CodeTool

tool = CodeTool()

# Create a file
await tool.execute(action="create", filename="hello.py", content="print('Hello!')")

# Execute the file
result = await tool.execute(action="execute", filename="hello.py", language="python")
```

## API Reference

### Chat Completions Endpoint

```http
POST /v1/chat/completions
```

**Request Body:**
```json
{
  "model": "bungpt",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "bungpt",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you today?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 12,
    "total_tokens": 22
  }
}
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/BunGPT/BunGPT.git
cd BunGPT

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bungpt

# Run specific test file
pytest tests/unit/test_config.py
```

### Code Formatting

```bash
# Format code
black bungpt tests examples

# Sort imports
isort bungpt tests examples

# Check types
mypy bungpt

# Lint code
flake8 bungpt tests examples
```

## Examples

Check out the `examples/` directory for comprehensive examples:

- **`basic_usage.py`**: Basic library usage
- **`chat_example.py`**: Interactive chat implementation
- **`api_client.py`**: API client example
- **`custom_tool.py`**: Creating custom tools

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [OpenAI's gpt-oss](https://github.com/openai/gpt-oss) repository
- Built with modern Python tools and best practices
- Thanks to the open-source community for the excellent libraries used in this project

## Support

- **Documentation**: [https://bungpt.readthedocs.io](https://bungpt.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/BunGPT/BunGPT/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BunGPT/BunGPT/discussions)

---

<p align="center">
  <strong>Built with ❤️ by the BunGPT Team</strong>
</p>
