"""Tests for text utilities."""

import pytest

from bungpt.utils.text import (
    format_text,
    truncate_text,
    extract_code_blocks,
    clean_html,
    extract_urls,
    sanitize_filename,
    count_words,
    extract_sentences,
)


def test_format_text():
    """Test text formatting."""
    text = "This is a very long line that should be wrapped to multiple lines when formatting."
    formatted = format_text(text, max_line_length=30)
    
    lines = formatted.split('\n')
    assert all(len(line) <= 30 for line in lines)
    assert len(lines) > 1


def test_truncate_text():
    """Test text truncation."""
    text = "This is a long text that needs to be truncated."
    
    # Test normal truncation
    truncated = truncate_text(text, 20)
    assert len(truncated) == 20
    assert truncated.endswith("...")
    
    # Test text shorter than limit
    short_text = "Short"
    truncated = truncate_text(short_text, 20)
    assert truncated == short_text


def test_extract_code_blocks():
    """Test code block extraction."""
    text = """
    Here's some Python code:
    
    ```python
    def hello():
        print("Hello, world!")
    ```
    
    And some JavaScript:
    
    ```javascript
    console.log("Hello, world!");
    ```
    """
    
    blocks = extract_code_blocks(text)
    
    assert len(blocks) == 2
    assert blocks[0]["language"] == "python"
    assert "def hello():" in blocks[0]["code"]
    assert blocks[1]["language"] == "javascript"
    assert "console.log" in blocks[1]["code"]


def test_clean_html():
    """Test HTML cleaning."""
    html = '<p>This is <strong>bold</strong> text with <a href="#">a link</a>.</p>'
    clean = clean_html(html)
    
    assert clean == "This is bold text with a link."
    assert "<" not in clean
    assert ">" not in clean


def test_extract_urls():
    """Test URL extraction."""
    text = "Visit https://example.com and http://test.org for more info."
    urls = extract_urls(text)
    
    assert len(urls) == 2
    assert "https://example.com" in urls
    assert "http://test.org" in urls


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test with invalid characters
    filename = "test<file>name.txt"
    sanitized = sanitize_filename(filename)
    assert sanitized == "test_file_name.txt"
    
    # Test with empty string
    empty = sanitize_filename("")
    assert empty == "unnamed"
    
    # Test with dots and spaces
    dotted = sanitize_filename("...  file  ...")
    assert not dotted.startswith(".")
    assert not dotted.endswith(".")


def test_count_words():
    """Test word counting."""
    text = "This is a test sentence with seven words."
    count = count_words(text)
    assert count == 8
    
    # Test with extra whitespace
    spaced_text = "  This   has    extra   spaces  "
    count = count_words(spaced_text)
    assert count == 4


def test_extract_sentences():
    """Test sentence extraction."""
    text = "First sentence. Second sentence! Third sentence? Fourth sentence."
    sentences = extract_sentences(text)
    
    assert len(sentences) == 4
    assert "First sentence" in sentences[0]
    assert "Second sentence" in sentences[1]
    assert "Third sentence" in sentences[2]
    assert "Fourth sentence" in sentences[3]