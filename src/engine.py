"""
Command execution orchestrator.
"""

from src.context import VFSContext
from src.parser import InputParser
from src.formatter import OutputFormatter
from src.security import SecurityEngine


class ExecutionEngine:
    def __init__(self, context: VFSContext, formatter: OutputFormatter) -> None:
        self.context = context
        self.formatter = formatter
        self.parser = InputParser()
        self.security = SecurityEngine()

    def run(self, raw_line: str) -> None:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            if line.startswith("#"):
                self.formatter.render_comment(line)
            return

        try:
            command = self.parser.parse(line)
            if not command:
                return

            # MVP Security Check
            cmd_name = line.split()[0].lower()
            required = self.security.get_required_access(cmd_name)

            # Checking access to current directory to allow actions
            if not self.security.has_access(
                self.context.current_directory, self.context.current_user, required
            ):
                raise PermissionError(
                    f"Permission denied: user '{self.context.current_user}' "
                    f"cannot execute '{cmd_name}' here."
                )

            self.formatter.render_command_echo(line)
            result = command.execute(self.context)
            self.formatter.render_result(result)

        except PermissionError as e:
            self.formatter.render_error(str(e))
        except Exception as e:
            self.formatter.render_error(str(e))
