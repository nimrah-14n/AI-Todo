"""
MCP Server startup script.

Run with: python -m src.mcp

This starts the MCP server on stdio for communication with the OpenAI agent.
"""
import asyncio
import logging
import sys
from .server import main
from .database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr to keep stdout clean for MCP protocol
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        # Initialize database tables
        init_db()

        # Run MCP server
        logger.info("Starting MCP server...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        sys.exit(1)
