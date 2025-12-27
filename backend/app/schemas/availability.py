"""
Availability Schemas.

Pydantic schemas for availability API requests and responses.
"""

from datetime import date as date_type
from datetime import datetime
from datetime import time as time_type
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AvailabilityBase(BaseModel):
    """Base schema for availability data."""

    date: date_type = Field(..., description="Date of unavailability")
    reason: str | None = Field(None, max_length=255, description="Optional reason")
    is_all_day: bool = Field(True, description="Whether entire day is unavailable")
    start_time: time_type | None = Field(None, description="Start time if partial day")
    end_time: time_type | None = Field(None, description="End time if partial day")


class AvailabilityCreate(AvailabilityBase):
    """Schema for creating a single availability entry."""

    pass


class AvailabilityResponse(AvailabilityBase):
    """Schema for availability response."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: str = Field(..., description="Availability entry ID")
    member_id: Annotated[str, Field(alias="memberId")] = Field(
        ..., description="Member ID"
    )
    created_at: Annotated[datetime, Field(alias="createdAt")] = Field(
        ..., description="Creation timestamp"
    )


class SetAvailabilitiesRequest(BaseModel):
    """Schema for setting all unavailable dates for a month."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    year: int = Field(..., ge=2020, le=2100, description="Year")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    unavailable_dates: Annotated[list[date_type], Field(alias="unavailableDates")] = (
        Field(..., description="List of dates the member is unavailable")
    )


class MemberAvailabilityResponse(BaseModel):
    """Schema for member availability response for a month."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    member_id: Annotated[str, Field(alias="memberId")] = Field(
        ..., description="Member ID"
    )
    member_name: Annotated[str, Field(alias="memberName")] = Field(
        ..., description="Member's full name"
    )
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month")
    unavailable_dates: Annotated[list[date_type], Field(alias="unavailableDates")] = (
        Field(..., description="List of unavailable dates")
    )


class DepartmentAvailabilityResponse(BaseModel):
    """Schema for department-wide availability response."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    department_id: Annotated[str, Field(alias="departmentId")] = Field(
        ..., description="Department ID"
    )
    department_name: Annotated[str, Field(alias="departmentName")] = Field(
        ..., description="Department name"
    )
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month")
    deadline: date_type = Field(..., description="Submission deadline for this month")
    deadline_passed: Annotated[bool, Field(alias="deadlinePassed")] = Field(
        ..., description="Whether the deadline has passed"
    )
    members: list[MemberAvailabilityResponse] = Field(
        ..., description="Availability for each member"
    )


class AvailabilityDeadlineResponse(BaseModel):
    """Schema for availability deadline information."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    department_id: Annotated[str, Field(alias="departmentId")] = Field(
        ..., description="Department ID"
    )
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month")
    deadline: date_type = Field(..., description="Submission deadline")
    deadline_days: Annotated[int, Field(alias="deadlineDays")] = Field(
        ..., description="Number of days before month for deadline"
    )
    is_past_deadline: Annotated[bool, Field(alias="isPastDeadline")] = Field(
        ..., description="Whether the deadline has passed"
    )
    days_remaining: Annotated[int | None, Field(alias="daysRemaining")] = Field(
        None, description="Days until deadline (null if passed)"
    )
