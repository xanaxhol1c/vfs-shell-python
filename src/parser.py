"""
The module contains class for parsing input with commands given from user.
Supports basic input or script.sh format.
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


class InputParser:
    """
    Класс для перетворення вхідних рядків у об'єкти команд.
    """

    @staticmethod
    def parse(raw_input: str) -> Optional[ICommand]:
        """
        Converts a string to a command object.
        Returns None if the string is empty or is a comment.
        """
        line = raw_input.strip()

        # check for comment or empty line
        if not line or line.startswith("#"):
            return None

        # Split line on tokens
        tokens = shlex.split(line)

        if not tokens:
            return None

        command_name = tokens[0].lower()
        args = tokens[1:]

        # Define factories for each command
        # Each lambda takes a list of arguments and returns a command object
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

        try:
            if command_name not in factories:
                raise ValueError(f"Command '{command_name}' is not supported")

            return factories[command_name](args)

        except (IndexError, ValueError) as e:
            # If an error occurs in lambda (for example, int(a[0]) with an empty list)
            raise ValueError(f"Invalid arguments for {command_name}: {e}") from e
