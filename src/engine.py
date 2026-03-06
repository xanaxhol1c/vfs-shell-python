"""
Pure Command Execution Engine.
"""

from src.context import VFSContext
from src.formatter import OutputFormatter
from src.security import SecurityEngine
from src.commands import ICommand


class ExecutionEngine:
    def __init__(self, context: VFSContext, formatter: OutputFormatter) -> None:
        self.context = context
        self.formatter = formatter
        self.security = SecurityEngine()

    def execute(self, command: ICommand, raw_line: str) -> None:
        try:
            # Identifying command name
            cmd_name = raw_line.split(maxsplit=1)[0].lower()

            required_access = self.security.get_required_access(cmd_name)

            # security check
            if not self.security.has_access(
                self.context.current_directory, self.context.current_user, required_access
            ):
                raise PermissionError(f"Access denied for '{cmd_name}'")

            # visualization and execution
            self.formatter.render_command_echo(raw_line)
            result = command.execute(self.context)
            self.formatter.render_result(result)

        except Exception as e:
            self.formatter.render_error(str(e))
