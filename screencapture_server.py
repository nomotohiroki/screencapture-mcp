import sys
import subprocess
import time
import argparse
from pathlib import Path

# --- STDOUT GUARD START ---
_original_stdout = sys.stdout
sys.stdout = sys.stderr

try:
    try:
        from Quartz import (  # type: ignore
            CGWindowListCopyWindowInfo,
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
    except ImportError:
        CGWindowListCopyWindowInfo = None

    from mcp.server.fastmcp import FastMCP

finally:
    sys.stdout = _original_stdout
# --- STDOUT GUARD END ---

# Global server instance (will be configured in main)
mcp = FastMCP("screencapture-mcp")
DEFAULT_CAPTURE_DIR = Path.cwd() / "Mcp_Captures"


def get_capture_dir(custom_dir: str | None = None) -> Path:
    """Returns the capture directory, creating it if necessary."""
    path = Path(custom_dir) if custom_dir else DEFAULT_CAPTURE_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_window_id(app_name: str) -> int | None:
    """Finds the window ID for a given application name."""
    if not CGWindowListCopyWindowInfo:
        return None

    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

    for window in window_list:
        owner_name = window.get("kCGWindowOwnerName", "")
        if app_name.lower() in owner_name.lower():
            window_name = window.get("kCGWindowName", "")
            bounds = window.get("kCGWindowBounds", {})
            if window_name or (
                bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100
            ):
                return window.get("kCGWindowNumber")
    return None


@mcp.tool()
def capture_screenshot(filename: str | None = None) -> str:
    """
    Captures a screenshot of the main display.

    Args:
        filename: Optional filename for the screenshot.

    Returns:
        Status message indicating success or failure.
    """
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"

    # mcp.run() will be called with the configured directory
    # For now we use the global DEFAULT_CAPTURE_DIR which might be overridden in main
    filepath = DEFAULT_CAPTURE_DIR / filename

    try:
        subprocess.run(
            ["/usr/sbin/screencapture", "-x", "-C", str(filepath)],
            check=True,
            capture_output=True
        )
        return f"Screenshot saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing screenshot: {e.stderr.decode() if e.stderr else str(e)}"


@mcp.tool()
def capture_window(app_name: str, filename: str | None = None) -> str:
    """
    Captures a screenshot of a specific application window.

    Args:
        app_name: Name of the application to capture.
        filename: Optional filename for the screenshot.

    Returns:
        Status message indicating success or failure.
    """
    window_id = find_window_id(app_name)
    if not window_id:
        return f"Could not find a visible window for application: {app_name}"

    if not filename:
        filename = f"window_{app_name}_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"

    filepath = DEFAULT_CAPTURE_DIR / filename

    try:
        subprocess.run(
            ["/usr/sbin/screencapture", "-l", str(window_id), "-o", str(filepath)],
            check=True,
            capture_output=True
        )
        return f"Window capture of '{app_name}' saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing window: {e.stderr.decode() if e.stderr else str(e)}"


@mcp.tool()
def record_video(duration_seconds: int = 5, filename: str | None = None) -> str:
    """
    Records a video of the screen for a specified duration (max 60s).

    Args:
        duration_seconds: Duration of the recording in seconds.
        filename: Optional filename for the video.

    Returns:
        Status message indicating success or failure.
    """
    duration_seconds = min(duration_seconds, 60)

    if not filename:
        filename = f"recording_{int(time.time())}.mov"
    if not filename.endswith(".mov"):
        filename += ".mov"

    filepath = DEFAULT_CAPTURE_DIR / filename

    try:
        subprocess.run(
            ["/usr/sbin/screencapture", "-V", str(duration_seconds), str(filepath)],
            check=True,
            capture_output=True
        )
        return f"Video recording saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error recording video: {e.stderr.decode() if e.stderr else str(e)}"


@mcp.tool()
def list_windows() -> str:
    """
    Lists the names of all currently visible application windows.

    Returns:
        A formatted string listing visible applications.
    """
    if not CGWindowListCopyWindowInfo:
        return "Quartz API not available. Make sure you are on macOS."

    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

    apps = set()
    for window in window_list:
        owner_name = window.get("kCGWindowOwnerName", "")
        window_name = window.get("kCGWindowName", "")
        bounds = window.get("kCGWindowBounds", {})

        if owner_name and (
            window_name or
            (bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100)
        ):
            apps.add(owner_name)

    if not apps:
        return "No visible application windows found."

    return "Visible applications:\n" + "\n".join(sorted(apps))


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server for macOS screen capture")
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save captures (default: project_dir/Mcp_Captures)"
    )
    args = parser.parse_args()

    global DEFAULT_CAPTURE_DIR
    if args.output_dir:
        DEFAULT_CAPTURE_DIR = Path(args.output_dir)
    
    # Ensure directory exists
    DEFAULT_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    mcp.run()


if __name__ == "__main__":
    main()
