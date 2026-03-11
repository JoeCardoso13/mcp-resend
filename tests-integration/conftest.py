"""
Shared fixtures and configuration for integration tests.

These tests require a valid RESEND_API_KEY environment variable.
They make real API calls and should not be run in CI without proper setup.
"""

import os

import pytest
import pytest_asyncio

from mcp_resend.api_client import ResendClient


def pytest_configure(config):
    """Check for required environment variables before running tests."""
    if not os.environ.get("RESEND_API_KEY"):
        pytest.exit(
            "ERROR: RESEND_API_KEY environment variable is required.\n"
            "Set it before running integration tests:\n"
            "  export RESEND_API_KEY=your_key_here\n"
            "  make test-integration"
        )


@pytest.fixture
def api_key() -> str:
    """Get the API key from environment."""
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        pytest.skip("RESEND_API_KEY not set")
    return key


@pytest_asyncio.fixture
async def client(api_key: str) -> ResendClient:
    """Create a client for testing."""
    client = ResendClient(api_key=api_key)
    yield client
    await client.close()


# TODO: Add well-known test data constants
# class TestData:
#     """Well-known test data for integration tests."""
#     KNOWN_ID = "abc123"
