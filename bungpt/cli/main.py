"""Main CLI entry point for BunGPT."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from bungpt import __version__
from bungpt.core.config import Config, set_config
from bungpt.core.logger import setup_logging, get_logger
from bungpt.models.inference import InferenceEngine
from bungpt.tools.base_tool import get_tool_registry
from bungpt.tools.python_tool import PythonTool
from bungpt.tools.browser_tool import BrowserTool
from bungpt.tools.code_tool import CodeTool


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Configuration file path",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--log-file",
    type=click.Path(),
    help="Log file path",
)
@click.pass_context
def cli(ctx, config, log_level, log_file):
    """BunGPT - A Python project template for GPT-like applications."""
    ctx.ensure_object(dict)
    
    # Set up logging
    setup_logging(level=log_level, log_file=log_file)
    
    # Load configuration
    if config:
        ctx.obj["config"] = Config.from_file(config)
    else:
        ctx.obj["config"] = Config()
    
    set_config(ctx.obj["config"])


@cli.command()
@click.option(
    "--model-path",
    type=click.Path(exists=True),
    help="Path to the model files",
)
@click.option(
    "--device",
    default="auto",
    help="Device to run inference on",
)
@click.option(
    "--max-length",
    type=int,
    default=150,
    help="Maximum length of generated text",
)
@click.option(
    "--temperature",
    type=float,
    default=1.0,
    help="Sampling temperature",
)
@click.option(
    "--top-p",
    type=float,
    default=1.0,
    help="Top-p sampling parameter",
)
@click.argument("prompt")
@click.pass_context
def generate(ctx, model_path, device, max_length, temperature, top_p, prompt):
    """Generate text from a prompt."""
    config = ctx.obj["config"]
    logger = get_logger(__name__)
    
    if model_path:
        config.model_path = Path(model_path)
    
    if not config.model_path:
        click.echo("Error: Model path is required. Use --model-path or set BUNGPT_MODEL_PATH", err=True)
        sys.exit(1)
    
    try:
        # Initialize inference engine
        engine = InferenceEngine(
            model_path=config.model_path,
            device=device,
        )
        
        click.echo("Loading model...")
        engine.load_model()
        
        click.echo("Generating text...")
        generated_text = engine.generate(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
        )
        
        click.echo(f"\\nPrompt: {prompt}")
        click.echo(f"Generated: {generated_text}")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--model-path",
    type=click.Path(exists=True),
    help="Path to the model files",
)
@click.option(
    "--device",
    default="auto",
    help="Device to run inference on",
)
@click.option(
    "--enable-python",
    is_flag=True,
    help="Enable Python tool",
)
@click.option(
    "--enable-browser",
    is_flag=True,
    help="Enable browser tool",
)
@click.option(
    "--enable-code",
    is_flag=True,
    help="Enable code tool",
)
@click.option(
    "--max-length",
    type=int,
    default=150,
    help="Maximum length of generated text",
)
@click.pass_context
def chat(ctx, model_path, device, enable_python, enable_browser, enable_code, max_length):
    """Start an interactive chat session."""
    config = ctx.obj["config"]
    logger = get_logger(__name__)
    
    if model_path:
        config.model_path = Path(model_path)
    
    if not config.model_path:
        click.echo("Error: Model path is required. Use --model-path or set BUNGPT_MODEL_PATH", err=True)
        sys.exit(1)
    
    try:
        # Initialize inference engine
        engine = InferenceEngine(
            model_path=config.model_path,
            device=device,
        )
        
        click.echo("Loading model...")
        engine.load_model()
        
        # Initialize tools
        registry = get_tool_registry()
        
        if enable_python:
            registry.register(PythonTool())
            click.echo("Python tool enabled")
        
        if enable_browser:
            registry.register(BrowserTool())
            click.echo("Browser tool enabled")
        
        if enable_code:
            registry.register(CodeTool())
            click.echo("Code tool enabled")
        
        # Start chat loop
        asyncio.run(chat_loop(engine, registry, max_length))
        
    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def chat_loop(engine: InferenceEngine, registry, max_length: int):
    """Run the interactive chat loop.
    
    Args:
        engine: Inference engine
        registry: Tool registry
        max_length: Maximum generation length
    """
    click.echo("\\n=== BunGPT Chat ===")
    click.echo("Type 'quit' or 'exit' to end the conversation.")
    click.echo("Type 'help' for available commands.\\n")
    
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = click.prompt("You", type=str)
            
            if user_input.lower() in ["quit", "exit"]:
                click.echo("Goodbye!")
                break
            
            if user_input.lower() == "help":
                show_help(registry)
                continue
            
            if user_input.lower() == "clear":
                conversation_history.clear()
                click.echo("Conversation history cleared.")
                continue
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Format conversation for inference
            prompt = format_conversation(conversation_history)
            
            # Generate response
            response = engine.generate(
                prompt=prompt,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
            )
            
            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": response})
            
            # Display response
            click.echo(f"Assistant: {response}\\n")
            
        except KeyboardInterrupt:
            click.echo("\\nGoodbye!")
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def format_conversation(messages: list) -> str:
    """Format conversation history for inference.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Formatted conversation string
    """
    formatted = []
    
    for message in messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            formatted.append(f"User: {content}")
        elif role == "assistant":
            formatted.append(f"Assistant: {content}")
        else:
            formatted.append(f"{role.capitalize()}: {content}")
    
    formatted.append("Assistant:")
    return "\\n".join(formatted)


def show_help(registry):
    """Show help information.
    
    Args:
        registry: Tool registry
    """
    click.echo("Available commands:")
    click.echo("  help  - Show this help message")
    click.echo("  clear - Clear conversation history")
    click.echo("  quit  - Exit the chat")
    
    tools = registry.list_tools()
    if tools:
        click.echo("\\nAvailable tools:")
        for tool_name in tools:
            tool = registry.get(tool_name)
            click.echo(f"  {tool_name} - {tool.description}")
    
    click.echo()


@cli.command()
@click.option(
    "--host",
    default="localhost",
    help="Server host",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Server port",
)
@click.option(
    "--workers",
    type=int,
    default=1,
    help="Number of workers",
)
@click.option(
    "--model-path",
    type=click.Path(exists=True),
    help="Path to the model files",
)
@click.pass_context
def serve(ctx, host, port, workers, model_path):
    """Start the API server."""
    config = ctx.obj["config"]
    
    if model_path:
        config.model_path = Path(model_path)
    
    config.api_host = host
    config.api_port = port
    config.api_workers = workers
    
    from bungpt.api.server import run_server
    
    click.echo(f"Starting BunGPT API server on {host}:{port}")
    run_server(host=host, port=port, workers=workers)


@cli.command()
@click.option(
    "--tool",
    type=click.Choice(["python", "browser", "code"]),
    required=True,
    help="Tool to test",
)
@click.argument("args", nargs=-1)
def test_tool(tool, args):
    """Test a specific tool."""
    logger = get_logger(__name__)
    
    async def run_test():
        try:
            if tool == "python":
                tool_instance = PythonTool()
                if args:
                    code = " ".join(args)
                else:
                    code = "print('Hello from Python tool!')"
                result = await tool_instance.execute(code=code)
            
            elif tool == "browser":
                tool_instance = BrowserTool()
                if args:
                    if args[0] == "search":
                        result = await tool_instance.execute(action="search", query=" ".join(args[1:]))
                    elif args[0] == "open":
                        result = await tool_instance.execute(action="open", url=args[1])
                    else:
                        result = await tool_instance.execute(action="search", query=" ".join(args))
                else:
                    result = await tool_instance.execute(action="search", query="BunGPT")
            
            elif tool == "code":
                tool_instance = CodeTool()
                if args:
                    result = await tool_instance.execute(action="list")
                else:
                    # Create and execute a simple Python file
                    await tool_instance.execute(
                        action="create",
                        filename="test.py",
                        content="print('Hello from code tool!')"
                    )
                    result = await tool_instance.execute(
                        action="execute",
                        filename="test.py",
                        language="python"
                    )
            
            click.echo(f"Tool result: {result}")
            
        except Exception as e:
            logger.error(f"Tool test failed: {e}", exc_info=True)
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(run_test())


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()