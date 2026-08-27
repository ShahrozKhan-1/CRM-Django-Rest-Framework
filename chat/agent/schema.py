from pydantic import BaseModel, Field


class AddLead(BaseModel):
    name: str = Field(description="Name of the lead")
    email: str = Field(description="Email address of the lead")
    phone: str = Field(description="Phone number of the lead")
    company: str = Field(description="Company of the lead")
    source: str = Field(description="Source of the lead")
    description: str | None = Field(default=None, description="Note or description for the lead")
    assigned_to: str = Field(description="Name of person to assign this lead to.")

class EditLead(BaseModel):
    id: int
    name: str | None = Field(description="Name of the lead")
    email: str | None = Field(description="Email address of the lead")
    phone: str | None = Field(description="Phone number of the lead")
    company: str | None = Field(description="Company of the lead")
    source: str | None = Field(description="Source of the lead")
    description: str | None = Field(default=None, description="Note or description for the lead")
    assigned_to: str | None = Field(description="Name of person to assign this lead to.")