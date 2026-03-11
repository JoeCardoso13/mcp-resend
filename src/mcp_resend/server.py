"""Resend MCP Server - FastMCP Implementation."""

import logging
import os
import sys
from importlib.resources import files

from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_resend.api_client import ResendAPIError, ResendClient
from mcp_resend.api_models import (
    Contact,
    ContactCreateResponse,
    ContactListResponse,
    Email,
    EmailListResponse,
    EmailSendResponse,
    SegmentListResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_resend")

SKILL_CONTENT = files("mcp_resend").joinpath("SKILL.md").read_text()

mcp = FastMCP(
    "Resend",
    instructions=(
        "Before using tools, read the skill://resend/usage resource "
        "for tool selection guidance and workflow patterns."
    ),
)

_client: ResendClient | None = None


def get_client() -> ResendClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        api_key = os.environ.get("RESEND_API_KEY")
        if not api_key:
            raise ValueError("RESEND_API_KEY environment variable is required")
        _client = ResendClient(api_key=api_key)
    return _client


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-resend"})


# ============================================================================
# Email Tools
# ============================================================================


@mcp.tool()
async def send_email(
    from_address: str,
    to: list[str],
    subject: str,
    html: str | None = None,
    text: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    reply_to: list[str] | None = None,
    scheduled_at: str | None = None,
    ctx: Context | None = None,
) -> EmailSendResponse:
    """Send an email via Resend.

    Args:
        from_address: Sender email (e.g. "Name <email@domain.com>")
        to: Recipient email addresses (max 50)
        subject: Email subject line
        html: HTML body content
        text: Plain text body (auto-generated from HTML if omitted)
        cc: CC recipients
        bcc: BCC recipients
        reply_to: Reply-to addresses
        scheduled_at: Schedule delivery (ISO 8601 or natural language)
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.send_email(
            from_=from_address,
            to=to,
            subject=subject,
            html=html,
            text=text,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            scheduled_at=scheduled_at,
        )
        return EmailSendResponse(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def get_email(
    email_id: str,
    ctx: Context | None = None,
) -> Email:
    """Get email details including delivery status.

    Args:
        email_id: The email ID to retrieve
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.get_email(email_id)
        return Email(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def list_emails(
    limit: int = 20,
    after: str | None = None,
    before: str | None = None,
    ctx: Context | None = None,
) -> EmailListResponse:
    """List sent emails with pagination.

    Args:
        limit: Max results (1-100, default 20)
        after: Cursor for forward pagination
        before: Cursor for backward pagination
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.list_emails(limit=limit, after=after, before=before)
        return EmailListResponse(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Contact Tools
# ============================================================================


@mcp.tool()
async def create_contact(
    email: str,
    first_name: str | None = None,
    last_name: str | None = None,
    unsubscribed: bool = False,
    ctx: Context | None = None,
) -> ContactCreateResponse:
    """Create a new contact.

    Args:
        email: Contact's email address
        first_name: First name
        last_name: Last name
        unsubscribed: If true, contact won't receive broadcasts
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.create_contact(
            email=email,
            first_name=first_name,
            last_name=last_name,
            unsubscribed=unsubscribed,
        )
        return ContactCreateResponse(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def get_contact(
    contact_id: str,
    ctx: Context | None = None,
) -> Contact:
    """Get a single contact by ID.

    Args:
        contact_id: The contact ID to retrieve
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.get_contact(contact_id)
        return Contact(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def list_contacts(
    limit: int = 20,
    after: str | None = None,
    before: str | None = None,
    segment_id: str | None = None,
    ctx: Context | None = None,
) -> ContactListResponse:
    """List contacts with optional segment filtering.

    Args:
        limit: Max results (1-100, default 20)
        after: Cursor for forward pagination
        before: Cursor for backward pagination
        segment_id: Filter by segment ID
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.list_contacts(
            limit=limit, after=after, before=before, segment_id=segment_id
        )
        return ContactListResponse(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def update_contact(
    contact_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    unsubscribed: bool | None = None,
    ctx: Context | None = None,
) -> dict:
    """Update an existing contact.

    Args:
        contact_id: The contact ID to update
        first_name: New first name
        last_name: New last name
        unsubscribed: New subscription status
        ctx: MCP context
    """
    client = get_client()
    try:
        return await client.update_contact(
            contact_id=contact_id,
            first_name=first_name,
            last_name=last_name,
            unsubscribed=unsubscribed,
        )
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def delete_contact(
    contact_id: str,
    ctx: Context | None = None,
) -> dict:
    """Remove a contact.

    Args:
        contact_id: The contact ID to delete
        ctx: MCP context
    """
    client = get_client()
    try:
        return await client.delete_contact(contact_id)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Segment Tools
# ============================================================================


@mcp.tool()
async def list_segments(
    ctx: Context | None = None,
) -> SegmentListResponse:
    """List all contact segments.

    Args:
        ctx: MCP context
    """
    client = get_client()
    try:
        data = await client.list_segments()
        return SegmentListResponse(**data)
    except ResendAPIError as e:
        if ctx:
            await ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Resources
# ============================================================================


@mcp.resource("skill://resend/usage")
def skill_usage() -> str:
    """Usage guide for the Resend MCP server tools."""
    return SKILL_CONTENT


# ============================================================================
# Entrypoints
# ============================================================================

app = mcp.http_app()

if __name__ == "__main__":
    mcp.run()
