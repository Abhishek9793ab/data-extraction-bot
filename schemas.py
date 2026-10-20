
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Education(StrictSchema):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class Resume(StrictSchema):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience_summary: Optional[str] = None


class LineItem(StrictSchema):
    description: str
    quantity: float = Field(ge=0)
    unit_price: float = Field(ge=0)
    total: float = Field(ge=0)


class Invoice(StrictSchema):
    invoice_number: Optional[str] = None
    date: Optional[str] = None
    vendor: Optional[str] = None
    customer: Optional[str] = None
    items: List[LineItem] = Field(default_factory=list)
    total_amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = None


SCHEMAS = {
    "Resume": Resume,
    "Invoice": Invoice,
}
