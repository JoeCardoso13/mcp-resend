"""Tests for Resend MCP Server tools and skill resource."""

from unittest.mock import patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_resend.api_client import ResendAPIError
from mcp_resend.server import SKILL_CONTENT


class TestSkillResource:
    @pytest.mark.asyncio
    async def test_initialize_returns_instructions(self, mcp_server):
        async with Client(mcp_server) as client:
            result = await client.initialize()
            assert result.instructions is not None
            assert "skill://resend/usage" in result.instructions

    @pytest.mark.asyncio
    async def test_skill_resource_listed(self, mcp_server):
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            uris = [str(r.uri) for r in resources]
            assert "skill://resend/usage" in uris

    @pytest.mark.asyncio
    async def test_skill_resource_readable(self, mcp_server):
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://resend/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert "send_email" in text

    @pytest.mark.asyncio
    async def test_skill_content_matches_constant(self, mcp_server):
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://resend/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert text == SKILL_CONTENT


class TestToolListing:
    @pytest.mark.asyncio
    async def test_all_tools_listed(self, mcp_server):
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            names = {t.name for t in tools}
            expected = {
                "send_email",
                "get_email",
                "list_emails",
                "create_contact",
                "get_contact",
                "list_contacts",
                "update_contact",
                "delete_contact",
                "list_segments",
            }
            assert expected == names


class TestEmailTools:
    @pytest.mark.asyncio
    async def test_send_email(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "send_email",
                    {
                        "from_address": "sender@example.com",
                        "to": ["user@example.com"],
                        "subject": "Test",
                        "html": "<p>Hello</p>",
                    },
                )
            assert result is not None
            mock_client.send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_email(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_email", {"email_id": "email_123"})
            assert result is not None
            mock_client.get_email.assert_called_once_with("email_123")

    @pytest.mark.asyncio
    async def test_list_emails(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_emails", {"limit": 10})
            assert result is not None
            mock_client.list_emails.assert_called_once_with(limit=10, after=None, before=None)


class TestContactTools:
    @pytest.mark.asyncio
    async def test_create_contact(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "create_contact",
                    {"email": "new@example.com", "first_name": "Jane"},
                )
            assert result is not None
            mock_client.create_contact.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("get_contact", {"contact_id": "contact_123"})
            assert result is not None
            mock_client.get_contact.assert_called_once_with("contact_123")

    @pytest.mark.asyncio
    async def test_list_contacts(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_contacts", {"limit": 5})
            assert result is not None

    @pytest.mark.asyncio
    async def test_delete_contact(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("delete_contact", {"contact_id": "c1"})
            assert result is not None
            mock_client.delete_contact.assert_called_once_with("c1")


class TestSegmentTools:
    @pytest.mark.asyncio
    async def test_list_segments(self, mcp_server, mock_client):
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("list_segments", {})
            assert result is not None
            mock_client.list_segments.assert_called_once()


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_send_email_api_error(self, mcp_server, mock_client):
        mock_client.send_email.side_effect = ResendAPIError(401, "Unauthorized")
        with patch("mcp_resend.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                with pytest.raises(ToolError, match="401"):
                    await client.call_tool(
                        "send_email",
                        {
                            "from_address": "s@b.com",
                            "to": ["a@b.com"],
                            "subject": "Fail",
                        },
                    )
