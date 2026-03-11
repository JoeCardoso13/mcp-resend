"""Unit tests for the Resend API client."""

import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from mcp_resend.api_client import ResendAPIError, ResendClient


@pytest_asyncio.fixture
async def mock_client():
    """Create a ResendClient with mocked session."""
    client = ResendClient(api_key="test_key")
    client._session = AsyncMock()
    yield client
    await client.close()


class TestClientInitialization:
    def test_init_with_explicit_key(self):
        client = ResendClient(api_key="explicit_key")
        assert client.api_key == "explicit_key"

    def test_init_with_env_var(self):
        os.environ["RESEND_API_KEY"] = "env_key"
        try:
            client = ResendClient()
            assert client.api_key == "env_key"
        finally:
            del os.environ["RESEND_API_KEY"]

    def test_init_without_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("RESEND_API_KEY", None)
            with pytest.raises(ValueError, match="RESEND_API_KEY is required"):
                ResendClient()

    def test_custom_timeout(self):
        client = ResendClient(api_key="key", timeout=60.0)
        assert client.timeout == 60.0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with ResendClient(api_key="test") as client:
            assert client._session is not None
        assert client._session is None


class TestClientMethods:
    @pytest.mark.asyncio
    async def test_send_email(self, mock_client):
        mock_response = {"id": "email_123"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.send_email(
                from_="sender@example.com",
                to=["user@example.com"],
                subject="Test",
                html="<p>Hello</p>",
            )
        assert result["id"] == "email_123"

    @pytest.mark.asyncio
    async def test_get_email(self, mock_client):
        mock_response = {"id": "email_123", "last_event": "delivered"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.get_email("email_123")
        assert result["id"] == "email_123"
        assert result["last_event"] == "delivered"

    @pytest.mark.asyncio
    async def test_list_emails(self, mock_client):
        mock_response = {"object": "list", "has_more": False, "data": [{"id": "e1"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_emails(limit=10)
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_create_contact(self, mock_client):
        mock_response = {"object": "contact", "id": "contact_123"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.create_contact(email="user@example.com", first_name="Jane")
        assert result["id"] == "contact_123"

    @pytest.mark.asyncio
    async def test_list_contacts(self, mock_client):
        mock_response = {"object": "list", "has_more": False, "data": [{"id": "c1"}]}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_contacts(limit=10)
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_contacts_with_segment(self, mock_client):
        mock_response = {"object": "list", "has_more": False, "data": []}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.list_contacts(segment_id="seg_1")
        call_args = mock_req.call_args
        assert call_args[1]["params"]["segment_id"] == "seg_1"

    @pytest.mark.asyncio
    async def test_update_contact(self, mock_client):
        mock_response = {"id": "c1", "object": "contact"}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.update_contact("c1", first_name="Updated")
        assert result["id"] == "c1"

    @pytest.mark.asyncio
    async def test_delete_contact(self, mock_client):
        mock_response = {"deleted": True}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.delete_contact("c1")
        assert result["deleted"] is True

    @pytest.mark.asyncio
    async def test_list_segments(self, mock_client):
        mock_response = {
            "object": "list",
            "has_more": False,
            "data": [{"id": "seg_1", "name": "VIPs"}],
        }
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.list_segments()
        assert len(result["data"]) == 1


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_401_unauthorized(self, mock_client):
        with patch.object(
            mock_client,
            "_request",
            side_effect=ResendAPIError(401, "Invalid API key"),
        ):
            with pytest.raises(ResendAPIError) as exc_info:
                await mock_client.list_emails()
            assert exc_info.value.status == 401

    @pytest.mark.asyncio
    async def test_429_rate_limit(self, mock_client):
        with patch.object(
            mock_client,
            "_request",
            side_effect=ResendAPIError(429, "Rate limit exceeded"),
        ):
            with pytest.raises(ResendAPIError) as exc_info:
                await mock_client.list_emails()
            assert exc_info.value.status == 429

    def test_error_string_representation(self):
        err = ResendAPIError(401, "Unauthorized", {"id": "auth_error"})
        assert "401" in str(err)
        assert "Unauthorized" in str(err)
        assert err.details == {"id": "auth_error"}
