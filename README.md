# docbase-mcp

`docbase-mcp` は、公式の `docbase` CLI をラップして MCP サーバとして公開する Python パッケージです。

このリポジトリは **DocBase API を直接呼ばず**、`docbase` コマンドを subprocess で実行し、その JSON 出力を MCP ツールの結果として返します。

## 概要

- **実装言語**: Python
- **MCP 実装**: MCP Python SDK (`FastMCP`)
- **認証方式**: アクセストークン認証のみ
- **実行モード**:
  - `stdio` — ローカルでクライアントが直接プロセス起動する用途
  - `streamable-http` — Docker や HTTP 対応 MCP クライアント向け
- **現在のスコープ**: read-only ツールのみ

## 現在サポートしているツール

| ツール名 | 説明 |
| --- | --- |
| `docbase_search_posts` | メモ検索 |
| `docbase_get_post` | メモ詳細取得 |
| `docbase_list_comments` | コメント一覧取得 |
| `docbase_search_users` | ユーザー検索 |
| `docbase_get_current_user_profile` | 自分のプロフィール取得 |
| `docbase_get_user_groups` | ユーザー所属グループ取得 |
| `docbase_search_groups` | グループ検索 |
| `docbase_get_group` | グループ詳細取得 |
| `docbase_list_tags` | タグ一覧取得 |
| `docbase_list_good_jobs` | グッジョブ一覧取得 |

各ツールは、概ね次のような構造化レスポンスを返します。

```json
{
  "command": ["posts", "search", "--page", "1"],
  "data": {}
}
```

- `command`: 実行した `docbase` CLI 引数
- `data`: CLI が返した JSON をパースした結果

## 動作の考え方

このサーバは認証状態を保持しません。実行時の環境変数から以下を読み取り、それを `docbase` CLI にそのまま渡します。

- `DOCBASE_TEAM_DOMAIN`
- `DOCBASE_TOKEN`

そのため、**remote HTTP サーバとして動かす場合は、これらの値をサーバ側プロセスまたはコンテナ側に設定する必要があります。**

## 前提条件

ローカル実行時は次が必要です。

- Python 3.11 以上
- `uv`
- Node.js / npm
- 公式 DocBase CLI

DocBase CLI のインストール:

```powershell
npm install --ignore-scripts -g @krayinc/docbase-cli
```

Python 依存のセットアップ:

```powershell
uv sync --dev
```

## 環境変数

### DocBase 認証

| 変数名 | 必須 | 用途 |
| --- | --- | --- |
| `DOCBASE_TEAM_DOMAIN` | 必須 | DocBase チームドメイン |
| `DOCBASE_TOKEN` | 必須 | DocBase アクセストークン |

### MCP ランタイム

| 変数名 | 必須 | 既定値 | 用途 |
| --- | --- | --- | --- |
| `DOCBASE_MCP_TRANSPORT` | 任意 | `stdio` | `stdio` または `streamable-http` |
| `DOCBASE_MCP_HOST` | 任意 | `127.0.0.1` | HTTP モードで bind するホスト |
| `DOCBASE_MCP_PORT` | 任意 | `8000` | HTTP モードで bind するポート |
| `DOCBASE_MCP_ALLOWED_HOSTS` | 任意 | なし | HTTP モードで許可する `Host` ヘッダー。カンマ区切り。`:*` のポートワイルドカード可 |
| `DOCBASE_MCP_ALLOWED_ORIGINS` | 任意 | なし | HTTP モードで許可する `Origin` ヘッダー。カンマ区切り |
| `DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION` | 任意 | `false` | 信頼できる環境で DNS rebinding protection を無効化 |

`DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION` は `1` / `true` / `yes` / `on` で有効になります。

## ローカル実行

### stdio モード

既定は `stdio` です。

```powershell
uv run docbase-mcp
```

または:

```powershell
uv run python -m docbase_mcp
```

### streamable-http モード

