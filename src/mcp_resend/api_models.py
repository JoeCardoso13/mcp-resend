"""Pydantic models for Resend API responses."""

from pydantic import BaseModel, Field

# ============================================================================
# Email Models
# ============================================================================


class Email(BaseModel):
    """A sent email."""

    id: str = Field(..., description="Email ID")
    to: list[str] = Field(default_factory=list, description="Recipient addresses")
    from_: str = Field(..., alias="from", description="Sender address")
    subject: str = Field("", description="Email subject")
    created_at: str = Field("", alias="created_at", description="Created timestamp")
    last_event: str | None = Field(
        None, description="Last delivery event (e.g. delivered, bounced)"
    )
    html: str | None = Field(None, description="HTML content")
    text: str | None = Field(None, description="Plain text content")
    bcc: list[str] | None = Field(None, description="BCC recipients")
    cc: list[str] | None = Field(None, description="CC recipients")
    reply_to: list[str] | None = Field(None, description="Reply-to addresses")
    scheduled_at: str | None = Field(None, description="Scheduled send time")


class EmailSendResponse(BaseModel):
    """Response from sending an email."""

    id: str = Field(..., description="Email ID")


class EmailListResponse(BaseModel):
    """Response for listing emails."""

    object: str = "list"
    has_more: bool = Field(default=False)
    data: list[Email] = Field(default_factory=list)


# ============================================================================
# Contact Models
# ============================================================================


class Contact(BaseModel):
    """A contact."""

    id: str = Field(..., description="Contact ID")
    email: str = Field(..., description="Email address")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    created_at: str = Field("", description="Created timestamp")
    unsubscribed: bool = Field(default=False, description="Global unsubscribe status")


class ContactCreateResponse(BaseModel):
    """Response from creating a contact."""

    object: str = "contact"
    id: str = Field(..., description="Contact ID")


class ContactListResponse(BaseModel):
    """Response for listing contacts."""

    object: str = "list"
    has_more: bool = Field(default=False)
    data: list[Contact] = Field(default_factory=list)


# ============================================================================
# Segment Models
# ============================================================================


class Segment(BaseModel):
    """A contact segment."""

    id: str = Field(..., description="Segment ID")
    name: str = Field(..., description="Segment name")
    created_at: str = Field("", description="Created timestamp")


class SegmentListResponse(BaseModel):
    """Response for listing segments."""

    object: str = "list"
    has_more: bool = Field(default=False)
    data: list[Segment] = Field(default_factory=list)
