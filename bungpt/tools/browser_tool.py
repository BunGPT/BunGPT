"""Browser tool for web searching and browsing."""

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from bungpt.tools.base_tool import Tool, ToolParameter, ToolResult


class BrowserTool(Tool):
    """Tool for web browsing and searching."""
    
    def __init__(
        self,
        timeout: int = 30,
        max_content_length: int = 50000,
        user_agent: str = "BunGPT/1.0",
        **kwargs: Any,
    ) -> None:
        """Initialize the browser tool.
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to process
            user_agent: User agent string for requests
            **kwargs: Additional configuration
        """
        parameters = [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["search", "open", "find"],
            ),
            ToolParameter(
                name="query",
                type="string",
                description="Search query (for search action)",
            ),
            ToolParameter(
                name="url",
                type="string",
                description="URL to open (for open action)",
            ),
            ToolParameter(
                name="text",
                type="string",
                description="Text to find on page (for find action)",
            ),
        ]
        
        super().__init__(
            name="browser",
            description="Browse the web, search for information, or find text on pages",
            parameters=parameters,
            **kwargs,
        )
        
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_content = ""
        self.current_url = ""
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an HTTP session.
        
        Returns:
            HTTP session
        """
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10),
            )
        
        return self.session
    
    async def _fetch_url(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with status, content, and metadata
        """
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {response.reason}",
                        "url": str(response.url),
                    }
                
                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return {
                        "success": False,
                        "error": f"Unsupported content type: {content_type}",
                        "url": str(response.url),
                    }
                
                # Read content with size limit
                content = await response.text()
                if len(content) > self.max_content_length:
                    content = content[:self.max_content_length] + "... [truncated]"
                
                return {
                    "success": True,
                    "content": content,
                    "url": str(response.url),
                    "title": self._extract_title(content),
                    "status": response.status,
                    "content_type": content_type,
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {self.timeout} seconds",
                "url": url,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "url": url,
            }
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content.
        
        Args:
            html_content: HTML content
            
        Returns:
            Page title
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
        except Exception:
            pass
        
        return "Unknown Title"
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract clean text content from HTML.
        
        Args:
            html_content: HTML content
            
        Returns:
            Clean text content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Failed to extract text content: {e}")
            return html_content
    
    async def _search_web(self, query: str) -> ToolResult:
        """Search the web for information.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        # This is a simplified implementation
        # In practice, you'd integrate with search APIs like Google, Bing, DuckDuckGo, etc.
        
        # Using DuckDuckGo as an example (requires no API key)
        search_url = f"https://duckduckgo.com/html/?q={query}"
        
        result = await self._fetch_url(search_url)
        
        if not result["success"]:
            return ToolResult(
                success=False,
                error=f"Search failed: {result['error']}",
            )
        
        # Parse search results (simplified)
        try:
            soup = BeautifulSoup(result["content"], 'html.parser')
            results = []
            
            # Extract search result links and snippets
            for result_div in soup.find_all('div', class_='result')[:5]:  # Top 5 results
                link_tag = result_div.find('a', class_='result__a')
                snippet_tag = result_div.find('a', class_='result__snippet')
                
                if link_tag:
                    title = link_tag.get_text().strip()
                    url = link_tag.get('href', '')
                    snippet = snippet_tag.get_text().strip() if snippet_tag else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    })
            
            if not results:
                return ToolResult(
                    success=False,
                    error="No search results found",
                )
            
            # Format results
            formatted_results = f"Search results for '{query}':\\n\\n"
            for i, res in enumerate(results, 1):
                formatted_results += f"{i}. {res['title']}\\n"
                formatted_results += f"   URL: {res['url']}\\n"
                if res['snippet']:
                    formatted_results += f"   {res['snippet']}\\n"
                formatted_results += "\\n"
            
            return ToolResult(
                success=True,
                result=formatted_results,
                metadata={
                    "query": query,
                    "results": results,
                    "search_url": search_url,
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to parse search results: {str(e)}",
            )
    
    async def _open_url(self, url: str) -> ToolResult:
        """Open and read content from a URL.
        
        Args:
            url: URL to open
            
        Returns:
            Page content
        """
        result = await self._fetch_url(url)
        
        if not result["success"]:
            return ToolResult(
                success=False,
                error=result["error"],
            )
        
        # Extract and clean text content
        text_content = self._extract_text_content(result["content"])
        
        # Store current content for find operations
        self.current_content = text_content
        self.current_url = result["url"]
        
        # Truncate content if too long
        if len(text_content) > 2000:
            text_content = text_content[:2000] + "... [content truncated]"
        
        return ToolResult(
            success=True,
            result=f"Page: {result['title']}\\nURL: {result['url']}\\n\\nContent:\\n{text_content}",
            metadata={
                "title": result["title"],
                "url": result["url"],
                "content_length": len(self.current_content),
                "status": result["status"],
            },
        )
    
    async def _find_text(self, text: str) -> ToolResult:
        """Find text on the current page.
        
        Args:
            text: Text to find
            
        Returns:
            Search results on the page
        """
        if not self.current_content:
            return ToolResult(
                success=False,
                error="No page is currently open. Use the 'open' action first.",
            )
        
        # Simple text search (case-insensitive)
        text_lower = text.lower()
        content_lower = self.current_content.lower()
        
        if text_lower not in content_lower:
            return ToolResult(
                success=False,
                error=f"Text '{text}' not found on the current page.",
            )
        
        # Find all occurrences and extract context
        occurrences = []
        start = 0
        
        while True:
            pos = content_lower.find(text_lower, start)
            if pos == -1:
                break
            
            # Extract context around the match
            context_start = max(0, pos - 100)
            context_end = min(len(self.current_content), pos + len(text) + 100)
            context = self.current_content[context_start:context_end]
            
            occurrences.append({
                "position": pos,
                "context": context,
            })
            
            start = pos + 1
        
        # Format results
        result_text = f"Found {len(occurrences)} occurrence(s) of '{text}' on {self.current_url}:\\n\\n"
        
        for i, occ in enumerate(occurrences[:3], 1):  # Show first 3 occurrences
            result_text += f"Occurrence {i}:\\n{occ['context']}\\n\\n"
        
        if len(occurrences) > 3:
            result_text += f"... and {len(occurrences) - 3} more occurrence(s)"
        
        return ToolResult(
            success=True,
            result=result_text,
            metadata={
                "search_text": text,
                "occurrences": len(occurrences),
                "url": self.current_url,
            },
        )
    
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the browser tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        action = kwargs["action"]
        
        try:
            if action == "search":
                query = kwargs.get("query")
                if not query:
                    return ToolResult(
                        success=False,
                        error="Query parameter is required for search action",
                    )
                return await self._search_web(query)
            
            elif action == "open":
                url = kwargs.get("url")
                if not url:
                    return ToolResult(
                        success=False,
                        error="URL parameter is required for open action",
                    )
                
                # Add http:// if no scheme is present
                if not urlparse(url).scheme:
                    url = "http://" + url
                
                return await self._open_url(url)
            
            elif action == "find":
                text = kwargs.get("text")
                if not text:
                    return ToolResult(
                        success=False,
                        error="Text parameter is required for find action",
                    )
                return await self._find_text(text)
            
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}",
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Browser tool error: {str(e)}",
            )
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self) -> None:
        """Cleanup when object is destroyed."""
        if self.session and not self.session.closed:
            # Schedule cleanup for the next event loop iteration
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.cleanup())
            except Exception:
                pass  # Event loop might not be available