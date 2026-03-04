"""
Command execution orchestrator.
"""
from src.context import VFSContext
from src.parser import InputParser
from src.formatter import OutputFormatter

class ExecutionEngine:
    def __init__(self, context: VFSContext, formatter: OutputFormatter):
        self.context = context
        self.formatter = formatter
        self.parser = InputParser()

    def run(self, raw_line: str) -> None:
        line = raw_line.strip()
        
        # print for comments
        if line.startswith('#'):
            print(f"\n\033[90m{line}\033[0m")  # grey collor
            return

        try:
            # Parser returns None for empty lines or comments
            command = self.parser.parse(line)
            
            if command is None:
                return

            # If there is a command, print it and execute it
            print(f"\n> {line}")
            result = command.execute(self.context)
            self.formatter.render_result(result)

        except Exception as e:
            self.formatter.render_error(str(e))