"""
Performance testing script for Todo AI Chatbot API.

This script tests the API's ability to handle concurrent users
and measures response times, throughput, and error rates.
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from uuid import uuid4
import json


class PerformanceTest:
    """
    Performance testing suite for the Todo AI Chatbot API.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize performance test.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []

    async def send_chat_request(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        message: str,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Send a single chat request and measure performance.

        Args:
            session: aiohttp client session
            user_id: UUID of the user
            message: Chat message
            conversation_id: Optional conversation ID

        Returns:
            Dictionary with request results
        """
        url = f"{self.base_url}/api/{user_id}/chat"
        payload = {"message": message}
        if conversation_id:
            payload["conversation_id"] = conversation_id

        start_time = time.time()
        result = {
            "user_id": user_id,
            "message": message,
            "start_time": start_time,
            "success": False,
            "status_code": None,
            "duration": None,
            "error": None
        }

        try:
            async with session.post(url, json=payload) as response:
                result["status_code"] = response.status
                result["success"] = response.status == 200

                if response.status == 200:
                    data = await response.json()
                    result["conversation_id"] = data.get("conversation_id")
                else:
                    result["error"] = await response.text()

        except Exception as e:
            result["error"] = str(e)

        result["duration"] = time.time() - start_time
        return result

    async def simulate_user(
        self,
        session: aiohttp.ClientSession,
        user_id: str,
        num_requests: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simulate a single user making multiple requests.

        Args:
            session: aiohttp client session
            user_id: UUID of the user
            num_requests: Number of requests to make

        Returns:
            List of request results
        """
        messages = [
            "Add a task to buy groceries",
            "Show me all my tasks",
            "Create a reminder to call mom",
            "List my incomplete tasks",
            "Mark the first task as complete"
        ]

        results = []
        conversation_id = None

        for i in range(num_requests):
            message = messages[i % len(messages)]
            result = await self.send_chat_request(
                session, user_id, message, conversation_id
            )
            results.append(result)

            # Use same conversation for subsequent requests
            if result["success"] and not conversation_id:
                conversation_id = result.get("conversation_id")

            # Small delay between requests from same user
            await asyncio.sleep(0.1)

        return results

    async def run_concurrent_users_test(
        self,
        num_users: int = 100,
        requests_per_user: int = 5
    ) -> Dict[str, Any]:
        """
        Run performance test with concurrent users.

        Args:
            num_users: Number of concurrent users to simulate
            requests_per_user: Number of requests each user makes

        Returns:
            Dictionary with test results and statistics
        """
        print(f"\n{'='*60}")
        print(f"Performance Test: {num_users} Concurrent Users")
        print(f"Requests per user: {requests_per_user}")
        print(f"Total requests: {num_users * requests_per_user}")
        print(f"{'='*60}\n")

        start_time = time.time()

        # Create aiohttp session with connection pooling
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Generate unique user IDs
            user_ids = [str(uuid4()) for _ in range(num_users)]

            # Create tasks for all users
            tasks = [
                self.simulate_user(session, user_id, requests_per_user)
                for user_id in user_ids
            ]

            # Run all users concurrently
            print(f"Starting test at {time.strftime('%H:%M:%S')}...")
            all_results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Flatten results
        flat_results = [
            result for user_results in all_results
            for result in user_results
        ]

        # Calculate statistics
        stats = self.calculate_statistics(flat_results, total_time)

        print(f"\nTest completed in {total_time:.2f}s")
        self.print_statistics(stats)

        return stats

    def calculate_statistics(
        self,
        results: List[Dict[str, Any]],
        total_time: float
    ) -> Dict[str, Any]:
        """
        Calculate performance statistics from results.

        Args:
            results: List of request results
            total_time: Total test duration

        Returns:
            Dictionary with statistics
        """
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests

        durations = [r["duration"] for r in results if r["duration"]]

        stats = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "response_times": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "mean": statistics.mean(durations) if durations else 0,
                "median": statistics.median(durations) if durations else 0,
                "p95": statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else 0,
                "p99": statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else 0
            },
            "errors": {}
        }

        # Count error types
        for result in results:
            if not result["success"]:
                error_type = result.get("status_code", "unknown")
                stats["errors"][error_type] = stats["errors"].get(error_type, 0) + 1

        return stats

    def print_statistics(self, stats: Dict[str, Any]):
        """
        Print formatted statistics.

        Args:
            stats: Statistics dictionary
        """
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST RESULTS")
        print(f"{'='*60}")

        print(f"\nRequests:")
        print(f"  Total:      {stats['total_requests']}")
        print(f"  Successful: {stats['successful_requests']}")
        print(f"  Failed:     {stats['failed_requests']}")
        print(f"  Success Rate: {stats['success_rate']:.2f}%")

        print(f"\nThroughput:")
        print(f"  Total Time: {stats['total_time']:.2f}s")
        print(f"  Requests/sec: {stats['requests_per_second']:.2f}")

        print(f"\nResponse Times (seconds):")
        rt = stats['response_times']
        print(f"  Min:    {rt['min']:.3f}s")
        print(f"  Max:    {rt['max']:.3f}s")
        print(f"  Mean:   {rt['mean']:.3f}s")
        print(f"  Median: {rt['median']:.3f}s")
        print(f"  P95:    {rt['p95']:.3f}s")
        print(f"  P99:    {rt['p99']:.3f}s")

        if stats['errors']:
            print(f"\nErrors:")
            for error_type, count in stats['errors'].items():
                print(f"  {error_type}: {count}")

        print(f"\n{'='*60}\n")


async def main():
    """Run performance tests."""
    tester = PerformanceTest()

    # Test 1: 10 concurrent users (warm-up)
    print("\n🔥 Warm-up Test")
    await tester.run_concurrent_users_test(num_users=10, requests_per_user=3)

    # Wait between tests
    await asyncio.sleep(5)

    # Test 2: 50 concurrent users
    print("\n📊 Test 1: 50 Concurrent Users")
    await tester.run_concurrent_users_test(num_users=50, requests_per_user=5)

    # Wait between tests
    await asyncio.sleep(5)

    # Test 3: 100 concurrent users
    print("\n🚀 Test 2: 100 Concurrent Users")
    await tester.run_concurrent_users_test(num_users=100, requests_per_user=5)


if __name__ == "__main__":
    print("Todo AI Chatbot - Performance Testing")
    print("=" * 60)
    print("\nNote: Ensure the API server is running before starting tests")
    print("      Default URL: http://localhost:8000")
    print("\nPress Ctrl+C to cancel\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
