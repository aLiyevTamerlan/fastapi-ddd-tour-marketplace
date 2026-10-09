from pydantic import BaseModel

# Fields are deliberately loose (optional strings): the domain validates them and returns its own error codes.


class RegisterAgencyRequest(BaseModel):
    name: str | None = None
    contact_email: str | None = None


class UpdateAgencyRequest(BaseModel):
    """Partial update: omitted fields are left unchanged."""

    name: str | None = None
    contact_email: str | None = None


class RejectAgencyRequest(BaseModel):
    reason: str | None = None
