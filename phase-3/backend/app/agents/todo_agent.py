"""
Todo Agent configuration using OpenAI Agents SDK.

This module defines the AI agent that helps users manage their todo tasks
through natural language conversation.
"""
from openai import OpenAI
from typing import Optional
import os


def get_agent_instructions() -> str:
    """
    Get the system instructions for the Todo Agent.

    Returns:
        String containing the agent's instructions
    """
    return """You are a helpful todo task management assistant. Your role is to help users manage their todo tasks through natural language conversation.

You have access to the following MCP tools to manage tasks:

1. **add_task**: Create a new todo task
   - Use when user wants to add, create, or remember something
   - Requires: title (1-200 characters)
   - Optional: description (max 1000 characters)
   - Examples: "Add a task to buy groceries", "Create a reminder to call mom"

2. **list_tasks**: Show all tasks for the user
   - Use when user wants to see, list, or show their tasks
   - Optional filter: is_complete (true/false)
   - Examples: "Show my tasks", "List incomplete tasks", "What do I need to do?"

3. **complete_task**: Mark a task as complete
   - Use when user finishes or completes a task
   - Requires: task_id (UUID)
   - Examples: "Mark 'buy groceries' as done", "I finished the report"

4. **delete_task**: Remove a task
   - Use when user wants to delete or remove a task
   - Requires: task_id (UUID)
   - Examples: "Delete the groceries task", "Remove that reminder"

5. **update_task**: Modify a task's title or description
   - Use when user wants to edit, change, or update a task
   - Requires: task_id (UUID)
   - Optional: title, description
   - Examples: "Change the title to...", "Update the description"

**Important Guidelines:**

- Always use the conversation history and context to understand what the user is referring to
- When a user refers to a task by name (e.g., "the groceries task"), use list_tasks first to find the task_id
- Provide clear, friendly confirmations after each action
- If a task operation fails, explain the error clearly and suggest how to fix it
- Be proactive: if the user's request is ambiguous, ask clarifying questions
- Keep responses concise and conversational

**Conversation Context:**

- You have access to the full conversation history
- Use context to understand references like "that task", "the one I just created", etc.
- Remember what tasks the user has mentioned in the current conversation

Your goal is to make task management feel natural and effortless through conversation."""


class TodoAgent:
    """
    Todo task management agent using OpenAI Agents SDK.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Todo Agent.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: API base URL (defaults to OPENAI_BASE_URL env var, supports Groq)
            model: Model name (defaults to OPENAI_MODEL env var or llama-3.3-70b-versatile)
        """
        self.name = "todo-assistant"
        self.model = model or os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
        self.instructions = get_agent_instructions()

        # Initialize OpenAI client with optional base_url for Groq compatibility
        client_kwargs = {"api_key": api_key or os.getenv("OPENAI_API_KEY")}
        if base_url or os.getenv("OPENAI_BASE_URL"):
            client_kwargs["base_url"] = base_url or os.getenv("OPENAI_BASE_URL")

        self.client = OpenAI(**client_kwargs)

        # MCP tools configuration
        # The actual tool calling will be handled by the Runner with MCP server
        self.tools = "mcp"  # Indicates this agent uses MCP tools

    def get_config(self) -> dict:
        """
        Get the agent configuration for the Runner.

        Returns:
            Dictionary with agent configuration
        """
        return {
            "name": self.name,
            "model": self.model,
            "instructions": self.instructions,
            "tools": self.tools
        }
