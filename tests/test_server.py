from types import SimpleNamespace

from mcp.server.transport_security import TransportSecurityMiddleware

from docbase_mcp.server import RuntimeOptions, configure_runtime, parse_runtime_options


def test_parse_runtime_options_defaults_to_stdio() -> None:
    options = parse_runtime_options([], {})

    assert options == RuntimeOptions(
        transport="stdio",
        host="127.0.0.1",
        port=8000,
        allowed_hosts=(),
        allowed_origins=(),
        disable_dns_rebinding_protection=False,
    )


def test_parse_runtime_options_reads_http_env_defaults() -> None:
    options = parse_runtime_options(
        [],
        {
            "DOCBASE_MCP_TRANSPORT": "streamable-http",
            "DOCBASE_MCP_HOST": "0.0.0.0",
            "DOCBASE_MCP_PORT": "9000",
            "DOCBASE_MCP_ALLOWED_HOSTS": "docbase-mcp:*,librechat-mcp:*",
            "DOCBASE_MCP_ALLOWED_ORIGINS": "http://librechat:3080",
        },
    )

    assert options == RuntimeOptions(
        transport="streamable-http",
        host="0.0.0.0",
        port=9000,
        allowed_hosts=("docbase-mcp:*", "librechat-mcp:*"),
        allowed_origins=("http://librechat:3080",),
        disable_dns_rebinding_protection=False,
    )


def test_configure_runtime_updates_server_settings() -> None:
    fake_server = SimpleNamespace(
        settings=SimpleNamespace(host="127.0.0.1", port=8000, transport_security=None)
    )

    configure_runtime(
        fake_server,
        RuntimeOptions(
            transport="streamable-http",
            host="0.0.0.0",
            port=9100,
            allowed_hosts=("docbase-mcp:*",),
            allowed_origins=(),
            disable_dns_rebinding_protection=False,
        ),
    )

    assert fake_server.settings.host == "0.0.0.0"
    assert fake_server.settings.port == 9100
    assert fake_server.settings.transport_security.enable_dns_rebinding_protection is True
    assert "docbase-mcp:*" in fake_server.settings.transport_security.allowed_hosts
    assert "localhost:*" in fake_server.settings.transport_security.allowed_hosts

    middleware = TransportSecurityMiddleware(fake_server.settings.transport_security)

    assert middleware._validate_host("docbase-mcp:8025")


def test_parse_runtime_options_can_disable_dns_rebinding_protection() -> None:
    options = parse_runtime_options(
        [],
        {
            "DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION": "true",
        },
    )

    assert options.disable_dns_rebinding_protection is True
