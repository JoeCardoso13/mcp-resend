"""Shared fixtures for unit tests."""

from unittest.mock import AsyncMock

import pytest

from mcp_resend.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    client = AsyncMock()
    client.send_email = AsyncMock(return_value={"id": "email_123"})
    client.get_email = AsyncMock(
        return_value={
            "id": "email_123",
            "object": "email",
            "to": ["user@example.com"],
            "from": "sender@example.com",
            "subject": "Test",
            "created_at": "2026-01-01T00:00:00Z",
            "last_event": "delivered",
            "html": "<p>Hello</p>",
            "text": None,
            "bcc": None,
            "cc": None,
            "reply_to": None,
            "scheduled_at": None,
        }
    )
    client.list_emails = AsyncMock(
        return_value={
            "object": "list",
            "has_more": False,
            "data": [
                {
                    "id": "email_1",
                    "to": ["a@example.com"],
                    "from": "sender@example.com",
                    "subject": "First",
                    "created_at": "2026-01-01T00:00:00Z",
                    "last_event": "delivered",
                },
            ],
        }
    )
    client.create_contact = AsyncMock(return_value={"object": "contact", "id": "contact_123"})
    client.get_contact = AsyncMock(
        return_value={
            "id": "contact_123",
            "email": "user@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "created_at": "2026-01-01T00:00:00Z",
            "unsubscribed": False,
        }
    )
    client.list_contacts = AsyncMock(
        return_value={
            "object": "list",
            "has_more": False,
            "data": [
                {
                    "id": "contact_1",
                    "email": "a@example.com",
                    "first_name": "Alice",
                    "last_name": None,
                    "created_at": "2026-01-01T00:00:00Z",
                    "unsubscribed": False,
                },
            ],
        }
    )
    client.update_contact = AsyncMock(return_value={"id": "contact_123", "object": "contact"})
    client.delete_contact = AsyncMock(return_value={"deleted": True})
    client.list_segments = AsyncMock(
        return_value={
            "object": "list",
            "has_more": False,
            "data": [
                {"id": "seg_1", "name": "VIPs", "created_at": "2026-01-01T00:00:00Z"},
            ],
        }
    )
    return client
