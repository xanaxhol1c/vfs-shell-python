"""
Security engine for checking file system permissions.
"""
from src.models import INode, Directory, File

class SecurityEngine:
    # Constants for checks
    READ = 4
    WRITE = 2
    EXECUTE = 1

    def has_access(self, node: INode, user: str, required_access: int) -> bool:
        """
        Checks whether the user has access to the node.
        MVP: admin has access to everything, others — according to permissions.
        """
        if user == "admin":
            return True

        # Get permissions (e.g., 755 -> last digit 5 for ‘others’)
        # Simplified approach: take the last digit (rights for everyone)
        others_permissions = node.permissions % 10
        
        # Checking with bitwise 'AND'
        return (others_permissions & required_access) == required_access

    def get_required_access(self, command_name: str) -> int:
        """Determines what level of access the team needs."""
        read_commands = {'ls', 'cat', 'pwd'}
        write_commands = {'mkdir', 'touch', 'rm', 'chmod'}
        execute_commands = {'cd'}

        if command_name in read_commands:
            return self.READ
        if command_name in write_commands:
            return self.WRITE
        if command_name in execute_commands:
            return self.EXECUTE
        return 0