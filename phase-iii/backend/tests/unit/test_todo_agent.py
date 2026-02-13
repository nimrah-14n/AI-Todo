"""
Unit tests for Todo Agent configuration.
RED PHASE: These tests should FAIL until the agent is implemented
"""
import pytest
from src.agents.todo_agent import TodoAgent, get_agent_instructions


def test_agent_initialization():
    """Test that TodoAgent can be initialized with correct configuration"""
    agent = TodoAgent()

    assert agent is not None
    assert hasattr(agent, 'name')
    assert agent.name == "todo-assistant"
    assert hasattr(agent, 'model')
    assert agent.model == "gpt-4o"
    assert hasattr(agent, 'instructions')


def test_agent_instructions_content():
    """Test that agent instructions contain required elements"""
    instructions = get_agent_instructions()

    assert instructions is not None
    assert isinstance(instructions, str)
    assert len(instructions) > 0

    # Check for key instruction elements
    assert "todo" in instructions.lower() or "task" in instructions.lower()
    assert "add" in instructions.lower() or "create" in instructions.lower()
    assert "list" in instructions.lower()
    assert "complete" in instructions.lower()
    assert "delete" in instructions.lower()


def test_agent_has_mcp_tools():
    """Test that agent is configured to use MCP tools"""
    agent = TodoAgent()

    # Agent should have tools configuration
    assert hasattr(agent, 'tools')
    assert agent.tools is not None


def test_agent_model_selection():
    """Test that agent uses the correct OpenAI model"""
    agent = TodoAgent()

    # Should use gpt-4o for best performance
    assert agent.model == "gpt-4o"


def test_agent_instructions_include_tool_usage():
    """Test that instructions guide the agent on when to use tools"""
    instructions = get_agent_instructions()

    # Instructions should mention MCP tools
    assert "tool" in instructions.lower()

    # Should have guidance for each tool
    assert "add_task" in instructions or "create" in instructions.lower()
    assert "list_tasks" in instructions or "show" in instructions.lower()
    assert "complete_task" in instructions or "finish" in instructions.lower()
    assert "delete_task" in instructions or "remove" in instructions.lower()
    assert "update_task" in instructions or "edit" in instructions.lower()


def test_agent_instructions_include_conversation_context():
    """Test that instructions mention using conversation history"""
    instructions = get_agent_instructions()

    # Should mention conversation or context
    assert "conversation" in instructions.lower() or "context" in instructions.lower() or "history" in instructions.lower()
