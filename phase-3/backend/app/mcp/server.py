"""
MCP Server initialization using Official MCP SDK.

This module sets up the Model Context Protocol server that provides
todo management tools to the AI agent.
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from typing import Any
from uuid import UUID
import logging

from .database import get_session
from .tools import TodoTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("todo-mcp-server")


@app.list_tools()
async def list_tools() -> list[dict[str, Any]]:
    """
    List all available MCP tools.

    Returns:
        List of tool definitions with schemas
    """
    return [
        {
            "name": "add_task",
            "description": "Create a new todo task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user creating the task",
                        "format": "uuid"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (1-200 characters)",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description (max 1000 characters)",
                        "maxLength": 1000
                    }
                },
                "required": ["user_id", "title"]
            }
        },
        {
            "name": "list_tasks",
            "description": "List all tasks for the user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user",
                        "format": "uuid"
                    },
                    "is_complete": {
                        "type": "boolean",
                        "description": "Filter by completion status (optional)"
                    }
                },
                "required": ["user_id"]
            }
        },
        {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user",
                        "format": "uuid"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to complete",
                        "format": "uuid"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        },
        {
            "name": "delete_task",
            "description": "Delete a task",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user",
                        "format": "uuid"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to delete",
                        "format": "uuid"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        },
        {
            "name": "update_task",
            "description": "Update a task's title or description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user",
                        "format": "uuid"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to update",
                        "format": "uuid"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (1-200 characters)",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (max 1000 characters)",
                        "maxLength": 1000
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Execute a tool call.

    Args:
        name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        List of content blocks with tool results
    """
    try:
        # Extract user_id from arguments
        user_id_str = arguments.get("user_id")
        if not user_id_str:
            return [{
                "type": "text",
                "text": f"Error: user_id is required for {name}"
            }]

        user_id = UUID(user_id_str)

        # Get database session and create tools instance
        with get_session() as session:
            tools = TodoTools(session=session, user_id=user_id)

            # Route to appropriate tool
            if name == "add_task":
                result = await tools.add_task(
                    title=arguments["title"],
                    description=arguments.get("description")
                )
            elif name == "list_tasks":
                result = await tools.list_tasks(
                    is_complete=arguments.get("is_complete")
                )
            elif name == "complete_task":
                result = await tools.complete_task(
                    task_id=arguments["task_id"]
                )
            elif name == "delete_task":
                result = await tools.delete_task(
                    task_id=arguments["task_id"]
                )
            elif name == "update_task":
                result = await tools.update_task(
                    task_id=arguments["task_id"],
                    title=arguments.get("title"),
                    description=arguments.get("description")
                )
            else:
                return [{
                    "type": "text",
                    "text": f"Error: Unknown tool '{name}'"
                }]

            # Return result as text content
            import json
            return [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]

    except ValueError as e:
        logger.error(f"Validation error in {name}: {e}")
        return [{
            "type": "text",
            "text": f"Validation error: {str(e)}"
        }]
    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return [{
            "type": "text",
            "text": f"Error: {str(e)}"
        }]


async def main():
    """Run the MCP server."""
    logger.info("Starting Todo MCP Server on stdio...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
