"""
Smoke test: verify the LLM reads the skill resource and selects the correct tool.

Requires ANTHROPIC_API_KEY and RESEND_API_KEY in environment.
"""

import os

import anthropic
import pytest
from fastmcp import Client

from mcp_resend.server import mcp


def get_anthropic_client() -> anthropic.Anthropic:
    token = os.environ.get("ANTHROPIC_API_KEY")
    if not token:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=token)


async def get_server_context() -> dict:
    """Extract instructions, skill content, and tool definitions from the MCP server."""
    async with Client(mcp) as client:
        init = await client.initialize()
        instructions = init.instructions

        resources = await client.list_resources()
        skill_text = ""
        for r in resources:
            if "skill://" in str(r.uri):
                contents = await client.read_resource(str(r.uri))
                skill_text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])

        tools_list = await client.list_tools()
        tools = []
        for t in tools_list:
            tool_def = {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            tools.append(tool_def)

        return {
            "instructions": instructions,
            "skill": skill_text,
            "tools": tools,
        }


class TestSkillLLMInvocation:
    """Test that an LLM reads the skill and makes correct tool choices."""

    @pytest.mark.asyncio
    async def test_send_email_selected(self):
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Send an email to joe@example.com saying hello"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"
        assert tool_calls[0].name == "send_email"

    @pytest.mark.asyncio
    async def test_list_emails_selected(self):
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Show me my sent emails"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"
        assert tool_calls[0].name == "list_emails"

    @pytest.mark.asyncio
    async def test_create_contact_selected(self):
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Add john@example.com to my contacts"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"
        assert tool_calls[0].name == "create_contact"

    @pytest.mark.asyncio
    async def test_list_contacts_selected(self):
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Show me all my contacts"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"
        assert tool_calls[0].name == "list_contacts"

    @pytest.mark.asyncio
    async def test_delete_contact_selected(self):
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Delete the contact with id abc123"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"
        assert tool_calls[0].name == "delete_contact"
