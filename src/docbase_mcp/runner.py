from __future__ import annotations

import asyncio
import json
import os
import shutil
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from .errors import (
    DocBaseCommandFailedError,
    DocBaseCommandTimeoutError,
    DocBaseExecutableNotFoundError,
    DocBaseInvalidJsonError,
    MissingEnvironmentVariableError,
)
from .models import DocBaseCommandResult

SubprocessFactory = Callable[..., Awaitable[asyncio.subprocess.Process]]


class DocBaseCliRunner:
    def __init__(
        self,
        *,
        executable_name: str = "docbase",
        timeout_seconds: float = 60.0,
        which: Callable[[str], str | None] = shutil.which,
        subprocess_factory: SubprocessFactory = asyncio.create_subprocess_exec,
    ) -> None:
        self._executable_name = executable_name
        self._timeout_seconds = timeout_seconds
        self._which = which
        self._subprocess_factory = subprocess_factory
        self._resolved_executable: str | None = None

    async def run_json(self, command: Sequence[str]) -> DocBaseCommandResult:
        executable = self._resolve_executable()
        environment = self._build_environment()
        process = await self._subprocess_factory(
            executable,
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=environment,
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=self._timeout_seconds,
            )
        except TimeoutError as error:
            process.kill()
            await process.wait()
            raise DocBaseCommandTimeoutError(command, self._timeout_seconds) from error

        stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
        stderr = stderr_bytes.decode("utf-8", errors="replace").strip()

        if process.returncode != 0:
            raise DocBaseCommandFailedError(
                command=command,
                exit_code=process.returncode or -1,
                stdout=stdout,
                stderr=stderr,
            )

        try:
            payload: Any = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise DocBaseInvalidJsonError(command=command, stdout=stdout) from error

        return DocBaseCommandResult(command=list(command), data=payload)

    def _resolve_executable(self) -> str:
        if self._resolved_executable is None:
            resolved = self._which(self._executable_name)
            if resolved is None:
                raise DocBaseExecutableNotFoundError()
            self._resolved_executable = resolved
        return self._resolved_executable

    def _build_environment(self) -> dict[str, str]:
        environment = os.environ.copy()

        for variable_name in ("DOCBASE_TEAM_DOMAIN", "DOCBASE_TOKEN"):
            value = environment.get(variable_name)
            if value is None or not value.strip():
                raise MissingEnvironmentVariableError(variable_name)

        return environment
