import pytest
import json
import tempfile
import os
from unittest.mock import MagicMock
from src.context import VFSContext
from src.models import Directory
from src.config_manager import ConfigManager

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


class TestVFSContextWithConfigManager:
    """Test VFSContext integration with ConfigManager."""

    def test_context_initialization_without_config(self):
        """Context should initialize without ConfigManager."""
        ctx = VFSContext(max_size=1000)
        assert ctx.config_manager is None

    def test_context_initialization_with_config(self):
        """Context should accept and store ConfigManager."""
        config = ConfigManager("nonexistent_file.json")
        ctx = VFSContext(max_size=1000, config_manager=config)

        assert ctx.config_manager is not None
        assert ctx.config_manager == config

    def test_context_with_valid_config_file(self):
        """Context should work with valid ConfigManager pointing to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {
                "rules": [{"path": "/secret", "decorators": ["encrypted"]}]
            }
            json.dump(config_data, f)

        try:
            config = ConfigManager(config_path)
            ctx = VFSContext(max_size=1000, config_manager=config)

            assert ctx.config_manager is not None
            assert len(ctx.config_manager.rules) == 1
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_context_preserves_existing_functionality_with_config(self):
        """Adding ConfigManager should not break existing VFSContext methods."""
        config = ConfigManager("nonexistent_file.json")
        ctx = VFSContext(max_size=1000, config_manager=config)

        # Verify all original functionality still works
        assert ctx.max_size == 1000
        assert ctx.is_initialized() is True
        assert ctx.current_user == "admin"
        assert ctx.root.name == "/"
        assert ctx.current_directory == ctx.root

    def test_context_commands_can_access_config(self):
        """Commands executing in context should access config_manager."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {
                "rules": [{"path": "/secret", "decorators": ["encrypted"]}]
            }
            json.dump(config_data, f)

        try:
            config = ConfigManager(config_path)
            ctx = VFSContext(max_size=1000, config_manager=config)

            # Verify context has config accessible
            assert ctx.config_manager is not None
            decorators = ctx.config_manager.get_decorators_for_path("/secret/file.txt")
            assert decorators == ["encrypted"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_context_supports_none_config_for_backward_compatibility(self):
        """Context should work fine with config_manager=None."""
        # Old way: no parameter
        ctx1 = VFSContext(max_size=1000)
        assert ctx1.config_manager is None

        # New way: explicit None
        ctx2 = VFSContext(max_size=1000, config_manager=None)
        assert ctx2.config_manager is None

        # Both should work identically
        assert ctx1.is_initialized() == ctx2.is_initialized()
        assert ctx1.max_size == ctx2.max_size

    def test_context_config_parameter_is_optional(self):
        """config_manager parameter should be optional with default None."""
        # Should not raise any errors
        ctx = VFSContext(max_size=1000)
        assert ctx.config_manager is None

        # Explicit None should work
        ctx2 = VFSContext(max_size=1000, config_manager=None)
        assert ctx2.config_manager is None