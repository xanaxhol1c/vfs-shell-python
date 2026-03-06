import pytest
from unittest.mock import MagicMock
from src.security import SecurityEngine
from src.models import INode

@pytest.fixture
def security():
    return SecurityEngine()

# --- Command Mapping Tests ---

def test_get_required_access_mapping(security):
    """Verify that commands are correctly mapped to READ/WRITE/EXECUTE bits."""
    assert security.get_required_access("ls") == security.READ
    assert security.get_required_access("cat") == security.READ
    assert security.get_required_access("mkdir") == security.WRITE
    assert security.get_required_access("touch") == security.WRITE
    assert security.get_required_access("cd") == security.EXECUTE
    assert security.get_required_access("unknown") == 0

# --- Access Logic Tests ---

def test_admin_has_full_access(security):
    """Positive test: Admin should always return True regardless of node permissions."""
    mock_node = MagicMock(spec=INode)
    mock_node.permissions = 0o000  # No permissions at all
    
    assert security.has_access(mock_node, "admin", security.WRITE) is True
    assert security.has_access(mock_node, "admin", security.READ) is True

def test_guest_access_bitwise_logic(security):
    """
    Fixed: Use decimal 755 so that 755 % 10 equals 5.
    """
    mock_node = MagicMock(spec=INode)

    # Use 755 (Decimal) -> 755 % 10 = 5 (Read + Execute)
    mock_node.permissions = 755 

    # Now 5 & 4 == 4 (True)
    assert security.has_access(mock_node, "guest", security.READ) is True
    # 5 & 1 == 1 (True)
    assert security.has_access(mock_node, "guest", security.EXECUTE) is True
    # 5 & 2 == 2 (False)
    assert security.has_access(mock_node, "guest", security.WRITE) is False

def test_no_access_guest(security):
    """
    Fixed: Use decimal 700 -> 700 % 10 = 0.
    """
    mock_node = MagicMock(spec=INode)
    mock_node.permissions = 700 
    
    assert security.has_access(mock_node, "guest", security.READ) is False

def test_exact_match_required(security):
    """
    Verify that if multiple permissions are required (hypothetically), 
    the engine checks for all of them.
    """
    mock_node = MagicMock(spec=INode)
    mock_node.permissions = 0o704 # Others have READ (4)
    
    # Needs READ and WRITE (4+2=6)
    required = security.READ | security.WRITE 
    assert security.has_access(mock_node, "guest", required) is False