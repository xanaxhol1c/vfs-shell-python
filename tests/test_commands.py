import pytest
import sys
from unittest.mock import patch
from src.context import VFSContext
from src.models import Directory, File
from src.exceptions import VFSFileSystemException, VFSValidationException
from src.commands import (
    MkfsCommand, MkdirCommand, TouchCommand, 
    CdCommand, ChmodCommand, LsCommand, CatCommand, ExitCommand
)

@pytest.fixture
def context():
    """Provides a fresh, clean VFS context for every test."""
    ctx = VFSContext()
    ctx.max_size = 2048  # Initialize with some space
    return ctx

# --- MkfsCommand Tests ---

def test_mkfs_positive(context):
    cmd = MkfsCommand(5000)
    result = cmd.execute(context)
    assert context.max_size == 5000
    assert "initialized" in result

def test_mkfs_negative_invalid_size(context):
    cmd = MkfsCommand(-10)
    with pytest.raises(VFSValidationException) as exc:
        cmd.execute(context)
    assert "greater than 0" in str(exc.value)

# --- MkdirCommand Tests ---

def test_mkdir_positive(context):
    cmd = MkdirCommand("home")
    cmd.execute(context)
    assert "home" in context.root.children
    assert isinstance(context.root.get_child("home"), Directory)

def test_mkdir_negative_invalid_path(context):
    # Attempting to create a dir in a non-existent parent
    cmd = MkdirCommand("/ghost/folder")
    with pytest.raises(VFSFileSystemException) as exc:
        cmd.execute(context)
    assert "No such file or directory" in str(exc.value)

# --- TouchCommand Tests ---

def test_touch_positive(context):
    cmd = TouchCommand("file.txt", "Hello VFS")
    cmd.execute(context)
    node = context.root.get_child("file.txt")
    assert isinstance(node, File)
    assert node.content == "Hello VFS"

def test_touch_negative_quota_exceeded(context):
    context.max_size = 5  # Very small disk
    cmd = TouchCommand("bigfile.txt", "This content is too long")
    with pytest.raises(VFSFileSystemException) as exc:
        cmd.execute(context)
    assert "Quota Exceeded" in str(exc.value)

# --- CdCommand Tests ---

def test_cd_positive(context):
    context.root.add_child(Directory("bin"))
    cmd = CdCommand("bin")
    cmd.execute(context)
    assert context.current_directory.name == "bin"

def test_cd_negative_not_a_directory(context):
    context.root.add_child(File("script.sh"))
    cmd = CdCommand("script.sh")
    with pytest.raises(VFSFileSystemException) as exc:
        cmd.execute(context)
    assert "Not a directory" in str(exc.value)

# --- LsCommand Tests ---

def test_ls_positive_list_dir(context):
    context.root.add_child(Directory("dir1"))
    context.root.add_child(File("file1"))
    cmd = LsCommand("")
    result = cmd.execute(context)
    assert len(result) == 2
    names = [node.name for node in result]
    assert "dir1" in names
    assert "file1" in names

def test_ls_negative_non_existent(context):
    cmd = LsCommand("missing_folder")
    with pytest.raises(VFSFileSystemException):
        cmd.execute(context)

# --- CatCommand Tests ---

def test_cat_positive(context):
    context.root.add_child(File("data.txt", content="Secret Data"))
    cmd = CatCommand("data.txt")
    result = cmd.execute(context)
    assert result == "Secret Data"

def test_cat_negative_is_directory(context):
    context.root.add_child(Directory("folder"))
    cmd = CatCommand("folder")
    with pytest.raises(VFSFileSystemException) as exc:
        cmd.execute(context)
    assert "Is a directory" in str(exc.value)

# --- ChmodCommand Tests ---

def test_chmod_positive(context):
    context.root.add_child(File("locked.txt"))
    cmd = ChmodCommand(0o777, "locked.txt")
    cmd.execute(context)
    assert context.root.get_child("locked.txt").permissions == 0o777

# --- ExitCommand Tests ---

def test_exit_execution():
    cmd = ExitCommand()
    with patch("sys.exit") as mock_exit:
        cmd.execute(None)
        mock_exit.assert_called_once_with(0)