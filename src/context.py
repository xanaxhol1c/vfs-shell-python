"""
The module contains the execution context of the virtual file system.
"""

from src.models import Directory


class VFSContext:
    """
    Stores the global state of the file system: root, current directory, and quotas.
    """

    def __init__(self, max_size: int = 0) -> None:
        self.max_size: int = max_size

        # Creating root directory
        self.root: Directory = Directory(name="/", parent=None)

        # Firstly current directory - its root
        self.current_directory: Directory = self.root
        self.current_user = "admin"

    def is_initialized(self) -> bool:
        """Checks whether the mkfs command was invoked."""
        return self.max_size > 0

    def get_used_space(self) -> int:
        """Returns how much space is already occupied on the disk."""
        return self.root.get_size()

    def has_enough_space(self, extra_bytes: int) -> bool:
        """Checks whether there is enough space to record new data."""
        return (self.get_used_space() + extra_bytes) <= self.max_size
