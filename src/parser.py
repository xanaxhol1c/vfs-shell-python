"""
The module contains class for parsing input with commands given from user.
Supports basic input or script.sh format.
Implements specific exception handling for parsing errors.
"""

import shlex
from typing import Optional, Dict, Callable
from src.commands import (
    ICommand,
    MkfsCommand,
    MkdirCommand,
    TouchCommand,
    CdCommand,
    ChmodCommand,
    LsCommand,
    CatCommand,
    ClsCommand,
    ExitCommand,
)
from src.exceptions import VFSSyntaxException, VFSValidationException


class InputParser:
    """
    Class responsible for converting input strings into executable command objects.
    """

    @staticmethod
    def parse(raw_input: str) -> Optional[ICommand]:
        """
        Converts a string to a command object using a dispatch table.
        Returns None if the string is empty or is a comment.
        Raises VFSSyntaxException or VFSValidationException on parsing errors.
        """
        line = raw_input.strip()

        # Ignore empty lines or comments
        if not line or line.startswith("#"):
            return None

        try:
            # Use shlex to handle tokens and quoted arguments properly
            tokens = shlex.split(line)
        except ValueError as e:
            raise VFSSyntaxException(f"Shell parsing error: {str(e)}") from e

        if not tokens:
            return None

        command_name = tokens[0].lower()
        args = tokens[1:]

        # Dispatch table mapping command strings to their respective factories
        factories: Dict[str, Callable[[list[str]], ICommand]] = {
            "mkfs": lambda a: MkfsCommand(max_size=int(a[0])),
            "mkdir": lambda a: MkdirCommand(path=a[0]),
            "touch": lambda a: TouchCommand(path=a[0], content=a[1] if len(a) > 1 else ""),
            "cd": lambda a: CdCommand(path=a[0]),
            "chmod": lambda a: ChmodCommand(permissions=int(a[0], 8), path=a[1]),
            "ls": lambda a: LsCommand(path=a[0] if a else ""),
            "cat": lambda a: CatCommand(path=a[0]),
            "cls": lambda _: ClsCommand(),
            "clear": lambda _: ClsCommand(),
            "exit": lambda _: ExitCommand(),
            "quit": lambda _: ExitCommand(),
        }

        if command_name not in factories:
            raise VFSSyntaxException(f"Command '{command_name}' is not supported")

        try:
            # Execute the factory lambda with the provided arguments
            return factories[command_name](args)

        except (IndexError, ValueError) as e:
            # Handle cases where arguments are missing or have incorrect types
            error_msg = f"Invalid arguments for '{command_name}': {str(e)}"
            raise VFSValidationException(error_msg) from e
