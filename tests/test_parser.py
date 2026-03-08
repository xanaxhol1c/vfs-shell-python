import pytest
from src.parser import InputParser
from src.commands import MkdirCommand, LsCommand
from src.exceptions import VFSSyntaxException, VFSValidationException

def test_parser_positive():
    cmd = InputParser.parse("mkdir /home/user")
    assert isinstance(cmd, MkdirCommand)
    assert cmd.path == "/home/user"

def test_parser_unknown_command():
    # Negative test: Syntax error
    with pytest.raises(VFSSyntaxException):
        InputParser.parse("unknown_cmd args")

def test_parser_missing_args():
    # Negative test: Validation error (mkfs needs size)
    with pytest.raises(VFSValidationException):
        InputParser.parse("mkfs")