```powershell
uv run docbase-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

HTTP エンドポイント:

```text
http://127.0.0.1:8000/mcp
```

## MCP クライアント連携

### stdio で使う場合

プロセスを直接起動する MCP クライアントでは、サーバ起動時の `env` に DocBase 認証情報を渡します。

```json
{
  "mcpServers": {
    "docbase": {
      "command": "uv",
      "args": ["run", "docbase-mcp"],
      "cwd": "C:\\path\\to\\docbase-mcp",
      "env": {
        "DOCBASE_TEAM_DOMAIN": "your-team",
        "DOCBASE_TOKEN": "your-access-token"
      }
    }
  }
}
```

### HTTP で使う場合

HTTP 対応クライアントでは、MCP サーバの URL を指定します。

```text
http://127.0.0.1:8000/mcp
```

この場合、**DocBase 認証情報は HTTP クライアント側ではなく、MCP サーバ側に置く必要があります。**

## Docker

このリポジトリには `Dockerfile` と `.dockerignore` が含まれています。

Docker イメージは次を含みます。

- Python 実行環境
- `uv`
- Node.js / npm
- `@krayinc/docbase-cli`
- このリポジトリの Python パッケージ

### build

```powershell
docker build -t docbase-mcp .
```

### run

```powershell
docker run --rm -p 8000:8000 `
  -e DOCBASE_TEAM_DOMAIN=your-team `
  -e DOCBASE_TOKEN=your-access-token `
  docbase-mcp
```

Docker イメージの既定値:

- `DOCBASE_MCP_TRANSPORT=streamable-http`
- `DOCBASE_MCP_HOST=0.0.0.0`
- `DOCBASE_MCP_PORT=8000`

したがって、既定のエンドポイントは次です。

```text
http://localhost:8000/mcp
```

### 外部公開ポートを変更する例

```powershell
docker run --rm -p 9000:8000 `
  -e DOCBASE_TEAM_DOMAIN=your-team `
  -e DOCBASE_TOKEN=your-access-token `
  docbase-mcp
```

この場合のエンドポイント:

```text
http://localhost:9000/mcp
```

### コンテナ内ポートも変更する例

```powershell
docker run --rm -p 9000:9000 `
  -e DOCBASE_TEAM_DOMAIN=your-team `
  -e DOCBASE_TOKEN=your-access-token `
  -e DOCBASE_MCP_PORT=9000 `
  docbase-mcp
```

## LibreChat 連携

LibreChat で `type: "streamable-http"` を使う場合、LibreChat は **すでに起動している HTTP サーバ**に接続します。  
そのため、DocBase の認証情報は **LibreChat 側の `env:` ではなく、`docbase-mcp` サーバ側**に置いてください。

### Compose 例

```yaml
services:
  docbase-mcp:
    image: docbase-mcp
    pull_policy: never
    environment:
      DOCBASE_TEAM_DOMAIN: your-team
      DOCBASE_TOKEN: ${DOCBASE_API_TOKEN}
      DOCBASE_MCP_PORT: "8025"
      DOCBASE_MCP_ALLOWED_HOSTS: "docbase-mcp:*"
    networks:
      - librechat_default
```

### LibreChat MCP 設定例

```yaml
docbase-mcp:
  type: "streamable-http"
  url: "http://docbase-mcp:8025/mcp"
```

### LibreChat 利用時の注意

- `DOCBASE_TEAM_DOMAIN` / `DOCBASE_TOKEN` は **サーバコンテナ側**
- `DOCBASE_DOMAIN` / `DOCBASE_API_TOKEN` は、このサーバが直接読む変数名ではありません
- Docker ネットワーク上のサービス名で接続するなら、`DOCBASE_MCP_ALLOWED_HOSTS` にそのホスト名を入れてください
- 例: `DOCBASE_MCP_ALLOWED_HOSTS=docbase-mcp:*`

必要であれば、信頼できる内部ネットワーク向けに Host/Origin チェックを無効化できます。

```yaml
environment:
  DOCBASE_MCP_DISABLE_DNS_REBINDING_PROTECTION: "true"
```

ただし、これは信頼できる環境に限定してください。

## エラー処理

このサーバは、少なくとも次のケースを明示的なエラーとして返します。

- `DOCBASE_TEAM_DOMAIN` が未設定
- `DOCBASE_TOKEN` が未設定
- `docbase` 実行ファイルが見つからない
- `docbase` CLI が非 0 で終了した
- `docbase` CLI の標準出力が JSON として解釈できない

## テスト

```powershell
uv run pytest
```

## 制限事項

- 現在は **read-only ツールのみ**です
- メモ作成・更新・削除、コメント投稿、添付ファイル操作などの書き込み系ツールは未実装です
- 認証方式は **アクセストークン認証のみ**で、OAuth はサポートしていません
