"""
Groq function calling parser for handling Groq's XML-like function format.

Groq's LLaMA models return function calls in this format:
<function=function_name={"arg1": "value1", "arg2": "value2"}</function>

This module parses that format and converts it to standard tool calls.
"""
import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def parse_groq_function_calls(content: str) -> List[Dict[str, Any]]:
    """
    Parse Groq's XML-like function calling format.

    Format: <function=function_name={"arg1": "value1"}</function>

    Args:
        content: The assistant's response content

    Returns:
        List of parsed function calls with name and arguments
    """
    if not content:
        return []

    # Pattern to match Groq's function format
    # <function=function_name={"args": "values"}</function>
    pattern = r'<function=([^=]+)=(\{[^}]+\})</function>'

    matches = re.findall(pattern, content)

    if not matches:
        return []

    function_calls = []
    for match in matches:
        function_name = match[0].strip()
        try:
            arguments = json.loads(match[1])
            function_calls.append({
                "name": function_name,
                "arguments": arguments
            })
            logger.info(f"Parsed Groq function call: {function_name}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse function arguments: {match[1]} - {e}")
            continue

    return function_calls


def extract_text_without_functions(content: str) -> str:
    """
    Remove function call tags from content and return clean text.

    Args:
        content: The assistant's response content

    Returns:
        Clean text without function tags
    """
    if not content:
        return ""

    # Remove all <function=...></function> tags
    pattern = r'<function=[^>]+</function>'
    clean_text = re.sub(pattern, '', content)

    return clean_text.strip()


def has_groq_function_calls(content: str) -> bool:
    """
    Check if content contains Groq function calls.

    Args:
        content: The assistant's response content

    Returns:
        True if content has function calls
    """
    if not content:
        return False

    pattern = r'<function='
    return bool(re.search(pattern, content))
