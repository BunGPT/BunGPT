"""File handling utilities."""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


def safe_read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Safely read a file and return its contents.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        File contents or None if reading failed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        return path.read_text(encoding=encoding)
    except Exception:
        return None


def safe_write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    create_parents: bool = True,
) -> bool:
    """Safely write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding
        create_parents: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding=encoding)
        return True
    except Exception:
        return False


def read_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data or None if reading failed
    """
    content = safe_read_file(file_path)
    if content is None:
        return None
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def write_json_file(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    create_parents: bool = True,
) -> bool:
    """Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write
        indent: JSON indentation
        create_parents: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        return safe_write_file(file_path, content, create_parents=create_parents)
    except Exception:
        return False


def read_yaml_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Read and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Parsed YAML data or None if reading failed
    """
    content = safe_read_file(file_path)
    if content is None:
        return None
    
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        return None


def write_yaml_file(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    create_parents: bool = True,
) -> bool:
    """Write data to a YAML file.
    
    Args:
        file_path: Path to the YAML file
        data: Data to write
        create_parents: Whether to create parent directories
        
    Returns:
        True if successful, False otherwise
    """
    try:
        content = yaml.dump(data, default_flow_style=False, indent=2)
        return safe_write_file(file_path, content, create_parents=create_parents)
    except Exception:
        return False


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
) -> List[Path]:
    """List files in a directory.
    
    Args:
        directory: Directory to search
        pattern: File pattern to match
        recursive: Whether to search recursively
        
    Returns:
        List of file paths
    """
    try:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            return []
        
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))
    except Exception:
        return []


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Copy a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        # Create parent directories if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src_path, dst_path)
        return True
    except Exception:
        return False


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """Move a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        # Create parent directories if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src_path), str(dst_path))
        return True
    except Exception:
        return False


def delete_file(file_path: Union[str, Path]) -> bool:
    """Delete a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
        return True
    except Exception:
        return False


def get_file_size(file_path: Union[str, Path]) -> Optional[int]:
    """Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        path = Path(file_path)
        if path.exists():
            return path.stat().st_size
        return None
    except Exception:
        return None


def ensure_directory(directory: Union[str, Path]) -> bool:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_file_older_than(file_path: Union[str, Path], seconds: int) -> bool:
    """Check if a file is older than a specified number of seconds.
    
    Args:
        file_path: Path to the file
        seconds: Number of seconds
        
    Returns:
        True if file is older than specified seconds, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return True
        
        import time
        file_time = path.stat().st_mtime
        current_time = time.time()
        
        return (current_time - file_time) > seconds
    except Exception:
        return True