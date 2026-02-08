# Screencapture MCP Server

macOS標準の `screencapture` コマンドを使用して、スクリーンショットの撮影や動画の録画を行うMCPサーバーです。

## 機能

- `capture_screenshot`: 現在の画面を静止画（PNG）として保存します。
- `capture_window`: 特定のアプリケーションウィンドウを検索してスクリーンショットを撮影します。
- `record_video`: 指定した秒数（デフォルト5秒、最大60秒）の動画（MOV）を録画します。
- `list_windows`: 現在開いている（表示されている）アプリケーションウィンドウの一覧を表示します。

保存先はデフォルトでプロジェクトディレクトリ配下の `Mcp_Captures` です。

## オプション

- `--output-dir <path>`: キャプチャの保存先ディレクトリを指定します。

## 実行 (uvxを使用)

インストール不要で、GitHubのリポジトリから直接実行できます。

```bash
uvx --from git+https://github.com/nomotohiroki/screencapture-mcp.git screencapture-mcp --output-dir ~/Downloads/Captures
```

## MCP設定例 (Claude Desktopなど)

`uvx` を使用してGitHubから直接読み込む設定です。

```json
{
  "mcpServers": {
    "screencapture": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/nomotohiroki/screencapture-mcp.git",
        "screencapture-mcp",
        "--output-dir",
        "/Users/YOUR_USER_NAME/Desktop/MCP_Captures"
      ]
    }
  }
}
```
