"""Python code execution tool for BunGPT."""

import asyncio
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Any, Dict, Optional

from bungpt.tools.base_tool import Tool, ToolParameter, ToolResult


class PythonTool(Tool):
    """Tool for executing Python code safely."""
    
    def __init__(self, timeout: int = 30, **kwargs: Any) -> None:
        """Initialize the Python tool.
        
        Args:
            timeout: Execution timeout in seconds
            **kwargs: Additional configuration
        """
        parameters = [
            ToolParameter(
                name="code",
                type="string",
                description="Python code to execute",
                required=True,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Execution timeout in seconds",
                default=timeout,
            ),
        ]
        
        super().__init__(
            name="python",
            description="Execute Python code and return the output",
            parameters=parameters,
            **kwargs,
        )
        
        self.timeout = timeout
        self.allowed_modules = {
            # Standard library
            "math", "random", "datetime", "time", "json", "csv", "re",
            "collections", "itertools", "functools", "operator",
            "statistics", "decimal", "fractions",
            # Data science
            "numpy", "pandas", "matplotlib", "seaborn", "plotly",
            "scipy", "sklearn", "requests",
            # Utilities
            "base64", "hashlib", "uuid", "urllib",
        }
        
        self.forbidden_modules = {
            "os", "sys", "subprocess", "socket", "urllib.request",
            "urllib.parse", "urllib.error", "http", "ftplib", "smtplib",
            "telnetlib", "shutil", "tempfile", "glob", "pathlib",
            "importlib", "__builtin__", "builtins",
        }
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a safe globals dictionary for code execution.
        
        Returns:
            Dictionary with safe globals
        """
        safe_globals = {
            "__builtins__": {
                # Safe built-ins
                "abs", "all", "any", "ascii", "bin", "bool", "bytearray",
                "bytes", "callable", "chr", "classmethod", "complex",
                "dict", "dir", "divmod", "enumerate", "eval", "filter",
                "float", "format", "frozenset", "getattr", "globals",
                "hasattr", "hash", "help", "hex", "id", "input", "int",
                "isinstance", "issubclass", "iter", "len", "list",
                "locals", "map", "max", "memoryview", "min", "next",
                "object", "oct", "ord", "pow", "print", "property",
                "range", "repr", "reversed", "round", "set", "setattr",
                "slice", "sorted", "staticmethod", "str", "sum", "super",
                "tuple", "type", "vars", "zip",
                # Math functions
                "abs", "divmod", "max", "min", "pow", "round", "sum",
                # Type conversion
                "bool", "int", "float", "str", "list", "tuple", "dict", "set",
            },
        }
        
        # Add safe modules
        try:
            import math
            safe_globals["math"] = math
        except ImportError:
            pass
        
        try:
            import random
            safe_globals["random"] = random
        except ImportError:
            pass
        
        try:
            import datetime
            safe_globals["datetime"] = datetime
        except ImportError:
            pass
        
        try:
            import json
            safe_globals["json"] = json
        except ImportError:
            pass
        
        return safe_globals
    
    def _check_code_safety(self, code: str) -> Optional[str]:
        """Check if code is safe to execute.
        
        Args:
            code: Code to check
            
        Returns:
            Error message if unsafe, None if safe
        """
        # Check for forbidden keywords/patterns
        forbidden_patterns = [
            "import os", "import sys", "import subprocess",
            "from os", "from sys", "from subprocess",
            "__import__", "exec(", "eval(",
            "open(", "file(", "input(", "raw_input(",
            "globals(", "locals(", "vars(",
            "getattr", "setattr", "delattr",
            "hasattr", "__", "compile",
        ]
        
        code_lower = code.lower()
        for pattern in forbidden_patterns:
            if pattern in code_lower:
                return f"Forbidden pattern detected: {pattern}"
        
        # Check for forbidden modules
        for module in self.forbidden_modules:
            if f"import {module}" in code_lower or f"from {module}" in code_lower:
                return f"Forbidden module: {module}"
        
        return None
    
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute Python code.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        code = kwargs["code"]
        timeout = kwargs.get("timeout", self.timeout)
        
        # Check code safety
        safety_error = self._check_code_safety(code)
        if safety_error:
            return ToolResult(
                success=False,
                error=f"Code safety check failed: {safety_error}",
            )
        
        # Prepare execution environment
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        safe_globals = self._create_safe_globals()
        safe_locals = {}
        
        try:
            # Execute code with timeout
            async def _execute():
                try:
                    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                        # Compile the code first to catch syntax errors
                        compiled_code = compile(code, "<string>", "exec")
                        
                        # Execute the compiled code
                        exec(compiled_code, safe_globals, safe_locals)
                    
                    return True, None
                except Exception as e:
                    return False, str(e)
            
            # Run with timeout
            try:
                success, error = await asyncio.wait_for(_execute(), timeout=timeout)
            except asyncio.TimeoutError:
                return ToolResult(
                    success=False,
                    error=f"Code execution timed out after {timeout} seconds",
                )
            
            # Get output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if not success:
                return ToolResult(
                    success=False,
                    error=error,
                    metadata={
                        "stdout": stdout_output,
                        "stderr": stderr_output,
                    },
                )
            
            # Check if there's any output
            result_output = stdout_output
            if stderr_output:
                if result_output:
                    result_output += f"\\nStderr: {stderr_output}"
                else:
                    result_output = f"Stderr: {stderr_output}"
            
            if not result_output:
                result_output = "Code executed successfully (no output)"
            
            return ToolResult(
                success=True,
                result=result_output,
                metadata={
                    "stdout": stdout_output,
                    "stderr": stderr_output,
                    "locals": {k: str(v) for k, v in safe_locals.items()},
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Execution error: {str(e)}",
                metadata={
                    "traceback": traceback.format_exc(),
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                },
            )


# Alternative implementation using Docker (more secure but requires Docker)
class DockerPythonTool(Tool):
    """Tool for executing Python code in a Docker container."""
    
    def __init__(self, image: str = "python:3.11-slim", timeout: int = 30, **kwargs: Any) -> None:
        """Initialize the Docker Python tool.
        
        Args:
            image: Docker image to use
            timeout: Execution timeout in seconds
            **kwargs: Additional configuration
        """
        parameters = [
            ToolParameter(
                name="code",
                type="string",
                description="Python code to execute",
                required=True,
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Execution timeout in seconds",
                default=timeout,
            ),
        ]
        
        super().__init__(
            name="docker_python",
            description="Execute Python code in a Docker container",
            parameters=parameters,
            **kwargs,
        )
        
        self.image = image
        self.timeout = timeout
    
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute Python code in Docker container.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        code = kwargs["code"]
        timeout = kwargs.get("timeout", self.timeout)
        
        try:
            import docker
            
            client = docker.from_env()
            
            # Create a temporary file with the code
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Run the code in Docker container
                result = client.containers.run(
                    self.image,
                    f"python {os.path.basename(temp_file)}",
                    volumes={
                        os.path.dirname(temp_file): {
                            'bind': '/app',
                            'mode': 'ro'
                        }
                    },
                    working_dir='/app',
                    remove=True,
                    network_disabled=True,
                    mem_limit='128m',
                    cpu_period=100000,
                    cpu_quota=50000,  # 50% CPU
                    timeout=timeout,
                )
                
                output = result.decode('utf-8')
                
                return ToolResult(
                    success=True,
                    result=output,
                    metadata={"execution_method": "docker"},
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file)
                
        except ImportError:
            return ToolResult(
                success=False,
                error="Docker library not available. Install with: pip install docker",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Docker execution error: {str(e)}",
            )