"""
Agent Runner module for executing the Todo Agent with MCP tools.

This module uses the OpenAI Agents SDK Runner to execute the agent
with access to MCP tools for task management.

Supports both OpenAI and Groq API with automatic function calling format detection.
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
import os
import time
import json
from uuid import UUID

from .groq_parser import parse_groq_function_calls, extract_text_without_functions, has_groq_function_calls

logger = logging.getLogger(__name__)


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get OpenAI function calling format tool definitions for MCP tools.

    Returns:
        List of tool definitions in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new todo task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description (max 1000 characters)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the user, optionally filtered by completion status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_complete": {
                            "type": "boolean",
                            "description": "Filter by completion status: true for completed tasks, false for incomplete tasks, omit for all tasks"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (max 1000 characters)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]


class AgentRunner:
    """
    Runner for executing the Todo Agent with conversation history and tool calling.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Agent Runner.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: API base URL (defaults to OPENAI_BASE_URL env var, supports Groq)
        """
        client_kwargs = {"api_key": api_key or os.getenv("OPENAI_API_KEY")}
        if base_url or os.getenv("OPENAI_BASE_URL"):
            client_kwargs["base_url"] = base_url or os.getenv("OPENAI_BASE_URL")

        self.client = OpenAI(**client_kwargs)
        self.tool_definitions = get_tool_definitions()

    async def execute_tool(
        self,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        user_id: UUID,
        session: Any
    ) -> Dict[str, Any]:
        """
        Execute a tool call using the TodoTools class.

        Args:
            tool_name: Name of the tool to execute
            tool_arguments: Arguments for the tool
            user_id: UUID of the authenticated user
            session: Database session

        Returns:
            Tool execution result
        """
        from ..mcp.tools import TodoTools
        from ..utils.metrics import get_metrics

        metrics = get_metrics()
        tool_start = time.time()

        try:
            logger.info(f"Executing tool: {tool_name} with args: {tool_arguments}")

            # Initialize tools with user context
            tools = TodoTools(session=session, user_id=user_id)

            # Handle None tool_arguments
            if tool_arguments is None:
                tool_arguments = {}

            # Route to appropriate tool
            if tool_name == "add_task":
                result = await tools.add_task(
                    title=tool_arguments.get("title"),
                    description=tool_arguments.get("description")
                )
            elif tool_name == "list_tasks":
                result = await tools.list_tasks(
                    is_complete=tool_arguments.get("is_complete")
                )
            elif tool_name == "complete_task":
                result = await tools.complete_task(
                    task_id=tool_arguments.get("task_id")
                )
            elif tool_name == "delete_task":
                result = await tools.delete_task(
                    task_id=tool_arguments.get("task_id")
                )
            elif tool_name == "update_task":
                result = await tools.update_task(
                    task_id=tool_arguments.get("task_id"),
                    title=tool_arguments.get("title"),
                    description=tool_arguments.get("description")
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            tool_duration = time.time() - tool_start
            metrics.record_tool_call(tool_name, tool_duration, success=True)

            logger.info(f"Tool {tool_name} executed successfully in {tool_duration:.3f}s")
            return result

        except Exception as e:
            tool_duration = time.time() - tool_start
            metrics.record_tool_call(tool_name, tool_duration, success=False)

            logger.error(f"Tool {tool_name} execution failed: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "tool": tool_name
            }

    async def run_async(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        agent_config: Dict[str, Any],
        user_id: UUID,
        session: Any,
        max_iterations: int = 5
    ) -> str:
        """
        Execute the agent asynchronously with conversation history and tool calling.

        Args:
            user_message: The user's current message
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            agent_config: Agent configuration dictionary (name, model, instructions, tools)
            user_id: UUID of the authenticated user
            session: Database session for tool execution
            max_iterations: Maximum number of tool calling iterations (default: 5)

        Returns:
            The agent's response as a string

        Raises:
            Exception: If agent execution fails
        """
        start_time = time.time()

        try:
            logger.info(f"Starting agent execution with tool calling - Model: {agent_config.get('model', 'unknown')}, "
                       f"History length: {len(conversation_history)}, "
                       f"User message length: {len(user_message)} chars")

            # Build messages array with conversation history
            messages = []

            # Add system instructions
            messages.append({
                "role": "system",
                "content": agent_config["instructions"]
            })
            logger.debug(f"Added system instructions: {len(agent_config['instructions'])} chars")

            # Add conversation history
            messages.extend(conversation_history)
            logger.debug(f"Added conversation history: {len(conversation_history)} messages")

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            total_messages = len(messages)
            logger.info(f"Prepared {total_messages} messages for agent execution")

            # Tool calling loop
            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"Tool calling iteration {iteration}/{max_iterations}")

                # Execute agent with OpenAI API and tool definitions
                logger.debug(f"Calling OpenAI API with model: {agent_config['model']}, tools enabled")

                response = self.client.chat.completions.create(
                    model=agent_config["model"],
                    messages=messages,
                    tools=self.tool_definitions,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=1000
                )

                # Log token usage if available
                if hasattr(response, 'usage') and response.usage:
                    logger.info(f"Token usage (iteration {iteration}) - Prompt: {response.usage.prompt_tokens}, "
                               f"Completion: {response.usage.completion_tokens}, "
                               f"Total: {response.usage.total_tokens}")

                assistant_message = response.choices[0].message

                # Check for Groq's XML-like function format in content
                if assistant_message.content and has_groq_function_calls(assistant_message.content):
                    logger.info("Detected Groq function calling format in response")

                    # Parse Groq function calls
                    groq_functions = parse_groq_function_calls(assistant_message.content)

                    if groq_functions:
                        logger.info(f"Parsed {len(groq_functions)} Groq function call(s)")

                        # Extract clean text without function tags
                        clean_text = extract_text_without_functions(assistant_message.content)

                        # Add assistant message to history
                        messages.append({
                            "role": "assistant",
                            "content": clean_text if clean_text else "Let me help you with that."
                        })

                        # Execute each function
                        tool_results = []
                        for func in groq_functions:
                            tool_name = func["name"]
                            tool_arguments = func["arguments"]

                            logger.info(f"Executing Groq function: {tool_name} with args: {tool_arguments}")

                            # Execute the tool
                            tool_result = await self.execute_tool(
                                tool_name=tool_name,
                                tool_arguments=tool_arguments,
                                user_id=user_id,
                                session=session
                            )

                            tool_results.append({
                                "tool": tool_name,
                                "result": tool_result
                            })

                            # Add tool result as a user message for next iteration
                            messages.append({
                                "role": "user",
                                "content": f"Tool {tool_name} result: {json.dumps(tool_result)}"
                            })

                        # Continue to next iteration to get final response
                        continue

                # Check if the model wants to call tools (OpenAI format)
                if assistant_message.tool_calls:
                    logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool call(s)")

                    # Add assistant message with tool calls to history
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                            for tool_call in assistant_message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_arguments = json.loads(tool_call.function.arguments)

                        logger.info(f"Executing tool: {tool_name}")

                        # Execute the tool
                        tool_result = await self.execute_tool(
                            tool_name=tool_name,
                            tool_arguments=tool_arguments,
                            user_id=user_id,
                            session=session
                        )

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })

                        logger.debug(f"Tool {tool_name} result added to conversation")

                    # Continue loop to get final response
                    continue

                else:
                    # No tool calls - we have the final response
                    assistant_response = assistant_message.content

                    if not assistant_response:
                        logger.warning("Assistant returned empty response")
                        assistant_response = "I apologize, but I couldn't process your request. Please try again."

                    execution_time = time.time() - start_time
                    logger.info(f"Agent execution completed successfully after {iteration} iteration(s) - "
                               f"Response length: {len(assistant_response)} chars, "
                               f"Total execution time: {execution_time:.2f}s")

                    return assistant_response

            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached without final response")
            return "I apologize, but I encountered an issue processing your request. Please try rephrasing or breaking it into smaller steps."

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent execution failed after {execution_time:.2f}s - "
                        f"Error: {str(e)}", exc_info=True)
            raise


async def run_agent_with_tools(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    agent_config: Dict[str, Any],
    user_id: str,
    session: Any
) -> str:
    """
    Execute the agent with MCP tools integration.

    This is a higher-level function that handles the full agent execution
    including tool calling through the MCP tools.

    Args:
        user_message: The user's current message
        conversation_history: List of previous messages
        agent_config: Agent configuration
        user_id: UUID of the authenticated user (as string)
        session: Database session for tool execution

    Returns:
        The agent's response as a string
    """
    runner = AgentRunner()

    # Convert user_id string to UUID
    user_uuid = UUID(user_id)

    # Execute agent with tool calling
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config,
        user_id=user_uuid,
        session=session
    )

    return response
