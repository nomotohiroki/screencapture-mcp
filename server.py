import os
import subprocess
import time
from pathlib import Path
from mcp.server.fastmcp import FastMCP
try:
    from Quartz import (
        CGWindowListCopyWindowInfo, 
        kCGWindowListOptionOnScreenOnly, 
        kCGNullWindowID
    )
except ImportError:
    # Fallback for environments where Quartz might not be available
    CGWindowListCopyWindowInfo = None

# Initialize FastMCP server
mcp = FastMCP("screencapture-mcp")

# Ensure a directory for captures exists
CAPTURE_DIR = Path.home() / "Desktop" / "MCP_Captures"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

def find_window_id(app_name: str):
    """Finds the window ID for a given application name."""
    if not CGWindowListCopyWindowInfo:
        return None
    
    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    
    for window in window_list:
        owner_name = window.get("kCGWindowOwnerName", "")
        if app_name.lower() in owner_name.lower():
            # Check if it's a standard window (has a name or is large enough)
            # This helps filter out menu bar items and other small background windows
            window_name = window.get("kCGWindowName", "")
            bounds = window.get("kCGWindowBounds", {})
            if window_name or (bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100):
                return window.get("kCGWindowNumber")
    return None

@mcp.tool()
def capture_screenshot(filename: str = None) -> str:
    """
    Captures a screenshot of the main display and saves it to the Desktop.
    
    Args:
        filename: Optional name for the file. If not provided, a timestamp will be used.
    """
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"
    
    filepath = CAPTURE_DIR / filename
    
    try:
        # -x: silent, -C: capture cursor
        subprocess.run(["screencapture", "-x", "-C", str(filepath)], check=True)
        return f"Screenshot saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing screenshot: {str(e)}"

@mcp.tool()
def capture_window(app_name: str, filename: str = None) -> str:
    """
    Captures a screenshot of a specific application window.
    
    Args:
        app_name: Name of the application (e.g., 'Finder', 'Safari', 'Chrome').
        filename: Optional name for the file.
    """
    window_id = find_window_id(app_name)
    if not window_id:
        return f"Could not find a visible window for application: {app_name}"

    if not filename:
        filename = f"window_{app_name}_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"
    
    filepath = CAPTURE_DIR / filename
    
    try:
        # -l: capture window by ID, -o: no shadow (optional, can be removed if shadow is desired)
        subprocess.run(["screencapture", "-l", str(window_id), "-o", str(filepath)], check=True)
        return f"Window capture of '{app_name}' saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing window: {str(e)}"

@mcp.tool()
def record_video(duration_seconds: int = 5, filename: str = None) -> str:
    """
    Records a video of the screen for a specified duration and saves it to the Desktop.
    
    Args:
        duration_seconds: Duration of the recording in seconds (max 60).
        filename: Optional name for the file. If not provided, a timestamp will be used.
    """
    if duration_seconds > 60:
        duration_seconds = 60
    
    if not filename:
        filename = f"recording_{int(time.time())}.mov"
    if not filename.endswith(".mov"):
        filename += ".mov"
    
    filepath = CAPTURE_DIR / filename
    
    try:
        # -V: record video for seconds
        # Note: In some macOS versions, -V might behave differently or require user permission
        subprocess.run(["screencapture", "-V", str(duration_seconds), str(filepath)], check=True)
        return f"Video recording saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error recording video: {str(e)}"

@mcp.tool()
def list_windows() -> str:
    """
    Lists the names of all currently visible application windows.
    Use this to find the correct app_name for capture_window.
    """
    if not CGWindowListCopyWindowInfo:
        return "Quartz API not available."
    
    options = kCGWindowListOptionOnScreenOnly
    window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    
    apps = set()
    for window in window_list:
        owner_name = window.get("kCGWindowOwnerName", "")
        window_name = window.get("kCGWindowName", "")
        bounds = window.get("kCGWindowBounds", {})
        
        # Filter for meaningful windows
        if owner_name and (window_name or (bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100)):
            apps.add(owner_name)
    
    if not apps:
        return "No visible application windows found."
    
    return "Visible applications:\n" + "\n".join(sorted(apps))

if __name__ == "__main__":
    mcp.run()
