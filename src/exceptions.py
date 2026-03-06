"""
Custom exception hierarchy for the Virtual File System.
"""

class VFSBaseException(Exception):
    """Base exception for all VFS-related errors."""
    pass

class VFSSyntaxException(VFSBaseException):
    """Raised when the parser encounters invalid syntax or unknown commands."""
    pass

class VFSValidationException(VFSBaseException):
    """Raised when command arguments are invalid (e.g., wrong types or missing arguments)."""
    pass

class VFSFileSystemException(VFSBaseException):
    """Raised when a file system operation fails (e.g., file not found, disk full)."""
    pass

class VFSSecurityException(VFSBaseException):
    """Raised when a user lacks permissions to perform an action."""
    pass