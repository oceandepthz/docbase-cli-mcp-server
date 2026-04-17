from __future__ import annotations

import argparse
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from .commands import (
    build_get_current_user_profile_command,
    build_get_group_command,
    build_get_post_command,
    build_get_user_groups_command,
    build_list_comments_command,
    build_list_good_jobs_command,
    build_list_tags_command,
    build_search_groups_command,
    build_search_posts_command,
    build_search_users_command,
)
from .models import (
    DocBaseCommandResult,
    GetGroupInput,
    GetPostInput,
    GetUserGroupsInput,
    ListCommentsInput,
    ListGoodJobsInput,
    SearchGroupsInput,
    SearchPostsInput,
    SearchUsersInput,
)
from .runner import DocBaseCliRunner

mcp = FastMCP("docbase_mcp", json_response=True)
runner = DocBaseCliRunner()

TransportName = Literal["stdio", "streamable-http"]
_DEFAULT_HTTP_HOST = "127.0.0.1"
_DEFAULT_HTTP_PORT = 8000


@dataclass(frozen=True)
class RuntimeOptions:
    transport: TransportName
    host: str
    port: int


def _get_default_transport(environ: Mapping[str, str]) -> TransportName:
    raw_transport = environ.get("DOCBASE_MCP_TRANSPORT", "stdio").strip().lower()
    if raw_transport not in {"stdio", "streamable-http"}:
        raise ValueError("DOCBASE_MCP_TRANSPORT must be either 'stdio' or 'streamable-http'.")
    return raw_transport  # type: ignore[return-value]


def _get_default_port(environ: Mapping[str, str]) -> int:
    raw_port = environ.get("DOCBASE_MCP_PORT")
    if raw_port is None or not raw_port.strip():
        return _DEFAULT_HTTP_PORT
    try:
        return int(raw_port)
    except ValueError as error:
        raise ValueError("DOCBASE_MCP_PORT must be an integer.") from error


def parse_runtime_options(
    argv: Sequence[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> RuntimeOptions:
    effective_environ = os.environ if environ is None else environ
    parser = argparse.ArgumentParser(
        prog="docbase-mcp",
        description="Run the DocBase MCP server over stdio or streamable HTTP.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default=_get_default_transport(effective_environ),
        help="Transport to use. Defaults to DOCBASE_MCP_TRANSPORT or stdio.",
    )
    parser.add_argument(
        "--host",
        default=effective_environ.get("DOCBASE_MCP_HOST", _DEFAULT_HTTP_HOST),
        help="Host to bind for streamable HTTP mode. Defaults to DOCBASE_MCP_HOST or 127.0.0.1.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_get_default_port(effective_environ),
        help="Port to bind for streamable HTTP mode. Defaults to DOCBASE_MCP_PORT or 8000.",
    )
    parsed = parser.parse_args(list(argv) if argv is not None else None)
    return RuntimeOptions(
        transport=parsed.transport,
        host=parsed.host,
        port=parsed.port,
    )


def configure_runtime(server: Any, options: RuntimeOptions) -> None:
    server.settings.host = options.host
    server.settings.port = options.port


def _read_only_annotations(title: str) -> dict[str, bool | str]:
    return {
        "title": title,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }


@mcp.tool(
    name="docbase_search_posts",
    annotations=_read_only_annotations("Search DocBase posts"),
)
async def docbase_search_posts(params: SearchPostsInput) -> DocBaseCommandResult:
    """Search DocBase posts with the official DocBase CLI query syntax."""
    return await runner.run_json(build_search_posts_command(params))


@mcp.tool(
    name="docbase_get_post",
    annotations=_read_only_annotations("Get a DocBase post"),
)
async def docbase_get_post(params: GetPostInput) -> DocBaseCommandResult:
    """Fetch a single DocBase post by numeric post ID."""
    return await runner.run_json(build_get_post_command(params))


@mcp.tool(
    name="docbase_list_comments",
    annotations=_read_only_annotations("List post comments"),
)
async def docbase_list_comments(params: ListCommentsInput) -> DocBaseCommandResult:
    """List comments for a DocBase post."""
    return await runner.run_json(build_list_comments_command(params))


@mcp.tool(
    name="docbase_search_users",
    annotations=_read_only_annotations("Search DocBase users"),
)
async def docbase_search_users(params: SearchUsersInput) -> DocBaseCommandResult:
    """Search DocBase users by partial user name or user ID."""
    return await runner.run_json(build_search_users_command(params))


@mcp.tool(
    name="docbase_get_current_user_profile",
    annotations=_read_only_annotations("Get current user profile"),
)
async def docbase_get_current_user_profile() -> DocBaseCommandResult:
    """Get the authenticated user's DocBase profile."""
    return await runner.run_json(build_get_current_user_profile_command())


@mcp.tool(
    name="docbase_get_user_groups",
    annotations=_read_only_annotations("Get user groups"),
)
async def docbase_get_user_groups(params: GetUserGroupsInput) -> DocBaseCommandResult:
    """Get the groups for a DocBase user. This requires owner or admin permissions."""
    return await runner.run_json(build_get_user_groups_command(params))


@mcp.tool(
    name="docbase_search_groups",
    annotations=_read_only_annotations("Search DocBase groups"),
)
async def docbase_search_groups(params: SearchGroupsInput) -> DocBaseCommandResult:
    """Search DocBase groups by exact group name or list groups with pagination."""
    return await runner.run_json(build_search_groups_command(params))


@mcp.tool(
    name="docbase_get_group",
    annotations=_read_only_annotations("Get a DocBase group"),
)
async def docbase_get_group(params: GetGroupInput) -> DocBaseCommandResult:
    """Fetch a DocBase group by numeric group ID."""
    return await runner.run_json(build_get_group_command(params))


@mcp.tool(
    name="docbase_list_tags",
    annotations=_read_only_annotations("List DocBase tags"),
)
async def docbase_list_tags() -> DocBaseCommandResult:
    """List tags available in the current DocBase team."""
    return await runner.run_json(build_list_tags_command())


@mcp.tool(
    name="docbase_list_good_jobs",
    annotations=_read_only_annotations("List DocBase good-jobs"),
)
async def docbase_list_good_jobs(params: ListGoodJobsInput) -> DocBaseCommandResult:
    """List good-jobs for a DocBase post."""
    return await runner.run_json(build_list_good_jobs_command(params))


def main(argv: Sequence[str] | None = None) -> None:
    options = parse_runtime_options(argv)
    configure_runtime(mcp, options)
    mcp.run(transport=options.transport)
