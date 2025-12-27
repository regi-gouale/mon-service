"""
Planning Schemas.

Pydantic schemas for planning-related requests and responses.
"""

from datetime import date as date_type
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Service Schemas
# ============================================================================


class RequiredRole(BaseModel):
    """Schema for a required role."""

    role: str = Field(..., description="Role name (e.g., 'musicien', 'technicien')")
    count: int = Field(1, ge=1, description="Number of members needed for this role")


class ServiceBase(BaseModel):
    """Base schema for service."""

    name: str = Field(..., min_length=1, max_length=255)
    service_type: str = Field(..., min_length=1, max_length=100)
    date: date_type = Field(..., description="Service date")
    start_time: time = Field(..., description="Start time")
    end_time: time | None = Field(None, description="End time (optional)")
    location: str | None = Field(None, max_length=255)
    dress_code_id: str | None = Field(None, description="UUID of dress code")
    required_roles: list[RequiredRole] = Field(
        default_factory=list, description="Roles required for this service"
    )
    notes: str | None = Field(None)
    is_recurring: bool = Field(False)
    recurrence_rule: str | None = Field(None, max_length=255)


class ServiceCreate(ServiceBase):
    """Schema for creating a service."""

    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service."""

    name: str | None = Field(None, min_length=1, max_length=255)
    service_type: str | None = Field(None, min_length=1, max_length=100)
    date: date_type | None = None
    start_time: time | None = None
    end_time: time | None = None
    location: str | None = None
    dress_code_id: str | None = None
    required_roles: list[RequiredRole] | None = None
    notes: str | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None


class ServiceResponse(ServiceBase):
    """Schema for service response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    department_id: str
    created_at: datetime
    updated_at: datetime
    created_by: str


# ============================================================================
# Planning Schemas
# ============================================================================


class PlanningCreate(BaseModel):
    """Schema for creating a planning."""

    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)


class PlanningResponse(BaseModel):
    """Schema for planning response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    department_id: str
    month: date_type
    status: str
    confidence_score: float | None = None
    generated_at: datetime | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str


class PlanningWithAssignmentsResponse(PlanningResponse):
    """Planning response with assignments."""

    assignments: list["AssignmentResponse"] = []


class GenerationWeights(BaseModel):
    """Schema for custom generation weights."""

    equity: float = Field(
        0.40, ge=0, le=1, description="Weight for equity (fair distribution)"
    )
    skills: float = Field(0.30, ge=0, le=1, description="Weight for skill matching")
    recency: float = Field(0.20, ge=0, le=1, description="Weight for recency")
    random: float = Field(0.10, ge=0, le=1, description="Weight for randomness")


class GenerateRequest(BaseModel):
    """Schema for generate planning request."""

    weights: GenerationWeights | None = Field(
        None, description="Custom weights for the generation algorithm"
    )


class ConflictInfo(BaseModel):
    """Schema for a generation conflict."""

    service_id: str
    service_name: str
    service_date: str
    role: str
    required: int
    available: int
    reason: str


class GenerationResultResponse(BaseModel):
    """Schema for generation result response."""

    assignments_count: int
    confidence_score: float
    conflicts: list[ConflictInfo]
    warnings: list[str]


# ============================================================================
# Assignment Schemas
# ============================================================================


class AssignmentCreate(BaseModel):
    """Schema for creating an assignment."""

    service_id: str
    member_id: str
    assigned_role: str = Field(..., min_length=1, max_length=100)


class AssignmentResponse(BaseModel):
    """Schema for assignment response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    planning_id: str
    service_id: str
    member_id: str
    assigned_role: str
    status: str
    confirmed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class AssignmentWithDetailsResponse(AssignmentResponse):
    """Assignment response with member and service details."""

    member_name: str | None = None
    service_name: str | None = None
    service_date: date_type | None = None
    service_start_time: time | None = None


class AssignmentStatusUpdate(BaseModel):
    """Schema for updating assignment status."""

    action: str = Field(..., pattern="^(confirm|decline)$")
    notes: str | None = None


# ============================================================================
# List Responses
# ============================================================================


class ServiceListResponse(BaseModel):
    """Schema for service list response."""

    services: list[ServiceResponse]
    total: int


class PlanningListResponse(BaseModel):
    """Schema for planning list response."""

    plannings: list[PlanningResponse]
    total: int


class AssignmentListResponse(BaseModel):
    """Schema for assignment list response."""

    assignments: list[AssignmentResponse]
    total: int
