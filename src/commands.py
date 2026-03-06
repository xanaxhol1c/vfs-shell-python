"""
The module contains the ICommand interface and implementations of specific commands (MVP).
Implements the Command pattern with Defensive Programming principles.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
import os
import sys

from src.models import INode, Directory, File
from src.context import VFSContext
from src.types import CommandResult
from src.exceptions import VFSFileSystemException, VFSValidationException

# Help functions for path resolution

def get_node_by_path(context: VFSContext, path: str) -> Optional[INode]:
    """
    Travels through VFS tree based on path line.
    Uses stack logic for processing of relative and absolute paths.
    """
    if path == "/":
        return context.root

    # Getting start point: root or current folder
    current: INode = context.root if path.startswith("/") else context.current_directory

    parts = path.split("/")
    for part in parts:
        if not part or part == ".":
            continue  # Current dir, continue

        if part == "..":
            # Going up if it's not root
            if current.parent is not None:
                current = current.parent
            continue

        if isinstance(current, Directory):
            child = current.get_child(part)
            if not child:
                return None  # Path crashed (node not found)
            current = child
        else:
            return None  # Trying to get inside a file

    return current


def get_parent_and_name(context: VFSContext, path: str) -> Tuple[Optional[Directory], str]:
    """
    Splits path to 'parent directory' and 'name of last file/folder'.
    Needed for mkdir and touch commands.
    """
    if "/" not in path:
        return context.current_directory, path

    parts = path.rsplit("/", 1)
    parent_path = parts[0] if parts[0] else "/"
    name = parts[1]

    parent_node = get_node_by_path(context, parent_path)
    if isinstance(parent_node, Directory):
        return parent_node, name
    return None, name


class ICommand(ABC):
    """Abstract interface for all system commands."""

    @abstractmethod
    def execute(self, context: VFSContext) -> CommandResult:
        """
        Executes action in the given context.
        Returns data to print or None.
        Raises VFSBaseException derivatives on failure.
        """
        pass


class MkfsCommand(ICommand):
    def __init__(self, max_size: int) -> None:
        self.max_size = max_size

    def execute(self, context: VFSContext) -> str:
        if self.max_size <= 0:
            raise VFSValidationException("mkfs: disk size must be greater than 0")
        
        context.max_size = self.max_size
        return f"The virtual file system has been initialized. Size: {self.max_size} bytes."


class MkdirCommand(ICommand):
    def __init__(self, path: str) -> None:
        self.path = path

    def execute(self, context: VFSContext) -> None:
        parent, name = get_parent_and_name(context, self.path)
        if not parent:
            raise VFSFileSystemException(f"mkdir: cannot create '{self.path}': No such file or directory")

        new_dir = Directory(name=name)
        parent.add_child(new_dir)


class TouchCommand(ICommand):
    def __init__(self, path: str, content: str = "") -> None:
        self.path = path
        self.content = content

    def execute(self, context: VFSContext) -> None:
        # MVP quota check before write
        if context.is_initialized() and not context.has_enough_space(len(self.content)):
            raise VFSFileSystemException("touch: No free space on device (Quota Exceeded)")

        parent, name = get_parent_and_name(context, self.path)
        if not parent:
            raise VFSFileSystemException(f"touch: cannot create '{self.path}': No such directory")

        new_file = File(name=name, content=self.content)
        parent.add_child(new_file)



class CdCommand(ICommand):
    def __init__(self, path: str) -> None:
        self.path = path

    def execute(self, context: VFSContext) -> None:
        node = get_node_by_path(context, self.path)
        if not node:
            raise VFSFileSystemException(f"cd: {self.path}: No such file or directory")
        if not isinstance(node, Directory):
            raise VFSFileSystemException(f"cd: {self.path}: Not a directory")

        context.current_directory = node


class ChmodCommand(ICommand):
    def __init__(self, permissions: int, path: str) -> None:
        self.permissions = permissions
        self.path = path

    def execute(self, context: VFSContext) -> None:
        node = get_node_by_path(context, self.path)
        if not node:
            raise VFSFileSystemException(f"chmod: cannot access '{self.path}': No such file or directory")

        node.permissions = self.permissions


class LsCommand(ICommand):
    def __init__(self, path: str = "") -> None:
        self.path = path

    def execute(self, context: VFSContext) -> List[INode]:
        target_path = self.path if self.path else "."
        node = get_node_by_path(context, target_path)

        if not node:
            raise VFSFileSystemException(f"ls: cannot access '{self.path}': No such file or directory")

        if isinstance(node, File):
            return [node]

        # If directory, return list of child elements
        return list(node.children.values())


class CatCommand(ICommand):
    def __init__(self, path: str) -> None:
        self.path = path

    def execute(self, context: VFSContext) -> str:
        node = get_node_by_path(context, self.path)

        if not node:
            raise VFSFileSystemException(f"cat: {self.path}: No such file or directory")
        if isinstance(node, Directory):
            raise VFSFileSystemException(f"cat: {self.path}: Is a directory")

        return node.content


class ClsCommand(ICommand):
    """Cleans terminal window"""

    def execute(self, context: VFSContext) -> bool:
        # 'cls' for Windows, 'clear' for POSIX (Linux/Mac)
        os.system("cls" if os.name == "nt" else "clear")
        return True


class ExitCommand(ICommand):
    """Program exit."""

    def execute(self, context: VFSContext) -> None:
        print("End of the VFS session...")
        # uses default system exit
        sys.exit(0)