"""Tests for tools functionality."""

import pytest

from bungpt.tools.base_tool import Tool, ToolParameter, ToolResult, ToolRegistry
from bungpt.tools.python_tool import PythonTool


class TestTool(Tool):
    """Test tool implementation."""
    
    def __init__(self):
        parameters = [
            ToolParameter(
                name="test_param",
                type="string",
                description="A test parameter",
                required=True,
            ),
            ToolParameter(
                name="optional_param",
                type="integer",
                description="An optional parameter",
                default=42,
            ),
        ]
        
        super().__init__(
            name="test_tool",
            description="A test tool",
            parameters=parameters,
        )
    
    async def execute(self, **kwargs):
        return ToolResult(
            success=True,
            result=f"Executed with params: {kwargs}",
        )


def test_tool_parameter():
    """Test tool parameter creation."""
    param = ToolParameter(
        name="test",
        type="string",
        description="A test parameter",
        required=True,
    )
    
    assert param.name == "test"
    assert param.type == "string"
    assert param.required is True


def test_tool_result():
    """Test tool result creation."""
    # Success result
    success_result = ToolResult(success=True, result="Success!")
    assert success_result.success is True
    assert success_result.result == "Success!"
    assert success_result.error is None
    
    # Error result
    error_result = ToolResult(success=False, error="Something went wrong")
    assert error_result.success is False
    assert error_result.error == "Something went wrong"


def test_tool_initialization():
    """Test tool initialization."""
    tool = TestTool()
    
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert len(tool.parameters) == 2


def test_tool_schema():
    """Test tool schema generation."""
    tool = TestTool()
    schema = tool.get_schema()
    
    assert schema["name"] == "test_tool"
    assert schema["description"] == "A test tool"
    assert "parameters" in schema
    assert "test_param" in schema["parameters"]["properties"]
    assert "optional_param" in schema["parameters"]["properties"]


def test_tool_parameter_validation():
    """Test tool parameter validation."""
    tool = TestTool()
    
    # Valid parameters
    valid_params = {"test_param": "hello", "optional_param": 100}
    validated = tool.validate_parameters(valid_params)
    assert validated["test_param"] == "hello"
    assert validated["optional_param"] == 100
    
    # Missing required parameter
    with pytest.raises(ValueError):
        tool.validate_parameters({"optional_param": 100})
    
    # Using default value
    partial_params = {"test_param": "hello"}
    validated = tool.validate_parameters(partial_params)
    assert validated["optional_param"] == 42


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""
    tool = TestTool()
    
    result = await tool.safe_execute(test_param="hello", optional_param=123)
    
    assert result.success is True
    assert "hello" in result.result
    assert "123" in result.result


def test_tool_registry():
    """Test tool registry functionality."""
    registry = ToolRegistry()
    tool = TestTool()
    
    # Register tool
    registry.register(tool)
    assert "test_tool" in registry.list_tools()
    
    # Get tool
    retrieved_tool = registry.get("test_tool")
    assert retrieved_tool is tool
    
    # Get schemas
    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "test_tool"
    
    # Unregister tool
    registry.unregister("test_tool")
    assert "test_tool" not in registry.list_tools()


@pytest.mark.asyncio
async def test_tool_registry_execution():
    """Test tool execution through registry."""
    registry = ToolRegistry()
    tool = TestTool()
    registry.register(tool)
    
    result = await registry.execute_tool("test_tool", test_param="hello")
    
    assert result.success is True
    assert "hello" in result.result


@pytest.mark.asyncio
async def test_python_tool_basic():
    """Test basic Python tool functionality."""
    tool = PythonTool()
    
    # Test simple calculation
    result = await tool.execute(code="result = 2 + 2\nprint(result)")
    
    assert result.success is True
    assert "4" in result.result


@pytest.mark.asyncio
async def test_python_tool_forbidden_code():
    """Test Python tool with forbidden code."""
    tool = PythonTool()
    
    # Test forbidden import
    result = await tool.execute(code="import os\nprint(os.getcwd())")
    
    assert result.success is False
    assert "safety check failed" in result.error.lower()


@pytest.mark.asyncio
async def test_python_tool_syntax_error():
    """Test Python tool with syntax error."""
    tool = PythonTool()
    
    # Test syntax error
    result = await tool.execute(code="print('hello'")  # Missing closing parenthesis
    
    assert result.success is False