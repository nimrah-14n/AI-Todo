"""
Monitoring and metrics collection for the Todo AI Chatbot API.

This module provides utilities for tracking API performance, agent execution,
error rates, and other operational metrics.
"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import time
import asyncio

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and aggregates metrics for monitoring and observability.

    For production, consider integrating with Prometheus, DataDog, or CloudWatch.
    """

    def __init__(self):
        """Initialize metrics collector."""
        # Request metrics
        self.request_count = 0
        self.request_errors = 0
        self.request_durations = []

        # Agent metrics
        self.agent_executions = 0
        self.agent_errors = 0
        self.agent_durations = []
        self.agent_token_usage = {"prompt": 0, "completion": 0, "total": 0}

        # Tool metrics
        self.tool_calls = defaultdict(int)
        self.tool_errors = defaultdict(int)
        self.tool_durations = defaultdict(list)

        # Rate limit metrics
        self.rate_limit_hits = 0

        # Conversation metrics
        self.conversations_created = 0
        self.messages_stored = 0

        # Error tracking
        self.errors_by_type = defaultdict(int)

        # Timestamp for metrics window
        self.window_start = datetime.utcnow()

        logger.info("Metrics collector initialized")

    def record_request(self, duration: float, success: bool = True):
        """
        Record API request metrics.

        Args:
            duration: Request duration in seconds
            success: Whether request was successful
        """
        self.request_count += 1
        self.request_durations.append(duration)

        if not success:
            self.request_errors += 1

        logger.debug(f"Request recorded - Duration: {duration:.3f}s, Success: {success}")

    def record_agent_execution(
        self,
        duration: float,
        success: bool = True,
        token_usage: Optional[Dict[str, int]] = None
    ):
        """
        Record agent execution metrics.

        Args:
            duration: Execution duration in seconds
            success: Whether execution was successful
            token_usage: Optional token usage stats
        """
        self.agent_executions += 1
        self.agent_durations.append(duration)

        if not success:
            self.agent_errors += 1

        if token_usage:
            self.agent_token_usage["prompt"] += token_usage.get("prompt_tokens", 0)
            self.agent_token_usage["completion"] += token_usage.get("completion_tokens", 0)
            self.agent_token_usage["total"] += token_usage.get("total_tokens", 0)

        logger.debug(f"Agent execution recorded - Duration: {duration:.3f}s, Success: {success}")

    def record_tool_call(self, tool_name: str, duration: float, success: bool = True):
        """
        Record MCP tool call metrics.

        Args:
            tool_name: Name of the tool called
            duration: Execution duration in seconds
            success: Whether call was successful
        """
        self.tool_calls[tool_name] += 1
        self.tool_durations[tool_name].append(duration)

        if not success:
            self.tool_errors[tool_name] += 1

        logger.debug(f"Tool call recorded - Tool: {tool_name}, Duration: {duration:.3f}s, Success: {success}")

    def record_rate_limit_hit(self):
        """Record a rate limit hit."""
        self.rate_limit_hits += 1
        logger.debug("Rate limit hit recorded")

    def record_conversation_created(self):
        """Record a new conversation creation."""
        self.conversations_created += 1
        logger.debug("Conversation creation recorded")

    def record_message_stored(self):
        """Record a message stored to database."""
        self.messages_stored += 1

    def record_error(self, error_type: str):
        """
        Record an error occurrence.

        Args:
            error_type: Type/category of error
        """
        self.errors_by_type[error_type] += 1
        logger.debug(f"Error recorded - Type: {error_type}")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected metrics.

        Returns:
            Dictionary with metric summaries
        """
        now = datetime.utcnow()
        window_duration = (now - self.window_start).total_seconds()

        # Calculate request metrics
        avg_request_duration = (
            sum(self.request_durations) / len(self.request_durations)
            if self.request_durations else 0
        )
        p95_request_duration = (
            sorted(self.request_durations)[int(len(self.request_durations) * 0.95)]
            if self.request_durations else 0
        )

        # Calculate agent metrics
        avg_agent_duration = (
            sum(self.agent_durations) / len(self.agent_durations)
            if self.agent_durations else 0
        )

        # Calculate tool metrics
        tool_stats = {}
        for tool_name, durations in self.tool_durations.items():
            avg_duration = sum(durations) / len(durations) if durations else 0
            tool_stats[tool_name] = {
                "calls": self.tool_calls[tool_name],
                "errors": self.tool_errors[tool_name],
                "avg_duration": round(avg_duration, 3),
                "success_rate": (
                    (self.tool_calls[tool_name] - self.tool_errors[tool_name]) /
                    self.tool_calls[tool_name] * 100
                    if self.tool_calls[tool_name] > 0 else 0
                )
            }

        summary = {
            "window": {
                "start": self.window_start.isoformat(),
                "duration_seconds": round(window_duration, 2)
            },
            "requests": {
                "total": self.request_count,
                "errors": self.request_errors,
                "success_rate": (
                    (self.request_count - self.request_errors) / self.request_count * 100
                    if self.request_count > 0 else 0
                ),
                "avg_duration": round(avg_request_duration, 3),
                "p95_duration": round(p95_request_duration, 3),
                "requests_per_second": (
                    self.request_count / window_duration if window_duration > 0 else 0
                )
            },
            "agent": {
                "executions": self.agent_executions,
                "errors": self.agent_errors,
                "success_rate": (
                    (self.agent_executions - self.agent_errors) / self.agent_executions * 100
                    if self.agent_executions > 0 else 0
                ),
                "avg_duration": round(avg_agent_duration, 3),
                "token_usage": self.agent_token_usage
            },
            "tools": tool_stats,
            "rate_limiting": {
                "hits": self.rate_limit_hits
            },
            "conversations": {
                "created": self.conversations_created,
                "messages_stored": self.messages_stored
            },
            "errors": dict(self.errors_by_type)
        }

        return summary

    def reset(self):
        """Reset all metrics (useful for starting a new window)."""
        self.__init__()
        logger.info("Metrics reset")

    async def log_summary_periodically(self, interval_seconds: int = 300):
        """
        Periodically log metrics summary.

        Args:
            interval_seconds: Interval between logs (default: 5 minutes)
        """
        while True:
            await asyncio.sleep(interval_seconds)
            summary = self.get_summary()
            logger.info(f"Metrics Summary: {summary}")


# Global metrics collector instance
metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics
