import pytest
from unittest.mock import MagicMock
from src.engine import ExecutionEngine
from src.exceptions import VFSSecurityException, VFSFileSystemException

@pytest.fixture
def setup_engine(mocker):
    """Fixture to initialize engine with mocked dependencies."""
    mock_context = MagicMock()
    mock_formatter = MagicMock()
    
    # We mock the internal SecurityEngine to control access logic
    mock_security = mocker.patch("src.engine.SecurityEngine")
    
    engine = ExecutionEngine(mock_context, mock_formatter)
    return engine, mock_context, mock_formatter, mock_security.return_value

# --- Positive Tests ---

def test_engine_successful_execution(setup_engine):
    """
    Positive test: Verify that the engine coordinates the full lifecycle
    of a command when security checks pass.
    """
    engine, mock_context, mock_formatter, mock_security = setup_engine
    mock_command = MagicMock()
    mock_command.execute.return_value = "Success"
    
    # Setup: Access is granted
    mock_security.get_required_access.return_value = 7
    mock_security.has_access.return_value = True
    
    engine.execute(mock_command, "mkdir test_dir")
    
    # Assertions: Verify the sequence of calls
    mock_formatter.render_command_echo.assert_called_once_with("mkdir test_dir")
    mock_command.execute.assert_called_once_with(mock_context)
    mock_formatter.render_result.assert_called_once_with("Success")

# --- Negative Tests ---

def test_engine_security_denial(setup_engine):
    """
    Negative test: Verify that the engine raises VFSSecurityException
    and stops execution if security check fails.
    """
    engine, mock_context, mock_formatter, mock_security = setup_engine
    mock_command = MagicMock()
    
    # Setup: Access is denied
    mock_security.has_access.return_value = False
    
    with pytest.raises(VFSSecurityException) as exc:
        engine.execute(mock_command, "touch private.txt")
    
    assert "Access denied" in str(exc.value)
    # Crucial: Command must NOT be executed if security fails
    mock_command.execute.assert_not_called()
    mock_formatter.render_result.assert_not_called()

def test_engine_command_failure_propagation(setup_engine):
    """
    Negative test: Verify that exceptions raised inside the command
    propagate through the engine to the caller (main.py).
    """
    engine, mock_context, mock_formatter, mock_security = setup_engine
    mock_command = MagicMock()
    
    # Setup: Security passes, but command logic fails (e.g., dir exists)
    mock_security.has_access.return_value = True
    mock_command.execute.side_effect = VFSFileSystemException("Already exists")
    
    with pytest.raises(VFSFileSystemException):
        engine.execute(mock_command, "mkdir duplicate")
        
    # Result should not be rendered if command failed
    mock_formatter.render_result.assert_not_called()

# --- Edge Cases ---

def test_engine_handles_empty_args_string(setup_engine):
    """
    Edge case: Verify engine can parse a command name from a single-word string.
    """
    engine, _, _, mock_security = setup_engine
    mock_command = MagicMock()
    mock_security.has_access.return_value = True
    
    # Testing "ls" without arguments
    engine.execute(mock_command, "ls")
    
    # Ensure get_required_access was called with "ls"
    mock_security.get_required_access.assert_called_with("ls")