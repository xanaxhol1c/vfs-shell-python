"""
Pure Command Execution Engine.
Coordinates security checks and command execution.
"""

from src.context import VFSContext
from src.formatter import OutputFormatter
from src.security import SecurityEngine
from src.commands import ICommand
from src.exceptions import VFSSecurityException


class ExecutionEngine:
    def __init__(self, context: VFSContext, formatter: OutputFormatter) -> None:
        """
        Initializes the engine with system context and output formatter.
        """
        self.context = context
        self.formatter = formatter
        self.security = SecurityEngine()

    def execute(self, command: ICommand, raw_line: str) -> None:
        """
        Handles the lifecycle of a single command execution.
        Security checks are performed before calling the command's logic.
        Exceptions are allowed to propagate to the caller for centralized error handling.
        """
        # Identifying command name from the raw input string
        cmd_name = raw_line.split(maxsplit=1)[0].lower()

        # Retrieve the required access level for this specific command
        required_access = self.security.get_required_access(cmd_name)

        # Perform a POSIX-style security check
        if not self.security.has_access(
            self.context.current_directory, self.context.current_user, required_access
        ):
            raise VFSSecurityException(
                f"Access denied: user '{self.context.current_user}' "
                f"lacks permissions to execute '{cmd_name}'"
            )

        # Visual feedback of the command being processed
        self.formatter.render_command_echo(raw_line)

        # Command execution and result rendering
        # result may raise VFSFileSystemException or VFSValidationException
        result = command.execute(self.context)
        self.formatter.render_result(result)
