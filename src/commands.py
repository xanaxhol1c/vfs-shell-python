"""
The module contains the ICommand interface and implementations of specific commands (MVP).
Implements the Command pattern.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, List

from src.models import INode, Directory, File
from src.context import VFSContext


# help functions for path resolution

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
            # Going up if its not root
            if current.parent is not None:
                current = current.parent
            continue
            
        if isinstance(current, Directory):
            child = current.get_child(part)
            if not child:
                return None  # Path crashed
            current = child
        else:
            return None  # Trying to get inside file
            
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
    def execute(self, context: VFSContext) -> Any:
        """
        Does action in given context.
        Returns data to print or None.
        """
        pass


class MkfsCommand(ICommand):
    def __init__(self, max_size: int):
        self.max_size = max_size

    def execute(self, context: VFSContext) -> str:
        context.max_size = self.max_size
        return f"Файлову систему ініціалізовано. Розмір: {self.max_size} байт."


class MkdirCommand(ICommand):
    def __init__(self, path: str):
        self.path = path

    def execute(self, context: VFSContext) -> None:
        parent, name = get_parent_and_name(context, self.path)
        if not parent:
            raise ValueError(f"mkdir: неможливо створити '{self.path}': Немає такого файлу або каталогу")
        
        new_dir = Directory(name=name)
        parent.add_child(new_dir)


class TouchCommand(ICommand):
    def __init__(self, path: str, content: str = ""):
        self.path = path
        self.content = content

    def execute(self, context: VFSContext) -> None:
        # MVP quota check before write
        if context.is_initialized() and not context.has_enough_space(len(self.content)):
            raise ValueError("touch: Немає вільного місця на пристрої (Quota Exceeded)")

        parent, name = get_parent_and_name(context, self.path)
        if not parent:
            raise ValueError(f"touch: неможливо створити '{self.path}': Немає такого каталогу")
        
        new_file = File(name=name, content=self.content)
        parent.add_child(new_file)


class CdCommand(ICommand):
    def __init__(self, path: str):
        self.path = path

    def execute(self, context: VFSContext) -> None:
        node = get_node_by_path(context, self.path)
        if not node:
            raise ValueError(f"cd: {self.path}: Немає такого файлу або каталогу")
        if not isinstance(node, Directory):
            raise ValueError(f"cd: {self.path}: Не є каталогом")
            
        context.current_directory = node


class ChmodCommand(ICommand):
    def __init__(self, permissions: int, path: str):
        self.permissions = permissions
        self.path = path

    def execute(self, context: VFSContext) -> None:
        node = get_node_by_path(context, self.path)
        if not node:
            raise ValueError(f"chmod: неможливо отримати доступ до '{self.path}': Немає такого файлу або каталогу")
        
        node.permissions = self.permissions


class LsCommand(ICommand):
    def __init__(self, path: str = ""):
        self.path = path

    def execute(self, context: VFSContext) -> List[INode]:
        target_path = self.path if self.path else "."
        node = get_node_by_path(context, target_path)
        
        if not node:
            raise ValueError(f"ls: неможливо отримати доступ до '{self.path}': Немає такого файлу або каталогу")
            
        if isinstance(node, File):
            return [node]
            
        # If directory, return list of child elements
        return list(node.children.values())


class CatCommand(ICommand):
    def __init__(self, path: str):
        self.path = path

    def execute(self, context: VFSContext) -> str:
        node = get_node_by_path(context, self.path)
        
        if not node:
            raise ValueError(f"cat: {self.path}: Немає такого файлу або каталогу")
        if isinstance(node, Directory):
            raise ValueError(f"cat: {self.path}: Є каталогом")
            
        return node.content