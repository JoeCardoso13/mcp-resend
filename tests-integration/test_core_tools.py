"""
Core tools integration tests.

Tests basic API functionality with real API calls against Resend API.
Requires RESEND_API_KEY environment variable.
"""

import time

import pytest

from mcp_resend.api_client import ResendClient


class TestListEmails:
    """Test listing emails."""

    @pytest.mark.asyncio
    async def test_list_emails(self, client: ResendClient):
        result = await client.list_emails(limit=5)
        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)
        print(f"Found {len(result['data'])} emails")


class TestSendAndGetEmail:
    """Test sending an email via Resend sandbox and retrieving it."""

    @pytest.mark.asyncio
    async def test_send_and_get_email(self, client: ResendClient):
        # Send using Resend's sandbox sender
        send_result = await client.send_email(
            from_="onboarding@resend.dev",
            to=["delivered@resend.dev"],
            subject=f"Integration test {int(time.time())}",
            text="This is an automated integration test email.",
        )
        assert "id" in send_result
        email_id = send_result["id"]
        print(f"Sent email: {email_id}")

        # Retrieve it
        email = await client.get_email(email_id)
        assert email["id"] == email_id
        assert email["subject"].startswith("Integration test")
        print(f"Retrieved email: subject={email['subject']}")


class TestContactCRUD:
    """Test contact create -> get -> update -> delete lifecycle."""

    @pytest.mark.asyncio
    async def test_contact_lifecycle(self, client: ResendClient):
        contact_id = None
        test_email = f"integration-test-{int(time.time())}@example.com"
        try:
            # Create
            created = await client.create_contact(
                email=test_email,
                first_name="Integration",
                last_name="Test",
            )
            assert "id" in created
            contact_id = created["id"]
            print(f"Created contact: {contact_id}")

            # Get
            fetched = await client.get_contact(contact_id)
            assert fetched["id"] == contact_id
            assert fetched["email"] == test_email
            print(f"Fetched contact: email={fetched['email']}")

            # Update
            updated = await client.update_contact(
                contact_id,
                first_name="Updated",
            )
            assert isinstance(updated, dict)
            print(f"Updated contact: {contact_id}")

        finally:
            if contact_id:
                await client.delete_contact(contact_id)
                print(f"Deleted contact: {contact_id}")


class TestListContacts:
    """Test listing contacts."""

    @pytest.mark.asyncio
    async def test_list_contacts(self, client: ResendClient):
        result = await client.list_contacts(limit=5)
        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)
        print(f"Found {len(result['data'])} contacts")


class TestListSegments:
    """Test listing segments."""

    @pytest.mark.asyncio
    async def test_list_segments(self, client: ResendClient):
        result = await client.list_segments()
        assert isinstance(result, dict)
        assert "data" in result
        assert isinstance(result["data"], list)
        print(f"Found {len(result['data'])} segments")
