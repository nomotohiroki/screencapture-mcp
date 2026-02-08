# Screencapture MCP Server

macOS標準の `screencapture` コマンドを使用して、スクリーンショットの撮影や動画の録画を行うMCPサーバーです。

## 機能

- `capture_screenshot`: 現在の画面を静止画（PNG）として保存します。
- `record_video`: 指定した秒数（デフォルト5秒、最大60秒）の動画（MOV）を録画します。

保存先はデフォルトで `~/Desktop/MCP_Captures` です。

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install mcp pyobjc
```

## 実行 (uvxを使用)

インストール不要で、GitHubのリポジトリから直接実行できます。

```bash
uvx --from git+https://github.com/nomotohiroki/screencapture-mcp.git screencapture-mcp
```

## MCP設定例 (Claude Desktopなど)

`uvx` を使用してGitHubから直接読み込む設定です。これにより、常に最新のツールが利用可能になります。

```json
{
  "mcpServers": {
    "screencapture": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/nomotohiroki/screencapture-mcp.git",
        "screencapture-mcp"
      ]
    }
  }
}
```
