"""Code execution and file management tool for BunGPT."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from bungpt.tools.base_tool import Tool, ToolParameter, ToolResult


class CodeTool(Tool):
    """Tool for creating, updating, and executing code files."""
    
    def __init__(
        self,
        working_dir: Optional[str] = None,
        timeout: int = 30,
        **kwargs: Any,
    ) -> None:
        """Initialize the code tool.
        
        Args:
            working_dir: Working directory for code execution
            timeout: Execution timeout in seconds
            **kwargs: Additional configuration
        """
        parameters = [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["create", "read", "update", "delete", "execute", "list"],
            ),
            ToolParameter(
                name="filename",
                type="string",
                description="Name of the file to work with",
            ),
            ToolParameter(
                name="content",
                type="string",
                description="File content (for create/update actions)",
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Programming language (for execute action)",
                enum=["python", "javascript", "bash", "shell"],
            ),
            ToolParameter(
                name="args",
                type="string",
                description="Command line arguments (for execute action)",
            ),
        ]
        
        super().__init__(
            name="code",
            description="Create, read, update, delete, and execute code files",
            parameters=parameters,
            **kwargs,
        )
        
        self.working_dir = Path(working_dir) if working_dir else Path(tempfile.mkdtemp())
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        
        # Supported languages and their execution commands
        self.language_commands = {
            "python": ["python", "{filename}"],
            "javascript": ["node", "{filename}"],
            "bash": ["bash", "{filename}"],
            "shell": ["sh", "{filename}"],
        }
    
    def _get_file_path(self, filename: str) -> Path:
        """Get the full file path within the working directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Full file path
        """
        # Ensure the filename is safe (no directory traversal)
        safe_filename = os.path.basename(filename)
        return self.working_dir / safe_filename
    
    async def _create_file(self, filename: str, content: str) -> ToolResult:
        """Create a new file with the given content.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            Tool execution result
        """
        file_path = self._get_file_path(filename)
        
        if file_path.exists():
            return ToolResult(
                success=False,
                error=f"File '{filename}' already exists. Use 'update' action to modify it.",
            )
        
        try:
            file_path.write_text(content, encoding='utf-8')
            
            return ToolResult(
                success=True,
                result=f"File '{filename}' created successfully",
                metadata={
                    "filename": filename,
                    "path": str(file_path),
                    "size": len(content),
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to create file '{filename}': {str(e)}",
            )
    
    async def _read_file(self, filename: str) -> ToolResult:
        """Read the content of a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Tool execution result
        """
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"File '{filename}' does not exist",
            )
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            return ToolResult(
                success=True,
                result=f"Content of '{filename}':\\n\\n{content}",
                metadata={
                    "filename": filename,
                    "path": str(file_path),
                    "size": len(content),
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to read file '{filename}': {str(e)}",
            )
    
    async def _update_file(self, filename: str, content: str) -> ToolResult:
        """Update an existing file with new content.
        
        Args:
            filename: Name of the file
            content: New file content
            
        Returns:
            Tool execution result
        """
        file_path = self._get_file_path(filename)
        
        try:
            file_path.write_text(content, encoding='utf-8')
            
            return ToolResult(
                success=True,
                result=f"File '{filename}' updated successfully",
                metadata={
                    "filename": filename,
                    "path": str(file_path),
                    "size": len(content),
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to update file '{filename}': {str(e)}",
            )
    
    async def _delete_file(self, filename: str) -> ToolResult:
        """Delete a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Tool execution result
        """
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"File '{filename}' does not exist",
            )
        
        try:
            file_path.unlink()
            
            return ToolResult(
                success=True,
                result=f"File '{filename}' deleted successfully",
                metadata={
                    "filename": filename,
                    "path": str(file_path),
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to delete file '{filename}': {str(e)}",
            )
    
    async def _list_files(self) -> ToolResult:
        """List all files in the working directory.
        
        Returns:
            Tool execution result
        """
        try:
            files = []
            for file_path in self.working_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "extension": file_path.suffix,
                    })
            
            if not files:
                return ToolResult(
                    success=True,
                    result="No files found in the working directory",
                    metadata={"working_dir": str(self.working_dir)},
                )
            
            # Format file list
            result_text = f"Files in {self.working_dir}:\\n\\n"
            for file_info in sorted(files, key=lambda x: x["name"]):
                result_text += f"- {file_info['name']} ({file_info['size']} bytes)\\n"
            
            return ToolResult(
                success=True,
                result=result_text,
                metadata={
                    "working_dir": str(self.working_dir),
                    "files": files,
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to list files: {str(e)}",
            )
    
    async def _execute_file(
        self,
        filename: str,
        language: str,
        args: Optional[str] = None,
    ) -> ToolResult:
        """Execute a code file.
        
        Args:
            filename: Name of the file to execute
            language: Programming language
            args: Command line arguments
            
        Returns:
            Tool execution result
        """
        file_path = self._get_file_path(filename)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"File '{filename}' does not exist",
            )
        
        if language not in self.language_commands:
            return ToolResult(
                success=False,
                error=f"Unsupported language: {language}. Supported: {list(self.language_commands.keys())}",
            )
        
        try:
            # Build command
            command_template = self.language_commands[language]
            command = [cmd.format(filename=str(file_path)) if "{filename}" in cmd else cmd for cmd in command_template]
            
            # Add arguments if provided
            if args:
                command.extend(args.split())
            
            # Execute the command
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            
            # Prepare output
            output = ""
            if result.stdout:
                output += f"STDOUT:\\n{result.stdout}\\n"
            if result.stderr:
                output += f"STDERR:\\n{result.stderr}\\n"
            
            if not output:
                output = "Command executed successfully (no output)"
            
            return ToolResult(
                success=result.returncode == 0,
                result=output,
                error=f"Command failed with return code {result.returncode}" if result.returncode != 0 else None,
                metadata={
                    "filename": filename,
                    "language": language,
                    "command": " ".join(command),
                    "return_code": result.returncode,
                    "execution_time": "unknown",  # Would need time tracking
                },
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Execution timed out after {self.timeout} seconds",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to execute file '{filename}': {str(e)}",
            )
    
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the code tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        action = kwargs["action"]
        
        try:
            if action == "create":
                filename = kwargs.get("filename")
                content = kwargs.get("content")
                
                if not filename:
                    return ToolResult(
                        success=False,
                        error="Filename parameter is required for create action",
                    )
                if not content:
                    return ToolResult(
                        success=False,
                        error="Content parameter is required for create action",
                    )
                
                return await self._create_file(filename, content)
            
            elif action == "read":
                filename = kwargs.get("filename")
                
                if not filename:
                    return ToolResult(
                        success=False,
                        error="Filename parameter is required for read action",
                    )
                
                return await self._read_file(filename)
            
            elif action == "update":
                filename = kwargs.get("filename")
                content = kwargs.get("content")
                
                if not filename:
                    return ToolResult(
                        success=False,
                        error="Filename parameter is required for update action",
                    )
                if not content:
                    return ToolResult(
                        success=False,
                        error="Content parameter is required for update action",
                    )
                
                return await self._update_file(filename, content)
            
            elif action == "delete":
                filename = kwargs.get("filename")
                
                if not filename:
                    return ToolResult(
                        success=False,
                        error="Filename parameter is required for delete action",
                    )
                
                return await self._delete_file(filename)
            
            elif action == "list":
                return await self._list_files()
            
            elif action == "execute":
                filename = kwargs.get("filename")
                language = kwargs.get("language")
                args = kwargs.get("args")
                
                if not filename:
                    return ToolResult(
                        success=False,
                        error="Filename parameter is required for execute action",
                    )
                if not language:
                    return ToolResult(
                        success=False,
                        error="Language parameter is required for execute action",
                    )
                
                return await self._execute_file(filename, language, args)
            
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}",
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code tool error: {str(e)}",
            )
    
    def cleanup(self) -> None:
        """Clean up the working directory."""
        try:
            import shutil
            if self.working_dir.exists():
                shutil.rmtree(self.working_dir)
        except Exception as e:
            self.logger.warning(f"Failed to clean up working directory: {e}")