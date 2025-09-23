"""Text processing utilities."""

import re
from typing import List, Optional


def format_text(text: str, max_line_length: int = 80) -> str:
    """Format text by wrapping lines and cleaning whitespace.
    
    Args:
        text: Text to format
        max_line_length: Maximum length per line
        
    Returns:
        Formatted text
    """
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Simple word wrapping
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_line_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def extract_code_blocks(text: str) -> List[dict]:
    """Extract code blocks from markdown-formatted text.
    
    Args:
        text: Text containing code blocks
        
    Returns:
        List of code block dictionaries with 'language' and 'code' keys
    """
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            'language': language or 'text',
            'code': code.strip(),
        })
    
    return code_blocks


def clean_html(text: str) -> str:
    """Remove HTML tags from text.
    
    Args:
        text: Text with HTML tags
        
    Returns:
        Clean text without HTML tags
    """
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    clean = re.sub(r'\s+', ' ', clean)
    
    # Decode common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' ',
    }
    
    for entity, char in html_entities.items():
        clean = clean.replace(entity, char)
    
    return clean.strip()


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text.
    
    Args:
        text: Text containing URLs
        
    Returns:
        List of URLs found in the text
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed'
    
    return sanitized


def count_words(text: str) -> int:
    """Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    # Split by whitespace and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)


def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text.
    
    Args:
        text: Text to extract sentences from
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting - could be improved with NLTK
    sentence_endings = r'[.!?]+'
    sentences = re.split(sentence_endings, text)
    
    # Clean up sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences