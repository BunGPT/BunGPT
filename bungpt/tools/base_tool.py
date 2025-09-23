"""Base tool implementation for BunGPT."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from bungpt.core.base import BaseTool
from bungpt.core.logger import get_logger


class ToolParameter(BaseModel):
    """Represents a tool parameter."""
    
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


class ToolSchema(BaseModel):
    """Represents a tool's schema."""
    
    name: str
    description: str
    parameters: List[ToolParameter]
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            
            if param.enum:
                prop["enum"] = param.enum
            
            if param.default is not None:
                prop["default"] = param.default
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


class ToolResult(BaseModel):
    """Represents the result of a tool execution."""
    
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            return f"Success: {self.result}"
        else:
            return f"Error: {self.error}"


class Tool(BaseTool):
    """Enhanced base tool implementation."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[List[ToolParameter]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the tool.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: List of tool parameters
            **kwargs: Additional configuration
        """
        super().__init__(name, description, **kwargs)
        self.parameters = parameters or []
        self.schema = ToolSchema(
            name=name,
            description=description,
            parameters=self.parameters,
        )
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process tool parameters.
        
        Args:
            params: Input parameters
            
        Returns:
            Validated parameters
            
        Raises:
            ValueError: If validation fails
        """
        validated = {}
        
        for param in self.parameters:
            value = params.get(param.name, param.default)
            
            # Check required parameters
            if param.required and value is None:
                raise ValueError(f"Required parameter '{param.name}' is missing")
            
            # Check enum values
            if param.enum and value not in param.enum:
                raise ValueError(
                    f"Parameter '{param.name}' must be one of {param.enum}, got {value}"
                )
            
            # Basic type checking (simplified)
            if value is not None:
                if param.type == "string" and not isinstance(value, str):
                    value = str(value)
                elif param.type == "integer" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parameter '{param.name}' must be an integer")
                elif param.type == "number" and not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Parameter '{param.name}' must be a number")
                elif param.type == "boolean" and not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes", "on")
                    else:
                        value = bool(value)
            
            if value is not None:
                validated[param.name] = value
        
        return validated
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema in OpenAI format.
        
        Returns:
            Tool schema
        """
        return self.schema.to_openai_format()
    
    async def safe_execute(self, **kwargs: Any) -> ToolResult:
        """Safely execute the tool with error handling.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(kwargs)
            
            # Execute the tool
            result = await self.execute(**validated_params)
            
            self.logger.info(f"Tool '{self.name}' executed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Tool '{self.name}' execution failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ToolResult(
                success=False,
                error=error_msg,
                metadata={"exception_type": type(e).__name__},
            )


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def register(self, tool: Tool) -> None:
        """Register a tool.
        
        Args:
            tool: Tool to register
        """
        if tool.name in self._tools:
            self.logger.warning(f"Tool '{tool.name}' is already registered, overwriting")
        
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, name: str) -> None:
        """Unregister a tool.
        
        Args:
            name: Name of the tool to unregister
        """
        if name in self._tools:
            del self._tools[name]
            self.logger.info(f"Unregistered tool: {name}")
        else:
            self.logger.warning(f"Tool '{name}' not found in registry")
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def execute_tool(self, name: str, **kwargs: Any) -> ToolResult:
        """Execute a tool by name.
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get(name)
        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found in registry",
            )
        
        return await tool.safe_execute(**kwargs)


# Global tool registry
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry