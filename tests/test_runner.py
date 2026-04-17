import asyncio

import pytest

from docbase_mcp.errors import (
    DocBaseCommandFailedError,
    DocBaseInvalidJsonError,
    MissingEnvironmentVariableError,
)
from docbase_mcp.runner import DocBaseCliRunner


class FakeProcess:
    def __init__(
        self,
        *,
        stdout: bytes = b"{}",
        stderr: bytes = b"",
        returncode: int = 0,
    ) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self.killed = False

    async def communicate(self) -> tuple[bytes, bytes]:
        return self._stdout, self._stderr

    def kill(self) -> None:
        self.killed = True

    async def wait(self) -> int:
        return self.returncode


@pytest.mark.asyncio
async def test_run_json_executes_docbase_with_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCBASE_TEAM_DOMAIN", "example-team")
    monkeypatch.setenv("DOCBASE_TOKEN", "secret-token")
    captured: dict[str, object] = {}

    async def fake_subprocess(*args: object, **kwargs: object) -> FakeProcess:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeProcess(stdout=b'{"ok": true}')

    runner = DocBaseCliRunner(
        which=lambda _: r"C:\tools\docbase.cmd",
        subprocess_factory=fake_subprocess,
    )

    result = await runner.run_json(["posts", "get", "123"])

    assert result.command == ["posts", "get", "123"]
    assert result.data == {"ok": True}
    assert captured["args"] == (r"C:\tools\docbase.cmd", "posts", "get", "123")
    assert captured["kwargs"]["stdout"] is asyncio.subprocess.PIPE
    assert captured["kwargs"]["stderr"] is asyncio.subprocess.PIPE
    assert captured["kwargs"]["env"]["DOCBASE_TEAM_DOMAIN"] == "example-team"
    assert captured["kwargs"]["env"]["DOCBASE_TOKEN"] == "secret-token"


@pytest.mark.asyncio
async def test_run_json_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCBASE_TEAM_DOMAIN", "example-team")
    monkeypatch.delenv("DOCBASE_TOKEN", raising=False)

    runner = DocBaseCliRunner(which=lambda _: r"C:\tools\docbase.cmd")

    with pytest.raises(MissingEnvironmentVariableError, match="DOCBASE_TOKEN"):
        await runner.run_json(["tags", "list"])


@pytest.mark.asyncio
async def test_run_json_raises_when_cli_returns_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCBASE_TEAM_DOMAIN", "example-team")
    monkeypatch.setenv("DOCBASE_TOKEN", "secret-token")

    async def fake_subprocess(*args: object, **kwargs: object) -> FakeProcess:
        return FakeProcess(stdout=b"not json")

    runner = DocBaseCliRunner(
        which=lambda _: r"C:\tools\docbase.cmd",
        subprocess_factory=fake_subprocess,
    )

    with pytest.raises(DocBaseInvalidJsonError, match="valid JSON"):
        await runner.run_json(["tags", "list"])


@pytest.mark.asyncio
async def test_run_json_raises_when_cli_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCBASE_TEAM_DOMAIN", "example-team")
    monkeypatch.setenv("DOCBASE_TOKEN", "secret-token")

    async def fake_subprocess(*args: object, **kwargs: object) -> FakeProcess:
        return FakeProcess(stdout=b'{"error":"boom"}', stderr=b"permission denied", returncode=2)

    runner = DocBaseCliRunner(
        which=lambda _: r"C:\tools\docbase.cmd",
        subprocess_factory=fake_subprocess,
    )

    with pytest.raises(DocBaseCommandFailedError, match="exit code 2"):
        await runner.run_json(["groups", "get", "1"])
