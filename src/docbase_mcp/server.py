from __future__ import annotations

import argparse
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

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
_LOCAL_ALLOWED_HOSTS = ("127.0.0.1:*", "localhost:*", "[::1]:*")
_LOCAL_ALLOWED_ORIGINS = ("http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*")


@dataclass(frozen=True)
class RuntimeOptions:
    transport: TransportName
    host: str
    port: int
    allowed_hosts: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    disable_dns_rebinding_protection: bool


def _get_default_transport(environ: Mapping[str, str]) -> TransportName:
    raw_transport = environ.get("DOCBASE_MCP_TRANSPORT", "stdio").strip().lower()
    if raw_transport not in {"stdio", "streamable-http"}:
        raise ValueError("DOCBASE_MCP_TRANSPORT must be either 'stdio' or 'streamable-http'.")
    return cast(TransportName, raw_transport)


def _get_default_port(environ: Mapping[str, str]) -> int:
    raw_port = environ.get("DOCBASE_MCP_PORT")
    if raw_port is None or not raw_port.strip():
        return _DEFAULT_HTTP_PORT
    try:
        return int(raw_port)
    except ValueError as error:
        raise ValueError("DOCBASE_MCP_PORT must be an integer.") from error


def _split_csv_values(raw_values: Sequence[str]) -> tuple[str, ...]:
    values: list[str] = []
    for raw_value in raw_values:
        for value in raw_value.split(","):
            normalized = value.strip()
            if normalized and normalized not in values:
                values.append(normalized)
    return tuple(values)


def _get_env_list(environ: Mapping[str, str], variable_name: str) -> tuple[str, ...]:
    raw_value = environ.get(variable_name, "")
    if not raw_value.strip():
        return ()
    return _split_csv_values((raw_value,))


def _get_env_flag(environ: Mapping[str, str], variable_name: str) -> bool:
    raw_value = environ.get(variable_name, "")
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _merge_list_values(
    cli_values: Sequence[str] | None,
    env_values: Sequence[str],
) -> tuple[str, ...]:
    merged = list(env_values)
    if cli_values:
        for value in _split_csv_values(cli_values):
            if value not in merged:
                merged.append(value)
    return tuple(merged)


def _build_transport_security(options: RuntimeOptions) -> TransportSecuritySettings:
    if options.disable_dns_rebinding_protection:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)

    allowed_hosts = list(options.allowed_hosts)
    allowed_origins = list(options.allowed_origins)

    for allowed_host in _LOCAL_ALLOWED_HOSTS:
        if allowed_host not in allowed_hosts:
            allowed_hosts.append(allowed_host)

    for allowed_origin in _LOCAL_ALLOWED_ORIGINS:
        if allowed_origin not in allowed_origins:
            allowed_origins.append(allowed_origin)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


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
    parser.add_argument(
        "--allowed-host",
        action="append",
        default=None,
        help=(
            "Allowed Host header value(s) for streamable HTTP mode. "
            "May be repeated or contain comma-separated entries. "
            "Defaults to DOCBASE_MCP_ALLOWED_HOSTS."
        ),
    )
    parser.add_argument(
        "--allowed-origin",
        action="append",
        default=None,
        help=(
            "Allowed Origin header value(s) for streamable HTTP mode. "
            "May be repeated or contain comma-separated entries. "
            "Defaults to DOCBASE_MCP_ALLOWED_ORIGINS."
        ),
    )
    parser.add_argument(
        "--disable-dns-rebinding-protection",
        action="store_true",
        default=_get_env_flag(effective_environ, "DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION"),
        help=(
            "Disable DNS rebinding protection for trusted environments. "
            "Defaults to DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION."
        ),
    )
    parsed = parser.parse_args(list(argv) if argv is not None else None)
    return RuntimeOptions(
        transport=parsed.transport,
        host=parsed.host,
        port=parsed.port,
        allowed_hosts=_merge_list_values(
            parsed.allowed_host,
            _get_env_list(effective_environ, "DOCBASE_MCP_ALLOWED_HOSTS"),
        ),
        allowed_origins=_merge_list_values(
            parsed.allowed_origin,
            _get_env_list(effective_environ, "DOCBASE_MCP_ALLOWED_ORIGINS"),
        ),
        disable_dns_rebinding_protection=parsed.disable_dns_rebinding_protection,
    )


def configure_runtime(server: Any, options: RuntimeOptions) -> None:
    server.settings.host = options.host
    server.settings.port = options.port
    server.settings.transport_security = _build_transport_security(options)


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
