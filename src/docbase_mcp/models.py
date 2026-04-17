from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolInputModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class DocBaseCommandResult(ToolInputModel):
    command: list[str] = Field(
        description=(
            "DocBase CLI arguments that were executed, excluding the executable path "
            "and environment-based authentication values."
        )
    )
    data: Any = Field(description="Parsed JSON payload returned by the DocBase CLI.")


class SearchPostsInput(ToolInputModel):
    query: str | None = Field(
        default=None,
        description="DocBase search query syntax such as 'group:開発 tag:API'.",
    )
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return per page (max 100).",
    )
    summary: bool = Field(
        default=False,
        description="Request summarized body text or the first 1000 characters when supported by the CLI.",
    )


class GetPostInput(ToolInputModel):
    post_id: int = Field(description="DocBase post ID.", ge=1)


class ListCommentsInput(ToolInputModel):
    post_id: int = Field(description="DocBase post ID.", ge=1)
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of comments to return per page (max 100).",
    )
    order: SortOrder = Field(default=SortOrder.ASC, description="Sort order for returned comments.")
    created_after: str | None = Field(
        default=None,
        description="Only include comments created on or after this date, for example '2026-01-01'.",
    )
    created_before: str | None = Field(
        default=None,
        description="Only include comments created on or before this date, for example '2026-01-01'.",
    )


class SearchUsersInput(ToolInputModel):
    query: str | None = Field(
        default=None,
        description="Partial DocBase user name or user ID to search for.",
    )
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Maximum number of users to return per page (max 100).",
    )


class GetUserGroupsInput(ToolInputModel):
    user_id: int = Field(description="Numeric DocBase user ID.", ge=1)
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of groups to return per page (max 100).",
    )


class SearchGroupsInput(ToolInputModel):
    name: str | None = Field(
        default=None,
        description="Exact DocBase group name to match.",
    )
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=100,
        ge=1,
        le=200,
        description="Maximum number of groups to return per page (max 200).",
    )


class GetGroupInput(ToolInputModel):
    group_id: int = Field(description="Numeric DocBase group ID.", ge=1)


class ListGoodJobsInput(ToolInputModel):
    post_id: int = Field(description="DocBase post ID.", ge=1)
    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of good-jobs to return per page (max 500).",
    )
    order: SortOrder = Field(default=SortOrder.ASC, description="Sort order for returned good-jobs.")
    created_after: str | None = Field(
        default=None,
        description="Only include good-jobs created on or after this date, for example '2026-01-01'.",
    )
    created_before: str | None = Field(
        default=None,
        description="Only include good-jobs created on or before this date, for example '2026-01-01'.",
    )
