#!/usr/bin/env python3
"""
Chat example for BunGPT.

This example demonstrates how to create a simple chat interface.
"""

import asyncio
from pathlib import Path

from bungpt.core.config import Config
from bungpt.core.base import Conversation
from bungpt.tools.python_tool import PythonTool
from bungpt.tools.browser_tool import BrowserTool
from bungpt.tools.base_tool import get_tool_registry


class SimpleChatBot:
    """A simple chatbot using BunGPT components."""
    
    def __init__(self):
        """Initialize the chatbot."""
        self.config = Config(
            model_name="chatbot-model",
            device="cpu",
            log_level="INFO",
        )
        
        self.conversation = Conversation()
        self.tool_registry = get_tool_registry()
        
        # Add system message
        self.conversation.add_message(
            "system",
            "You are a helpful assistant with access to Python and web browsing tools."
        )
        
        # Register tools
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up available tools."""
        # Python tool for calculations and code execution
        python_tool = PythonTool()
        self.tool_registry.register(python_tool)
        
        # Browser tool for web searches (simplified for example)
        browser_tool = BrowserTool()
        self.tool_registry.register(browser_tool)
        
        print("Available tools:")
        for tool_name in self.tool_registry.list_tools():
            tool = self.tool_registry.get(tool_name)
            print(f"  - {tool_name}: {tool.description}")
    
    async def process_user_input(self, user_input: str) -> str:
        """Process user input and generate a response.
        
        Args:
            user_input: User's message
            
        Returns:
            Bot's response
        """
        # Add user message to conversation
        self.conversation.add_message("user", user_input)
        
        # Simple rule-based response generation (placeholder for actual model)
        response = await self._generate_response(user_input)
        
        # Add assistant response to conversation
        self.conversation.add_message("assistant", response)
        
        return response
    
    async def _generate_response(self, user_input: str) -> str:
        """Generate a response based on user input.
        
        This is a simplified example. In practice, this would use
        an actual language model for generation.
        
        Args:
            user_input: User's input
            
        Returns:
            Generated response
        """
        input_lower = user_input.lower()
        
        # Handle tool usage requests
        if "calculate" in input_lower or "python" in input_lower:
            return await self._handle_python_request(user_input)
        
        elif "search" in input_lower or "web" in input_lower or "browse" in input_lower:
            return await self._handle_browser_request(user_input)
        
        elif "help" in input_lower:
            return self._get_help_message()
        
        elif "conversation" in input_lower and "history" in input_lower:
            return self._get_conversation_history()
        
        else:
            # Simple conversational responses
            responses = [
                "I understand you're saying: " + user_input,
                "That's interesting! Can you tell me more?",
                "I'd be happy to help you with that. What specifically would you like to know?",
                "Thanks for sharing that with me. Is there anything specific you'd like assistance with?",
            ]
            
            # Simple response selection based on input length
            return responses[len(user_input) % len(responses)]
    
    async def _handle_python_request(self, user_input: str) -> str:
        """Handle Python/calculation requests."""
        # Extract potential Python code or math expressions
        if "factorial" in user_input.lower():
            code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Calculate factorial of 5
result = factorial(5)
print(f"Factorial of 5 = {result}")
"""
            result = await self.tool_registry.execute_tool("python", code=code)
            return f"I'll calculate that for you:\n\n{result.result if result.success else result.error}"
        
        elif any(op in user_input for op in ["+", "-", "*", "/", "**"]):
            # Simple math expression
            code = f"result = {user_input.split()[-1]}\nprint(f'Result: {{result}}')"
            result = await self.tool_registry.execute_tool("python", code=code)
            return f"Calculation result:\n{result.result if result.success else result.error}"
        
        else:
            return "I can help you with Python code and calculations. Could you provide a specific calculation or code to execute?"
    
    async def _handle_browser_request(self, user_input: str) -> str:
        """Handle browser/search requests."""
        # Extract search query
        search_terms = ["search for", "look up", "find information about", "web search"]
        query = user_input
        
        for term in search_terms:
            if term in user_input.lower():
                query = user_input.lower().split(term, 1)[1].strip()
                break
        
        if not query or query == user_input:
            return "What would you like me to search for on the web?"
        
        # Simulate web search (actual implementation would use real search)
        return f"I would search for '{query}' on the web. (Note: This is a simulated response for the example)"
    
    def _get_help_message(self) -> str:
        """Get help message."""
        tools = self.tool_registry.list_tools()
        tool_descriptions = []
        
        for tool_name in tools:
            tool = self.tool_registry.get(tool_name)
            tool_descriptions.append(f"  - {tool_name}: {tool.description}")
        
        return f"""
I'm a helpful assistant with the following capabilities:

Available Tools:
{chr(10).join(tool_descriptions)}

You can ask me to:
- Perform calculations or run Python code
- Search for information on the web
- Have a general conversation
- Show conversation history

Just ask me naturally, and I'll do my best to help!
"""
    
    def _get_conversation_history(self) -> str:
        """Get conversation history."""
        return f"Conversation History:\n\n{self.conversation.to_string()}"


async def main():
    """Main chat loop."""
    print("🤖 BunGPT Chat Example")
    print("=" * 40)
    print("Type 'quit' to exit, 'help' for available commands")
    print()
    
    bot = SimpleChatBot()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Goodbye! Thanks for chatting with me! 👋")
                break
            
            if not user_input:
                continue
            
            # Process input and get response
            print("Bot: ", end="", flush=True)
            response = await bot.process_user_input(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nBot: Sorry, I encountered an error: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())