import os
import sys
import subprocess
import time
from pathlib import Path

# MCP communication must happen on stdout. 
# We must ensure no other library prints to stdout.
try:
    from Quartz import (
        CGWindowListCopyWindowInfo, 
        kCGWindowListOptionOnScreenOnly, 
        kCGNullWindowID
    )
except ImportError:
    CGWindowListCopyWindowInfo = None

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with explicit log level to avoid stdout pollution
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
            window_name = window.get("kCGWindowName", "")
            bounds = window.get("kCGWindowBounds", {})
            if window_name or (bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100):
                return window.get("kCGWindowNumber")
    return None

@mcp.tool()
def capture_screenshot(filename: str = None) -> str:
    """
    Captures a screenshot of the main display and saves it to the Desktop.
    """
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    if not filename.endswith(".png"):
        filename += ".png"
    
    filepath = CAPTURE_DIR / filename
    
    try:
        # Using subprocess with capture_output to prevent leaking info to stdout
        subprocess.run(["screencapture", "-x", "-C", str(filepath)], check=True, capture_output=True)
        return f"Screenshot saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing screenshot: {e.stderr.decode() if e.stderr else str(e)}"

@mcp.tool()
def capture_window(app_name: str, filename: str = None) -> str:
    """
    Captures a screenshot of a specific application window.
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
        subprocess.run(["screencapture", "-l", str(window_id), "-o", str(filepath)], check=True, capture_output=True)
        return f"Window capture of '{app_name}' saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error capturing window: {e.stderr.decode() if e.stderr else str(e)}"

@mcp.tool()
def record_video(duration_seconds: int = 5, filename: str = None) -> str:
    """
    Records a video of the screen for a specified duration (max 60s).
    """
    if duration_seconds > 60:
        duration_seconds = 60
    
    if not filename:
        filename = f"recording_{int(time.time())}.mov"
    if not filename.endswith(".mov"):
        filename += ".mov"
    
    filepath = CAPTURE_DIR / filename
    
    try:
        subprocess.run(["screencapture", "-V", str(duration_seconds), str(filepath)], check=True, capture_output=True)
        return f"Video recording saved to: {filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error recording video: {e.stderr.decode() if e.stderr else str(e)}"

@mcp.tool()
def list_windows() -> str:
    """
    Lists the names of all currently visible application windows.
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
        
        if owner_name and (window_name or (bounds.get("getWidth", 0) > 100 and bounds.get("getHeight", 0) > 100)):
            apps.add(owner_name)
    
    if not apps:
        return "No visible application windows found."
    
    return "Visible applications:\n" + "\n".join(sorted(apps))

def main():
    # Final safety check: ensure stdout is not used for anything but MCP
    mcp.run()

if __name__ == "__main__":
    main()
