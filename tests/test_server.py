import sys
import subprocess
from unittest.mock import MagicMock, patch
import pytest

# Add parent directory to path to import server
sys.path.append(".")

# Mock Quartz before importing the server
sys.modules["Quartz"] = MagicMock()

import screencapture_server

class TestScreencaptureServer:

    @pytest.fixture
    def mock_quartz(self):
        with patch("screencapture_server.CGWindowListCopyWindowInfo") as mock:
            yield mock

    @pytest.fixture
    def mock_subprocess(self):
        with patch("subprocess.run") as mock:
            yield mock

    def test_find_window_id_success(self, mock_quartz):
        mock_quartz.return_value = [
            {
                "kCGWindowOwnerName": "TestApp",
                "kCGWindowName": "Main Window",
                "kCGWindowNumber": 123,
                "kCGWindowBounds": {"getWidth": 500, "getHeight": 400}
            },
            {
                "kCGWindowOwnerName": "OtherApp",
                "kCGWindowNumber": 456
            }
        ]
        
        window_id = screencapture_server.find_window_id("TestApp")
        assert window_id == 123

    def test_find_window_id_not_found(self, mock_quartz):
        mock_quartz.return_value = []
        window_id = screencapture_server.find_window_id("NonExistentApp")
        assert window_id is None

    def test_capture_screenshot_success(self, mock_subprocess):
        result = screencapture_server.capture_screenshot("test.png")
        
        assert "Screenshot saved to" in result
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert args[0] == "/usr/sbin/screencapture"
        assert "-x" in args
        assert str(args[-1]).endswith("test.png")

    def test_capture_screenshot_failure(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "cmd", stderr=b"Error occurred")
        
        result = screencapture_server.capture_screenshot()
        assert "Error capturing screenshot" in result
        assert "Error occurred" in result

    def test_capture_window_success(self, mock_subprocess):
        with patch("screencapture_server.find_window_id", return_value=123):
            result = screencapture_server.capture_window("TestApp", "window.png")
            
            assert "Window capture of 'TestApp' saved to" in result
            mock_subprocess.assert_called_once()
            args = mock_subprocess.call_args[0][0]
            assert "-l" in args
            assert "123" in args

    def test_capture_window_not_found(self):
        with patch("screencapture_server.find_window_id", return_value=None):
            result = screencapture_server.capture_window("UnknownApp")
            assert "Could not find a visible window" in result

    def test_record_video_duration_limit(self, mock_subprocess):
        screencapture_server.record_video(duration_seconds=100, filename="video.mov")
        
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        # Duration should be capped at 60
        assert args[2] == "60"

    def test_list_windows(self, mock_quartz):
        mock_quartz.return_value = [
            {
                "kCGWindowOwnerName": "App1",
                "kCGWindowName": "Win1",
                "kCGWindowBounds": {"getWidth": 200, "getHeight": 200}
            },
            {
                "kCGWindowOwnerName": "App2",
                "kCGWindowName": "Win2",
                "kCGWindowBounds": {"getWidth": 200, "getHeight": 200}
            }
        ]
        
        result = screencapture_server.list_windows()
        assert "App1" in result
        assert "App2" in result

    def test_list_windows_empty(self, mock_quartz):
        mock_quartz.return_value = []
        result = screencapture_server.list_windows()
        assert "No visible application windows found" in result
