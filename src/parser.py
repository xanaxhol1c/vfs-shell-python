"""
The module contains class for parsing input with commands given from user.
Supports basic input or script.sh format.
"""

import shlex
from typing import List, Optional
from src.commands import (
    ICommand, MkfsCommand, MkdirCommand, TouchCommand, 
    CdCommand, ChmodCommand, LsCommand, CatCommand
)

class InputParser:
    @staticmethod
    def parse(raw_input: str) -> Optional[ICommand]:
        """
        Converts a string to a command object. 
        Returns None if the string is empty or is a comment.
        """
        line = raw_input.strip()

        # check for comment or empty line
        if not line or line.startswith('#'):
            return None

        # Split line on tokens
        tokens = shlex.split(line)
        if not tokens:
            return None

        command_name = tokens[0].lower()
        args = tokens[1:]

        try:
            if command_name == "mkfs":
                return MkfsCommand(max_size=int(args[0]))
            elif command_name == "mkdir":
                return MkdirCommand(path=args[0])
            elif command_name == "touch":
                path = args[0]
                content = args[1] if len(args) > 1 else ""
                return TouchCommand(path=path, content=content)
            elif command_name == "cd":
                return CdCommand(path=args[0])
            elif command_name == "chmod":
                perms = int(args[0], 8)
                path = args[1]
                return ChmodCommand(permissions=perms, path=path)
            elif command_name == "ls":
                path = args[0] if args else ""
                return LsCommand(path=path)
            elif command_name == "cat":
                return CatCommand(path=args[0])
            else:
                raise ValueError(f"Команда '{command_name}' не підтримується")

        except IndexError:
            raise ValueError(f"Команді '{command_name}' бракує аргументів")