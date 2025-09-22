"""Validation utilities."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def validate_model_path(path: str) -> bool:
    """Validate that a model path exists and is accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        path_obj = Path(path)
        
        # Check if it's a directory (for local models)
        if path_obj.is_dir():
            # Look for common model files
            model_files = [
                "config.json",
                "pytorch_model.bin",
                "model.safetensors",
                "tokenizer.json",
                "tokenizer_config.json",
            ]
            
            existing_files = [f for f in model_files if (path_obj / f).exists()]
            return len(existing_files) > 0
        
        # Check if it's a single model file
        if path_obj.is_file():
            valid_extensions = [".bin", ".safetensors", ".pt", ".pth"]
            return path_obj.suffix.lower() in valid_extensions
        
        # If it's neither a directory nor a file, it might be a Hugging Face model ID
        # Basic validation for Hugging Face model IDs
        if "/" in path and len(path.split("/")) == 2:
            org, model = path.split("/")
            # Basic format validation
            if re.match(r'^[a-zA-Z0-9._-]+$', org) and re.match(r'^[a-zA-Z0-9._-]+$', model):
                return True
        
        return False
        
    except Exception:
        return False


def validate_url(url: str) -> bool:
    """Validate that a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_port(port: int) -> bool:
    """Validate that a port number is valid.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 1 <= port <= 65535


def validate_temperature(temperature: float) -> bool:
    """Validate temperature parameter for text generation.
    
    Args:
        temperature: Temperature value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= temperature <= 2.0


def validate_top_p(top_p: float) -> bool:
    """Validate top_p parameter for text generation.
    
    Args:
        top_p: Top-p value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= top_p <= 1.0


def validate_max_tokens(max_tokens: Optional[int]) -> bool:
    """Validate max_tokens parameter.
    
    Args:
        max_tokens: Max tokens value to validate
        
    Returns:
        True if valid, False otherwise
    """
    if max_tokens is None:
        return True
    return isinstance(max_tokens, int) and max_tokens > 0


def validate_filename(filename: str) -> bool:
    """Validate that a filename is safe to use.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not filename or filename in [".", ".."]:
        return False
    
    # Check for invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    if re.search(invalid_chars, filename):
        return False
    
    # Check for reserved names on Windows
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    ]
    
    name_without_ext = filename.split(".")[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    return True


def validate_json_string(json_string: str) -> bool:
    """Validate that a string contains valid JSON.
    
    Args:
        json_string: JSON string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        import json
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_regex_pattern(pattern: str) -> bool:
    """Validate that a string is a valid regex pattern.
    
    Args:
        pattern: Regex pattern to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def validate_api_key(api_key: str, min_length: int = 10) -> bool:
    """Validate API key format.
    
    Args:
        api_key: API key to validate
        min_length: Minimum required length
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or len(api_key) < min_length:
        return False
    
    # Check that it contains only valid characters (alphanumeric, hyphens, underscores)
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', api_key))


def validate_language_code(language: str) -> bool:
    """Validate programming language code.
    
    Args:
        language: Language code to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_languages = {
        "python", "javascript", "java", "c", "cpp", "csharp", "go", "rust",
        "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql",
        "html", "css", "xml", "json", "yaml", "markdown", "bash", "shell",
        "powershell", "dockerfile", "makefile", "cmake", "toml", "ini",
    }
    
    return language.lower() in valid_languages