import pytest
from unittest.mock import MagicMock
from src.context import VFSContext
from src.models import Directory

def test_context_initialization():
    """
    Positive test: Verify that a new context has a root directory,
    admin user, and starts at the root path.
    """
    ctx = VFSContext(max_size=1024)
    assert ctx.max_size == 1024
    assert ctx.current_user == "admin"
    assert ctx.root.name == "/"
    assert ctx.current_directory == ctx.root
    assert ctx.is_initialized() is True

def test_is_initialized_false():
    """
    Negative test: Context should not be considered initialized if max_size is 0.
    """
    ctx = VFSContext(max_size=0)
    assert ctx.is_initialized() is False

def test_get_used_space(mocker):
    """
    Mock test: Verify that get_used_space calls the root's get_size method.
    We mock the Directory to avoid dependency on real file objects.
    """
    ctx = VFSContext(max_size=1000)
    # Mocking the get_size method of the root directory
    mocker.patch.object(Directory, 'get_size', return_value=500)
    
    assert ctx.get_used_space() == 500

def test_has_enough_space_positive(mocker):
    """
    Positive test: Verify that has_enough_space returns True when 
    under the quota limit.
    """
    ctx = VFSContext(max_size=100)
    mocker.patch.object(Directory, 'get_size', return_value=40)
    
    # 40 (used) + 50 (extra) = 90. 90 <= 100 is True.
    assert ctx.has_enough_space(50) is True

def test_has_enough_space_negative(mocker):
    """
    Negative test: Verify that has_enough_space returns False when 
    the quota is exceeded.
    """
    ctx = VFSContext(max_size=100)
    mocker.patch.object(Directory, 'get_size', return_value=90)
    
    # 90 (used) + 20 (extra) = 110. 110 > 100 is False.
    assert ctx.has_enough_space(20) is False

def test_current_directory_change():
    """
    Positive test: Verify that the context can track a change in 
    the current working directory.
    """
    ctx = VFSContext(max_size=1024)
    new_dir = Directory(name="home", parent=ctx.root)
    ctx.current_directory = new_dir
    
    assert ctx.current_directory.name == "home"
    assert ctx.current_directory.parent == ctx.root