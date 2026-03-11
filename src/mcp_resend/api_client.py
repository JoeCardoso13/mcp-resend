"""Async HTTP client for Resend API."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError


class ResendAPIError(Exception):
    """Exception raised for Resend API errors."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"Resend API Error {status}: {message}")


class ResendClient:
    """Async client for Resend API."""

    BASE_URL = "https://api.resend.com"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("RESEND_API_KEY")
        if not self.api_key:
            raise ValueError("RESEND_API_KEY is required")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "ResendClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> None:
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-resend/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: Any | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Resend API."""
        await self._ensure_session()
        url = f"{self.BASE_URL}{path}"

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            kwargs: dict[str, Any] = {}
            if json_data is not None:
                kwargs["json"] = json_data
            if params:
                kwargs["params"] = params

            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 204:
                    return {"deleted": True}

                result = await response.json()

                if response.status >= 400:
                    error_msg = "Unknown error"
                    if isinstance(result, dict):
                        if "error" in result:
                            error_obj = result["error"]
                            if isinstance(error_obj, dict):
                                error_msg = error_obj.get("message", str(error_obj))
                            else:
                                error_msg = str(error_obj)
                        elif "message" in result:
                            error_msg = result["message"]

                    raise ResendAPIError(response.status, error_msg, result)

                return result

        except ClientError as e:
            raise ResendAPIError(500, f"Network error: {str(e)}") from e

    # ========================================================================
    # Emails
    # ========================================================================

    async def send_email(
        self,
        from_: str,
        to: list[str],
        subject: str,
        html: str | None = None,
        text: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: list[str] | None = None,
        scheduled_at: str | None = None,
    ) -> dict[str, Any]:
        """Send an email."""
        payload: dict[str, Any] = {
            "from": from_,
            "to": to,
            "subject": subject,
        }
        if html is not None:
            payload["html"] = html
        if text is not None:
            payload["text"] = text
        if cc is not None:
            payload["cc"] = cc
        if bcc is not None:
            payload["bcc"] = bcc
        if reply_to is not None:
            payload["reply_to"] = reply_to
        if scheduled_at is not None:
            payload["scheduled_at"] = scheduled_at
        return await self._request("POST", "/emails", json_data=payload)

    async def get_email(self, email_id: str) -> dict[str, Any]:
        """Get a single email by ID."""
        return await self._request("GET", f"/emails/{email_id}")

    async def list_emails(
        self,
        limit: int = 20,
        after: str | None = None,
        before: str | None = None,
    ) -> dict[str, Any]:
        """List sent emails."""
        return await self._request(
            "GET", "/emails", params={"limit": limit, "after": after, "before": before}
        )

    # ========================================================================
    # Contacts
    # ========================================================================

    async def create_contact(
        self,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        unsubscribed: bool = False,
    ) -> dict[str, Any]:
        """Create a contact."""
        payload: dict[str, Any] = {"email": email, "unsubscribed": unsubscribed}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        return await self._request("POST", "/contacts", json_data=payload)

    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        """Get a single contact by ID."""
        return await self._request("GET", f"/contacts/{contact_id}")

    async def list_contacts(
        self,
        limit: int = 20,
        after: str | None = None,
        before: str | None = None,
        segment_id: str | None = None,
    ) -> dict[str, Any]:
        """List contacts, optionally filtered by segment."""
        params: dict[str, Any] = {"limit": limit, "after": after, "before": before}
        if segment_id:
            params["segment_id"] = segment_id
        return await self._request("GET", "/contacts", params=params)

    async def update_contact(
        self,
        contact_id: str,
        first_name: str | None = None,
        last_name: str | None = None,
        unsubscribed: bool | None = None,
    ) -> dict[str, Any]:
        """Update a contact."""
        payload: dict[str, Any] = {}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        if unsubscribed is not None:
            payload["unsubscribed"] = unsubscribed
        return await self._request("PATCH", f"/contacts/{contact_id}", json_data=payload)

    async def delete_contact(self, contact_id: str) -> dict[str, Any]:
        """Delete a contact."""
        return await self._request("DELETE", f"/contacts/{contact_id}")

    # ========================================================================
    # Segments
    # ========================================================================

    async def list_segments(self) -> dict[str, Any]:
        """List all segments."""
        return await self._request("GET", "/segments")
