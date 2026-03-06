import pytest
from src.models import Directory, File
from src.exceptions import VFSFileSystemException, VFSValidationException # Added missing import

def test_directory_creation():
    root = Directory("root")
    assert root.name == "root"
    assert len(root.children) == 0

def test_add_child_conflict():
    root = Directory("root")
    root.add_child(Directory("docs"))
    # Now this will correctly catch VFSFileSystemException instead of ValueError
    with pytest.raises(VFSFileSystemException) as exc:
        root.add_child(File("docs"))
    assert "already exists" in str(exc.value).lower()

def test_invalid_characters():
    root = Directory("root")
    # Testing ?, *, \
    for char in ["?", "*", "\\"]:
        with pytest.raises(VFSValidationException):
            root.add_child(Directory(f"folder{char}"))