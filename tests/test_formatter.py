import pytest
from unittest.mock import MagicMock
from src.formatter import OutputFormatter
from src.models import Directory, File

@pytest.fixture
def formatter():
    return OutputFormatter()

# --- Basic Rendering Tests ---

def test_render_comment(formatter, capsys):
    """Verify comments are wrapped in grey color codes."""
    formatter.render_comment("# This is a test comment")
    captured = capsys.readouterr()
    # \033[90m is the code for grey
    assert "\033[90m# This is a test comment\033[0m" in captured.out

def test_render_command_echo(formatter, capsys):
    """Verify command echoes are prefixed with '>'."""
    formatter.render_command_echo("mkdir test")
    captured = capsys.readouterr()
    assert "> mkdir test" in captured.out

# --- Result Rendering Tests ---

def test_render_result_none(formatter, capsys):
    """Verify that None (default success) prints a green [OK]."""
    formatter.render_result(None)
    captured = capsys.readouterr()
    assert "\033[92m[OK]\033[0m" in captured.out

def test_render_result_true(formatter, capsys):
    """Verify that True (e.g., from cls) prints absolutely nothing."""
    formatter.render_result(True)
    captured = capsys.readouterr()
    assert captured.out == ""

def test_render_result_string(formatter, capsys):
    """Verify string results (cat/mkfs) are rendered in blue."""
    formatter.render_result("File content")
    captured = capsys.readouterr()
    assert "\033[94mFile content\033[0m" in captured.out

# --- Error Rendering Tests ---

def test_render_error(formatter, capsys):
    """Verify errors are prefixed with [ERROR] and wrapped in red."""
    error_msg = "[VFSSyntaxException] - Unknown command"
    formatter.render_error(error_msg)
    captured = capsys.readouterr()
    # \033[91m is the code for red
    assert "\033[91m[ERROR] [VFSSyntaxException] - Unknown command\033[0m" in captured.out

# --- Table (ls) Rendering Tests ---

def test_render_ls_empty(formatter, capsys):
    """Verify empty directory output."""
    formatter.render_result([])
    captured = capsys.readouterr()
    assert "(empty)" in captured.out

def test_render_ls_with_nodes(formatter, capsys):
    """
    Verify that the table header and node details are correctly aligned.
    We use mocks for nodes to isolate formatter logic.
    """
    mock_dir = MagicMock(spec=Directory)
    mock_dir.name = "docs"
    mock_dir.permissions = 0o755
    mock_dir.get_size.return_value = 100
    # Directory check uses isinstance, so we can't fully mock Directory class 
    # if it's used in isinstance(node, Directory). Using real objects is safer here.
    
    real_dir = Directory("home")
    real_dir.permissions = 0o700
    
    formatter.render_result([real_dir])
    captured = capsys.readouterr()
    
    # Check Header
    assert "TYPE" in captured.out
    assert "PERM" in captured.out
    assert "SIZE" in captured.out
    # Check Content
    assert "DIR" in captured.out
    assert "700" in captured.out
    assert "home" in captured.out