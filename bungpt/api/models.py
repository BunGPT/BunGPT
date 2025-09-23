"""API models for BunGPT."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model."""
    
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    
    model: str
    messages: List[Message]
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    n: int = Field(default=1, ge=1, le=128)
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = Field(default=None, ge=1)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, str]]] = None


class Usage(BaseModel):
    """Token usage model."""
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    """Chat completion choice model."""
    
    index: int
    message: Message
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Chat completion response model."""
    
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    system_fingerprint: Optional[str] = None


class StreamChoice(BaseModel):
    """Streaming chat completion choice model."""
    
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    """Streaming chat completion response model."""
    
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
    system_fingerprint: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    version: str
    model_loaded: bool
    uptime: float


class ModelInfo(BaseModel):
    """Model information model."""
    
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: List[Dict[str, Any]] = []
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelsResponse(BaseModel):
    """Models list response model."""
    
    object: str = "list"
    data: List[ModelInfo]