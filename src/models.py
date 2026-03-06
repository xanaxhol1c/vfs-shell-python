"""
The module contains classes for representing the virtual file system (VFS).
It implements the Composite pattern for unified work with files and directories.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from src.exceptions import VFSFileSystemException, VFSValidationException

class INode(ABC):
    """
    Abstract base class for all file system elements.
    """

    def __init__(
        self, name: str, parent: Optional["Directory"] = None, permissions: int = 0o777
    ) -> None:
        self.name: str = name
        self.parent: Optional["Directory"] = parent
        self.permissions: int = permissions

    @abstractmethod
    def get_size(self) -> int:
        """Returns the size of the node in bytes."""
        pass

    def get_path(self) -> str:
        """
        Recursively builds the absolute path to the current node.
        """
        if self.parent is None:
            return self.name if self.name == "/" else f"/{self.name}"

        parent_path = self.parent.get_path()
        if parent_path == "/":
            return f"/{self.name}"
        return f"{parent_path}/{self.name}"


class File(INode):
    """
    A class representing a text file in VFS.
    """

    def __init__(
        self,
        name: str,
        content: str = "",
        parent: Optional["Directory"] = None,
        permissions: int = 0o644,
    ) -> None:
        # Files have default permissions of 644 (rw-r--r--)
        super().__init__(name, parent, permissions)
        self.content: str = content

    def get_size(self) -> int:
        """
        Returns the file size.
        For MVP, we consider 1 character = 1 byte.
        """
        return len(self.content)


class Directory(INode):
    """
    A class representing a directory in VFS.
    Contains a dictionary of child elements for fast O(1) access.
    """

    def __init__(
        self, name: str, parent: Optional["Directory"] = None, permissions: int = 0o755
    ) -> None:
        # Directories have default permissions of 755 (rwxr-xr-x)
        super().__init__(name, parent, permissions)
        self.children: Dict[str, INode] = {}

    def get_size(self) -> int:
        """
        Recursively calculates the total size of all embedded files and folders.
        """
        return sum(child.get_size() for child in self.children.values())

    def add_child(self, node: INode) -> None:   
        """Adds new node to directory with name and character validation."""
        # check for invalid characters
        forbidden_chars = ["?", "*", "\\"]
        if any(char in node.name for char in forbidden_chars):
            raise VFSValidationException(
                f"Invalid characters in name '{node.name}'. "
                f"Symbols ?, *, \\ are forbidden."
            )

        # check for name conflicts
        if node.name in self.children:
            raise VFSFileSystemException(
                f"Element with name '{node.name}' already exists in this directory."
            )
        
        self.children[node.name] = node
        node.parent = self

    def remove_child(self, name: str) -> None:
        """Removes node from directory based on name."""
        if name not in self.children:
            raise KeyError(f"Element '{name}' not found")
        del self.children[name]

    def get_child(self, name: str) -> Optional[INode]:
        """Returns the child node by name or None if it does not exist."""
        return self.children.get(name)
