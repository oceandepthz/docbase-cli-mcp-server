from docbase_mcp.commands import (
    build_list_comments_command,
    build_list_good_jobs_command,
    build_search_posts_command,
)
from docbase_mcp.models import ListCommentsInput, ListGoodJobsInput, SearchPostsInput, SortOrder


def test_build_search_posts_command_omits_query_when_not_set() -> None:
    params = SearchPostsInput(page=2, per_page=25, summary=True)

    assert build_search_posts_command(params) == [
        "posts",
        "search",
        "--page",
        "2",
        "--per-page",
        "25",
        "--summary",
    ]


def test_build_list_comments_command_includes_filters() -> None:
    params = ListCommentsInput(
        post_id=42,
        page=3,
        per_page=50,
        order=SortOrder.DESC,
        created_after="2026-01-01",
        created_before="2026-02-01",
    )

    assert build_list_comments_command(params) == [
        "comments",
        "list",
        "42",
        "--page",
        "3",
        "--per-page",
        "50",
        "--order",
        "desc",
        "--created-after",
        "2026-01-01",
        "--created-before",
        "2026-02-01",
    ]


def test_build_list_good_jobs_command_uses_docbase_order_values() -> None:
    params = ListGoodJobsInput(post_id=7, order=SortOrder.ASC)

    assert build_list_good_jobs_command(params) == [
        "good-jobs",
        "list",
        "7",
        "--page",
        "1",
        "--per-page",
        "100",
        "--order",
        "asc",
    ]
