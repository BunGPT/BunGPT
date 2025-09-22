"""Base classes and utilities for BunGPT."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel as PydanticBaseModel

from bungpt.core.logger import get_logger


class BaseModel(PydanticBaseModel):
    """Base Pydantic model with additional functionality."""
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        arbitrary_types_allowed = True
        extra = "forbid"


class BaseInferenceEngine(ABC):
    """Base class for inference engines."""
    
    def __init__(self, model_path: str, device: str = "auto", **kwargs: Any) -> None:
        """Initialize the inference engine.
        
        Args:
            model_path: Path to the model
            device: Device to run inference on
            **kwargs: Additional configuration
        """
        self.model_path = model_path
        self.device = device
        self.config = kwargs
        self.logger = get_logger(self.__class__.__name__)
        self._model = None
        self._tokenizer = None
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the model and tokenizer."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def batch_generate(
        self,
        prompts: List[str],
        max_length: int = 100,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs: Any,
    ) -> List[str]:
        """Generate text from multiple prompts.
        
        Args:
            prompts: List of input prompts
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated texts
        """
        pass


class BaseTool(ABC):
    """Base class for tools."""
    
    def __init__(self, name: str, description: str, **kwargs: Any) -> None:
        """Initialize the tool.
        
        Args:
            name: Tool name
            description: Tool description
            **kwargs: Additional configuration
        """
        self.name = name
        self.description = description
        self.config = kwargs
        self.logger = get_logger(f"{self.__class__.__name__}({name})")
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution results
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's parameter schema.
        
        Returns:
            JSON schema for tool parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }


class Message(BaseModel):
    """Represents a message in a conversation."""
    
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """String representation of the message."""
        return f"{self.role}: {self.content}"


class Conversation(BaseModel):
    """Represents a conversation with multiple messages."""
    
    messages: List[Message] = []
    metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the conversation.
        
        Args:
            role: Message role (user, assistant, system, etc.)
            content: Message content
            metadata: Optional message metadata
        """
        self.messages.append(Message(role=role, content=content, metadata=metadata))
    
    def get_messages_by_role(self, role: str) -> List[Message]:
        """Get all messages with a specific role.
        
        Args:
            role: Role to filter by
            
        Returns:
            List of messages with the specified role
        """
        return [msg for msg in self.messages if msg.role == role]
    
    def to_string(self, include_metadata: bool = False) -> str:
        """Convert conversation to a string representation.
        
        Args:
            include_metadata: Whether to include metadata in the output
            
        Returns:
            String representation of the conversation
        """
        lines = []
        for msg in self.messages:
            line = f"{msg.role}: {msg.content}"
            if include_metadata and msg.metadata:
                line += f" [metadata: {msg.metadata}]"
            lines.append(line)
        return "\n".join(lines)


class TokenUsage(BaseModel):
    """Token usage statistics."""
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        """Add two token usage objects."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )