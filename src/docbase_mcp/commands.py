from __future__ import annotations

from .models import (
    GetGroupInput,
    GetPostInput,
    GetUserGroupsInput,
    ListCommentsInput,
    ListGoodJobsInput,
    SearchGroupsInput,
    SearchPostsInput,
    SearchUsersInput,
)


def _add_option(arguments: list[str], flag: str, value: object | None) -> None:
    if value is None:
        return
    arguments.extend([flag, str(value)])


def _add_flag(arguments: list[str], flag: str, enabled: bool) -> None:
    if enabled:
        arguments.append(flag)


def build_search_posts_command(params: SearchPostsInput) -> list[str]:
    arguments = ["posts", "search"]
    _add_option(arguments, "--query", params.query)
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    _add_flag(arguments, "--summary", params.summary)
    return arguments


def build_get_post_command(params: GetPostInput) -> list[str]:
    return ["posts", "get", str(params.post_id)]


def build_list_comments_command(params: ListCommentsInput) -> list[str]:
    arguments = ["comments", "list", str(params.post_id)]
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    _add_option(arguments, "--order", params.order.value)
    _add_option(arguments, "--created-after", params.created_after)
    _add_option(arguments, "--created-before", params.created_before)
    return arguments


def build_search_users_command(params: SearchUsersInput) -> list[str]:
    arguments = ["users", "search"]
    _add_option(arguments, "--query", params.query)
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    return arguments


def build_get_current_user_profile_command() -> list[str]:
    return ["users", "get-profile"]


def build_get_user_groups_command(params: GetUserGroupsInput) -> list[str]:
    arguments = ["users", "get-groups", str(params.user_id)]
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    return arguments


def build_search_groups_command(params: SearchGroupsInput) -> list[str]:
    arguments = ["groups", "search"]
    _add_option(arguments, "--name", params.name)
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    return arguments


def build_get_group_command(params: GetGroupInput) -> list[str]:
    return ["groups", "get", str(params.group_id)]


def build_list_tags_command() -> list[str]:
    return ["tags", "list"]


def build_list_good_jobs_command(params: ListGoodJobsInput) -> list[str]:
    arguments = ["good-jobs", "list", str(params.post_id)]
    _add_option(arguments, "--page", params.page)
    _add_option(arguments, "--per-page", params.per_page)
    _add_option(arguments, "--order", params.order.value)
    _add_option(arguments, "--created-after", params.created_after)
    _add_option(arguments, "--created-before", params.created_before)
    return arguments
