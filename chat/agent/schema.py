from pydantic import BaseModel, Field
from enum import Enum


class AddLead(BaseModel):
    name: str = Field(description="Name of the lead")
    email: str = Field(description="Email address of the lead")
    phone: str = Field(description="Phone number of the lead")
    company: str = Field(description="Company of the lead")
    source: str = Field(description="Source of the lead")
    description: str | None = Field(default=None, description="Note or description for the lead")
    assigned_to: str = Field(description="Name of person to assign this lead to.")

class LeadStatus(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    CLOSED_LOST = "Closed_Lost"

class EditLead(BaseModel):
    id: int = Field(description="ID of the lead")
    name: str | None = Field(default=None, description="Name of the lead")
    email: str | None = Field(default=None, description="Email address of the lead")
    phone: str | None = Field(default=None, description="Phone number of the lead")
    company: str | None = Field(default=None, description="Company of the lead")
    source: str | None = Field(default=None, description="Source of the lead")
    status: LeadStatus | None = Field(default=None, description="Lead status. New, Contacted, Qualified, or Closed_Lost.")
    description: str | None = Field(default=None, description="Note or description for the lead")
    assigned_to: str | None = Field(default=None, description="Name of person to assign this lead to.")

class SearchLead(BaseModel):
    name: str | None = Field(default=None, description="Name of the lead")
    email: str | None = Field(default=None, description="Email address of the lead")
    phone: str | None = Field(default=None, description="Phone number of the lead")
    company: str | None = Field(default=None, description="Company of the lead")
    source: str | None = Field(default=None, description="Source of the lead")
    status: LeadStatus | None = Field(default=None, description="Lead status. New, Contacted, Qualified, or Closed_Lost.")

class ConvertLead(BaseModel):
    id: int = Field(description="ID of the qualified lead to convert into a customer and deal.")


class DealStatus(str, Enum):
    OPEN = "Open"
    WON = "Won"
    LOST = "Lost"
    CLOSED = "Closed"

class AddDeal(BaseModel):
    title: str = Field(description="Title or Name of the deal")
    amount: int = Field(description="Monetary amount of the deal.")
    stage: DealStatus = Field(description="Current stage of the deal. Allowed values: Open, Won, Lost, Closed.")
    expected_close_date: str = Field(description="Expected closing date of the deal in YYYY-MM-DD format.")
    description: str | None = Field(default=None, description="Note or description for the deal")
    customer: int = Field(description="ID of the customer associated with this deal.")
    lead: int | None = Field(default=None, description="ID of the lead associated with this deal, if applicable.")

class EditDeal(BaseModel):
    id: int = Field(description="ID of the deal")
    title: str | None = Field(default=None, description="Title or Name of the deal")
    amount: int | None = Field(default=None, description="Monetary amount of the deal.")
    stage: DealStatus | None = Field(default=None, description="Current stage of the deal. Allowed values: Open, Won, Lost, Closed.")
    expected_close_date: str | None = Field(default=None, description="Expected closing date of the deal in YYYY-MM-DD format.")
    description: str | None = Field(default=None, description="Note or description for the deal")
    customer: int | None = Field(default=None, description="ID of the customer associated with this deal.")
    lead: int | None = Field(default=None, description="ID of the lead associated with this deal, if applicable.")


class SearchDeal(BaseModel):
    title: str | None = Field(default=None, description="Title or Name of the deal")
    amount: int | None = Field(default=None, description="Monetary amount of the deal.")
    expected_close_date: str | None = Field(default=None, description="Expected closing date of the deal in YYYY-MM-DD format.")
    customer: int | None = Field(default=None, description="customer associated with this deal.")
    stage: DealStatus | None = Field(default=None, description="deal status. New, Contacted, Qualified, or Closed_Lost.")
    lead: int | None = Field(default=None, description="ID of the lead associated with this deal, if applicable.")


class AddCustomer(BaseModel):
    name: str = Field(description="Name of the customer.")
    email: str = Field(description="Email address of the customer.")
    phone: str = Field(description="Phone number of the customer.")
    company: str = Field(description="Company associated with the customer.")
    lead: int | None = Field(default=None, description="Optional lead ID from which this customer was created.")
    assigned_to: int = Field(description="User ID of the CRM user to assign this customer to.")

class EditCustomer(BaseModel):
    id: int = Field(description="ID of the customer to edit.")
    name: str | None = Field(default=None, description="New name of the customer.")
    email: str | None = Field(default=None, description="New email address of the customer.")
    phone: str | None = Field(default=None, description="New phone number of the customer.")
    company: str | None = Field(default=None, description="Company associated with the customer.")
    lead: int | None = Field(default=None, description="Lead ID associated with the customer.")
    assigned_to: int | None = Field(default=None, description="User ID to assign the customer to.")

class SearchCustomer(BaseModel):
    name: str | None = Field(default=None, description="Customer name to search for.")
    email: str | None = Field(default=None, description="Customer email to search for.")
    phone: str | None = Field(default=None, description="Customer phone number to search for.")
    company: str | None = Field(default=None, description="Company name to filter customers by.")
    lead: int | None = Field(default=None, description="Lead ID to filter customers by.")
    assigned_to: int | None = Field(default=None, description="User ID to filter customers by.")