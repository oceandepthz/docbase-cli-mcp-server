from __future__ import annotations

import shlex
from collections.abc import Sequence

_INSTALL_HINT = (
    "Install the DocBase CLI with "
    "`npm install --ignore-scripts -g @krayinc/docbase-cli` and restart the MCP client."
)


def _format_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _truncate_output(text: str, limit: int = 600) -> str:
    normalized = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


class DocBaseCliError(RuntimeError):
    """Base class for actionable DocBase CLI wrapper errors."""


class MissingEnvironmentVariableError(DocBaseCliError):
    def __init__(self, variable_name: str) -> None:
        super().__init__(
            f"Missing required environment variable `{variable_name}`. "
            f"Configure `{variable_name}` in the MCP client's `env` block before starting this server."
        )


class DocBaseExecutableNotFoundError(DocBaseCliError):
    def __init__(self) -> None:
        super().__init__(f"Could not find the `docbase` executable in PATH. {_INSTALL_HINT}")


class DocBaseCommandTimeoutError(DocBaseCliError):
    def __init__(self, command: Sequence[str], timeout_seconds: float) -> None:
        super().__init__(
            f"DocBase CLI command `{_format_command(command)}` timed out after {timeout_seconds:.0f} seconds."
        )


class DocBaseCommandFailedError(DocBaseCliError):
    def __init__(
        self,
        *,
        command: Sequence[str],
        exit_code: int,
        stdout: str,
        stderr: str,
    ) -> None:
        details: list[str] = []
        if stderr.strip():
            details.append(f"stderr: {_truncate_output(stderr)}")
        if stdout.strip():
            details.append(f"stdout: {_truncate_output(stdout)}")
        detail_suffix = f" {' | '.join(details)}" if details else ""
        super().__init__(
            f"DocBase CLI command `{_format_command(command)}` failed with exit code {exit_code}.{detail_suffix}"
        )


class DocBaseInvalidJsonError(DocBaseCliError):
    def __init__(self, *, command: Sequence[str], stdout: str) -> None:
        details = _truncate_output(stdout) if stdout.strip() else "No stdout was returned."
        super().__init__(
            f"DocBase CLI command `{_format_command(command)}` did not return valid JSON. "
            f"stdout: {details}"
        )
