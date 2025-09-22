"""FastAPI server implementation for BunGPT."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from bungpt.api.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    Choice,
    StreamChoice,
    Usage,
    ErrorResponse,
    HealthResponse,
    ModelsResponse,
    ModelInfo,
    Message,
)
from bungpt.core.config import get_config
from bungpt.core.logger import get_logger
from bungpt.models.inference import InferenceEngine
from bungpt.tools.base_tool import get_tool_registry


# Global variables
inference_engine: Optional[InferenceEngine] = None
start_time = time.time()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global inference_engine
    
    config = get_config()
    logger.info("Starting BunGPT API server")
    
    # Initialize inference engine if model path is provided
    if config.model_path:
        try:
            inference_engine = InferenceEngine(
                model_path=config.model_path,
                device=config.device,
            )
            inference_engine.load_model()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            inference_engine = None
    
    yield
    
    # Cleanup
    logger.info("Shutting down BunGPT API server")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    config = get_config()
    
    app = FastAPI(
        title="BunGPT API",
        description="A GPT-like API server powered by BunGPT",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        """Authentication middleware."""
        if config.api_key:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
            
            token = auth_header.split(" ", 1)[1]
            if token != config.api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        response = await call_next(request)
        return response
    
    @app.get("/health")
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            version="0.1.0",
            model_loaded=inference_engine is not None,
            uptime=time.time() - start_time,
        )
    
    @app.get("/v1/models")
    async def list_models() -> ModelsResponse:
        """List available models."""
        models = []
        
        if inference_engine:
            models.append(ModelInfo(
                id=get_config().model_name,
                created=int(start_time),
                owned_by="bungpt",
            ))
        
        return ModelsResponse(data=models)
    
    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """Handle chat completion requests."""
        if not inference_engine:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        try:
            if request.stream:
                return StreamingResponse(
                    stream_chat_completion(request),
                    media_type="text/plain",
                )
            else:
                return await create_chat_completion(request)
                
        except Exception as e:
            logger.error(f"Chat completion error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def create_chat_completion(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """Create a chat completion response.
    
    Args:
        request: Chat completion request
        
    Returns:
        Chat completion response
    """
    global inference_engine
    
    # Convert messages to prompt
    prompt = format_messages_for_inference(request.messages)
    
    # Generate response
    generated_text = inference_engine.generate(
        prompt=prompt,
        max_length=request.max_tokens or 150,
        temperature=request.temperature,
        top_p=request.top_p,
    )
    
    # Calculate token usage
    token_usage = inference_engine.get_token_usage(prompt, generated_text)
    
    # Create response
    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    
    choice = Choice(
        index=0,
        message=Message(
            role="assistant",
            content=generated_text,
        ),
        finish_reason="stop" if not request.max_tokens or len(generated_text) < request.max_tokens else "length",
    )
    
    return ChatCompletionResponse(
        id=response_id,
        created=int(time.time()),
        model=request.model,
        choices=[choice],
        usage=Usage(
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
            total_tokens=token_usage.total_tokens,
        ),
    )


async def stream_chat_completion(request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
    """Stream a chat completion response.
    
    Args:
        request: Chat completion request
        
    Yields:
        Server-sent events for streaming response
    """
    global inference_engine
    
    # Convert messages to prompt
    prompt = format_messages_for_inference(request.messages)
    
    # Generate response (simplified streaming - in practice you'd want token-by-token streaming)
    generated_text = inference_engine.generate(
        prompt=prompt,
        max_length=request.max_tokens or 150,
        temperature=request.temperature,
        top_p=request.top_p,
    )
    
    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    
    # Simulate token-by-token streaming by splitting the response
    words = generated_text.split()
    
    for i, word in enumerate(words):
        chunk = ChatCompletionStreamResponse(
            id=response_id,
            created=created,
            model=request.model,
            choices=[StreamChoice(
                index=0,
                delta={"content": word + " " if i < len(words) - 1 else word},
            )],
        )
        
        yield f"data: {chunk.json()}\\n\\n"
    
    # Send finish chunk
    finish_chunk = ChatCompletionStreamResponse(
        id=response_id,
        created=created,
        model=request.model,
        choices=[StreamChoice(
            index=0,
            delta={},
            finish_reason="stop",
        )],
    )
    
    yield f"data: {finish_chunk.json()}\\n\\n"
    yield "data: [DONE]\\n\\n"


def format_messages_for_inference(messages: list) -> str:
    """Format messages for inference.
    
    Args:
        messages: List of messages
        
    Returns:
        Formatted prompt string
    """
    formatted_messages = []
    
    for message in messages:
        role = message.role
        content = message.content
        
        if role == "system":
            formatted_messages.append(f"System: {content}")
        elif role == "user":
            formatted_messages.append(f"User: {content}")
        elif role == "assistant":
            formatted_messages.append(f"Assistant: {content}")
        else:
            formatted_messages.append(f"{role.capitalize()}: {content}")
    
    formatted_messages.append("Assistant:")
    return "\\n".join(formatted_messages)


def run_server(
    host: str = "localhost",
    port: int = 8000,
    workers: int = 1,
    **kwargs,
) -> None:
    """Run the API server.
    
    Args:
        host: Server host
        port: Server port
        workers: Number of workers
        **kwargs: Additional uvicorn arguments
    """
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        **kwargs,
    )


if __name__ == "__main__":
    run_server()