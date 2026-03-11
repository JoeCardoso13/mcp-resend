"""Tests for Resend API models."""

from mcp_resend.api_models import (
    Contact,
    ContactCreateResponse,
    ContactListResponse,
    Email,
    EmailListResponse,
    EmailSendResponse,
    Segment,
    SegmentListResponse,
)


class TestEmailModels:
    def test_email_from_api(self) -> None:
        data = {
            "id": "email_123",
            "to": ["user@example.com"],
            "from": "sender@example.com",
            "subject": "Hello",
            "created_at": "2026-01-01T00:00:00Z",
            "last_event": "delivered",
            "html": "<p>Hi</p>",
            "text": None,
            "bcc": None,
            "cc": None,
            "reply_to": None,
            "scheduled_at": None,
        }
        email = Email(**data)
        assert email.id == "email_123"
        assert email.from_ == "sender@example.com"
        assert email.last_event == "delivered"
        assert email.to == ["user@example.com"]

    def test_email_minimal(self) -> None:
        email = Email(id="e1", **{"from": "a@b.com"})
        assert email.id == "e1"
        assert email.last_event is None

    def test_email_send_response(self) -> None:
        resp = EmailSendResponse(id="email_456")
        assert resp.id == "email_456"

    def test_email_list_response(self) -> None:
        data = {
            "object": "list",
            "has_more": True,
            "data": [
                {
                    "id": "e1",
                    "to": ["a@b.com"],
                    "from": "s@b.com",
                    "subject": "Hi",
                    "created_at": "2026-01-01T00:00:00Z",
                    "last_event": "delivered",
                },
            ],
        }
        resp = EmailListResponse(**data)
        assert len(resp.data) == 1
        assert resp.has_more is True

    def test_email_list_response_empty(self) -> None:
        resp = EmailListResponse()
        assert resp.data == []
        assert resp.has_more is False


class TestContactModels:
    def test_contact_from_api(self) -> None:
        data = {
            "id": "c_123",
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "created_at": "2026-01-01T00:00:00Z",
            "unsubscribed": False,
        }
        contact = Contact(**data)
        assert contact.id == "c_123"
        assert contact.email == "jane@example.com"
        assert contact.unsubscribed is False

    def test_contact_minimal(self) -> None:
        contact = Contact(id="c_1", email="a@b.com")
        assert contact.first_name is None
        assert contact.unsubscribed is False

    def test_contact_create_response(self) -> None:
        resp = ContactCreateResponse(id="c_new")
        assert resp.id == "c_new"
        assert resp.object == "contact"

    def test_contact_list_response(self) -> None:
        data = {
            "object": "list",
            "has_more": False,
            "data": [{"id": "c_1", "email": "a@b.com", "created_at": "2026-01-01T00:00:00Z"}],
        }
        resp = ContactListResponse(**data)
        assert len(resp.data) == 1


class TestSegmentModels:
    def test_segment_from_api(self) -> None:
        seg = Segment(id="seg_1", name="VIPs", created_at="2026-01-01T00:00:00Z")
        assert seg.id == "seg_1"
        assert seg.name == "VIPs"

    def test_segment_list_response(self) -> None:
        data = {
            "object": "list",
            "has_more": False,
            "data": [{"id": "seg_1", "name": "VIPs", "created_at": "2026-01-01T00:00:00Z"}],
        }
        resp = SegmentListResponse(**data)
        assert len(resp.data) == 1
        assert resp.data[0].name == "VIPs"
