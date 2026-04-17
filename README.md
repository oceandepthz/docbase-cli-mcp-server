# docbase-mcp

`docbase-mcp` is a Python MCP server that wraps the official `docbase` CLI.

It supports:

- `stdio` for local command-style MCP launches
- `streamable-http` for Docker or other HTTP-capable MCP clients

The server uses **access-token authentication only**. The MCP client must provide these environment variables when launching the server:

- `DOCBASE_TEAM_DOMAIN`
- `DOCBASE_TOKEN`

## Scope

This initial version is a read-only MVP. It exposes these tools:

- `docbase_search_posts`
- `docbase_get_post`
- `docbase_list_comments`
- `docbase_search_users`
- `docbase_get_current_user_profile`
- `docbase_get_user_groups`
- `docbase_search_groups`
- `docbase_get_group`
- `docbase_list_tags`
- `docbase_list_good_jobs`

Each tool returns a structured object with:

- `command`: the DocBase CLI arguments that were executed
- `data`: the parsed JSON returned by the CLI

## Requirements

- Python 3.11+
- Node.js and npm
- The official DocBase CLI:

```powershell
npm install --ignore-scripts -g @krayinc/docbase-cli
```

## Development setup

```powershell
uv sync --dev
```

## Run locally

Default local mode is `stdio`:

```powershell
uv run docbase-mcp
```

You can also run the package module directly:

```powershell
uv run python -m docbase_mcp
```

To run locally over HTTP instead:

```powershell
uv run docbase-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

The streamable HTTP endpoint is exposed at:

```text
http://127.0.0.1:8000/mcp
```

## MCP client configuration

Example `stdio` configuration:

```json
{
  "mcpServers": {
    "docbase": {
      "command": "uv",
      "args": ["run", "docbase-mcp"],
      "cwd": "C:\\Users\\you\\path\\to\\docbase cli wapper mcp",
      "env": {
        "DOCBASE_TEAM_DOMAIN": "your-team",
        "DOCBASE_TOKEN": "your-access-token"
      }
    }
  }
}
```

If the client does not use `uv`, point it at a Python interpreter that has this package installed and run `-m docbase_mcp`.

For an HTTP-capable MCP client, point it at:

```text
http://127.0.0.1:8000/mcp
```

The exact JSON fields vary by client, but the transport target is the streamable HTTP endpoint above.

## Docker

Build the image:

```powershell
docker build -t docbase-mcp .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 `
  -e DOCBASE_TEAM_DOMAIN=your-team `
  -e DOCBASE_TOKEN=your-access-token `
  docbase-mcp
```

The container defaults to:

- `DOCBASE_MCP_TRANSPORT=streamable-http`
- `DOCBASE_MCP_HOST=0.0.0.0`
- `DOCBASE_MCP_PORT=8000`

So the MCP endpoint is:

```text
http://localhost:8000/mcp
```

You can override the HTTP port if needed:

```powershell
docker run --rm -p 9000:9000 `
  -e DOCBASE_TEAM_DOMAIN=your-team `
  -e DOCBASE_TOKEN=your-access-token `
  -e DOCBASE_MCP_PORT=9000 `
  docbase-mcp
```

## Error handling

The server returns actionable tool errors for these cases:

- missing `DOCBASE_TEAM_DOMAIN`
- missing `DOCBASE_TOKEN`
- missing `docbase` executable in `PATH`
- non-zero exit status from `docbase`
- invalid JSON returned by the CLI

## Tests

```powershell
uv run pytest
```
