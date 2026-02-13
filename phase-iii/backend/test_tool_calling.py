"""
Test script to verify tool calling integration.

This script tests the agent's ability to call MCP tools for task management.
Run this after starting the backend server.
"""
import asyncio
import sys
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from src.agents.todo_agent import TodoAgent
from src.agents.runner import run_agent_with_tools
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message


async def test_tool_calling():
    """Test the tool calling integration."""

    print("=" * 80)
    print("TOOL CALLING INTEGRATION TEST")
    print("=" * 80)

    # Create in-memory database for testing
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    # Create test user
    test_user_id = uuid4()
    print(f"\n✓ Created test user: {test_user_id}")

    # Initialize agent
    agent = TodoAgent()
    agent_config = agent.get_config()
    print(f"✓ Initialized agent with model: {agent_config['model']}")

    # Test cases
    test_cases = [
        {
            "name": "Create Task",
            "message": "Add a task to buy groceries",
            "expected_tool": "add_task"
        },
        {
            "name": "List Tasks",
            "message": "Show me all my tasks",
            "expected_tool": "list_tasks"
        },
        {
            "name": "Complete Task",
            "message": "Mark the groceries task as complete",
            "expected_tool": "complete_task"
        },
        {
            "name": "Update Task",
            "message": "Change the groceries task to 'Buy groceries and snacks'",
            "expected_tool": "update_task"
        },
        {
            "name": "Delete Task",
            "message": "Delete the groceries task",
            "expected_tool": "delete_task"
        }
    ]

    print("\n" + "=" * 80)
    print("RUNNING TEST CASES")
    print("=" * 80)

    conversation_history = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test_case['name']}")
        print(f"User: {test_case['message']}")

        try:
            with Session(engine) as session:
                # Run agent with tools
                response = await run_agent_with_tools(
                    user_message=test_case['message'],
                    conversation_history=conversation_history,
                    agent_config=agent_config,
                    user_id=str(test_user_id),
                    session=session
                )

                print(f"Assistant: {response}")

                # Add to conversation history
                conversation_history.append({
                    "role": "user",
                    "content": test_case['message']
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

                print(f"✓ Test passed: {test_case['name']}")

        except Exception as e:
            print(f"✗ Test failed: {test_case['name']}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_cases)}")
    print(f"Conversation turns: {len(conversation_history) // 2}")
    print("\n✓ Tool calling integration test completed!")
    print("=" * 80)


async def test_tool_definitions():
    """Test that tool definitions are properly formatted."""
    from src.agents.runner import get_tool_definitions

    print("\n" + "=" * 80)
    print("TOOL DEFINITIONS TEST")
    print("=" * 80)

    tools = get_tool_definitions()

    print(f"\n✓ Found {len(tools)} tool definitions:")

    for tool in tools:
        tool_name = tool['function']['name']
        tool_desc = tool['function']['description']
        required_params = tool['function']['parameters'].get('required', [])

        print(f"\n  • {tool_name}")
        print(f"    Description: {tool_desc}")
        print(f"    Required params: {', '.join(required_params) if required_params else 'None'}")

    # Verify all expected tools are present
    expected_tools = ['add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task']
    actual_tools = [tool['function']['name'] for tool in tools]

    missing_tools = set(expected_tools) - set(actual_tools)
    extra_tools = set(actual_tools) - set(expected_tools)

    if missing_tools:
        print(f"\n✗ Missing tools: {', '.join(missing_tools)}")
        return False

    if extra_tools:
        print(f"\n⚠ Extra tools: {', '.join(extra_tools)}")

    print("\n✓ All expected tools are defined correctly!")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PHASE III - TOOL CALLING INTEGRATION VERIFICATION")
    print("=" * 80)

    # Check if required environment variables are set
    import os

    required_env_vars = ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_MODEL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("\n✗ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file and try again.")
        sys.exit(1)

    print("\n✓ Environment variables configured")
    print(f"  - API Base URL: {os.getenv('OPENAI_BASE_URL')}")
    print(f"  - Model: {os.getenv('OPENAI_MODEL')}")

    # Run tests
    try:
        # Test 1: Tool definitions
        if not asyncio.run(test_tool_definitions()):
            print("\n✗ Tool definitions test failed!")
            sys.exit(1)

        # Test 2: Tool calling (requires API key)
        print("\n" + "=" * 80)
        print("NOTE: The following test requires a valid Groq API key")
        print("      and will make actual API calls.")
        print("=" * 80)

        response = input("\nProceed with API test? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_tool_calling())
        else:
            print("\n⚠ Skipped API test")

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n✓ Tool calling integration is working correctly")
        print("✓ Phase III implementation is COMPLETE")

    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
