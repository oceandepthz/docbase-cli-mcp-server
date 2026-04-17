from types import SimpleNamespace

from docbase_mcp.server import RuntimeOptions, configure_runtime, parse_runtime_options


def test_parse_runtime_options_defaults_to_stdio() -> None:
    options = parse_runtime_options([], {})

    assert options == RuntimeOptions(
        transport="stdio",
        host="127.0.0.1",
        port=8000,
    )


def test_parse_runtime_options_reads_http_env_defaults() -> None:
    options = parse_runtime_options(
        [],
        {
            "DOCBASE_MCP_TRANSPORT": "streamable-http",
            "DOCBASE_MCP_HOST": "0.0.0.0",
            "DOCBASE_MCP_PORT": "9000",
        },
    )

    assert options == RuntimeOptions(
        transport="streamable-http",
        host="0.0.0.0",
        port=9000,
    )


def test_configure_runtime_updates_server_settings() -> None:
    fake_server = SimpleNamespace(settings=SimpleNamespace(host="127.0.0.1", port=8000))

    configure_runtime(
        fake_server,
        RuntimeOptions(transport="streamable-http", host="0.0.0.0", port=9100),
    )

    assert fake_server.settings.host == "0.0.0.0"
    assert fake_server.settings.port == 9100
