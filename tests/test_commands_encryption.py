"""
Unit tests for updated commands: TouchCommand and CatCommand.
Tests integration with encryption/compression decorators.
"""

import pytest
import json
import tempfile
import os
from src.commands import TouchCommand, CatCommand, MkdirCommand, get_node_by_path
from src.context import VFSContext
from src.config_manager import ConfigManager
from src.models import Directory, File
from src.decorators import EncryptedFileDecorator, CompressedFileDecorator
from src.exceptions import VFSFileSystemException


class TestTouchCommandWithEncryption:
    """Test TouchCommand creates encrypted files based on config."""

    @pytest.fixture
    def context_with_config(self):
        """Create context with encryption config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(config_data, f)

        config = ConfigManager(config_path)
        context = VFSContext(max_size=50000, config_manager=config)
        yield context
        try:
            os.unlink(config_path)
        except:
            pass

    def test_touch_creates_encrypted_file_in_secret_directory(self, context_with_config):
        """TouchCommand should create encrypted file in /secret."""
        # Setup
        mkdir_cmd = MkdirCommand(path="/secret")
        mkdir_cmd.execute(context_with_config)

        # Create encrypted file
        touch_cmd = TouchCommand(path="/secret/file.txt", content="secret data")
        touch_cmd.execute(context_with_config)

        # Verify file is encrypted
        secret_dir = get_node_by_path(context_with_config, "/secret")
        file_node = secret_dir.get_child("file.txt")

        assert isinstance(file_node, EncryptedFileDecorator)
        assert file_node.read() == "secret data"

    def test_touch_creates_compressed_file_in_archive_directory(self, context_with_config):
        """TouchCommand should create compressed file in /archive."""
        # Setup
        mkdir_cmd = MkdirCommand(path="/archive")
        mkdir_cmd.execute(context_with_config)

        # Create compressed file
        touch_cmd = TouchCommand(path="/archive/log.txt", content="hello    spaces")
        touch_cmd.execute(context_with_config)

        # Verify file is compressed
        archive_dir = get_node_by_path(context_with_config, "/archive")
        file_node = archive_dir.get_child("log.txt")

        assert isinstance(file_node, CompressedFileDecorator)
        assert file_node.read() == "hello spaces"

    def test_touch_creates_encrypted_and_compressed_in_secure(self, context_with_config):
        """TouchCommand should create decorated file in /secure."""
        # Setup
        mkdir_cmd = MkdirCommand(path="/secure")
        mkdir_cmd.execute(context_with_config)

        # Create file with both decorators
        touch_cmd = TouchCommand(path="/secure/data.txt", content="data   here")
        touch_cmd.execute(context_with_config)

        # Verify file has both decorators
        secure_dir = get_node_by_path(context_with_config, "/secure")
        file_node = secure_dir.get_child("data.txt")

        assert isinstance(file_node, CompressedFileDecorator)
        assert file_node.read() == "data here"

    def test_touch_creates_plain_file_when_no_config(self):
        """TouchCommand should create plain File when no config."""
        context = VFSContext(max_size=50000)  # No config_manager
        touch_cmd = TouchCommand(path="/file.txt", content="data")
        touch_cmd.execute(context)

        file_node = get_node_by_path(context, "/file.txt")
        assert type(file_node).__name__ == "File"
        assert file_node.read() == "data"

    def test_touch_uses_fallback_when_no_matching_rules(self):
        """TouchCommand should create plain file when no rules match."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {"rules": [{"path": "/secret", "decorators": ["encrypted"]}]}
            json.dump(config_data, f)

        try:
            config = ConfigManager(config_path)
            context = VFSContext(max_size=50000, config_manager=config)

            # Create /regular directory first
            mkdir_cmd = MkdirCommand(path="/regular")
            mkdir_cmd.execute(context)

            # Create file in unmapped directory
            touch_cmd = TouchCommand(path="/regular/file.txt", content="data")
            touch_cmd.execute(context)

            file_node = get_node_by_path(context, "/regular/file.txt")
            assert type(file_node).__name__ == "File"
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_touch_respects_configured_path_prefix(self, context_with_config):
        """TouchCommand should apply rules based on parent directory."""
        # Setup directories
        mkdir_cmd = MkdirCommand(path="/secret")
        mkdir_cmd.execute(context_with_config)

        mkdir_cmd = MkdirCommand(path="/secret/subdir")
        mkdir_cmd.execute(context_with_config)

        # Create file in nested directory that matches rule
        touch_cmd = TouchCommand(path="/secret/subdir/nested.txt", content="nested secret")
        touch_cmd.execute(context_with_config)

        # Verify file in /secret/subdir is encrypted (path starts with /secret)
        file_node = get_node_by_path(context_with_config, "/secret/subdir/nested.txt")
        assert isinstance(file_node, EncryptedFileDecorator)


class TestCatCommandWithEncryption:
    """Test CatCommand reads encrypted files transparently."""

    @pytest.fixture
    def context_with_encrypted_file(self):
        """Create context with encrypted file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {
                "rules": [{"path": "/secret", "decorators": ["encrypted"]}]
            }
            json.dump(config_data, f)

        config = ConfigManager(config_path)
        context = VFSContext(max_size=50000, config_manager=config)

        # Create secret directory
        secret_dir = Directory(name="secret", parent=context.root)
        context.root.add_child(secret_dir)

        # Create encrypted file directly
        from src.factory import FileFactory
        encrypted_file = FileFactory.create_file(
            name="secret.txt",
            parent_path="/secret",
            config_manager=config,
            content="top secret"
        )
        secret_dir.add_child(encrypted_file)

        yield context
        try:
            os.unlink(config_path)
        except:
            pass

    def test_cat_reads_encrypted_file_transparently(self, context_with_encrypted_file):
        """CatCommand should read encrypted file and return plaintext."""
        cat_cmd = CatCommand(path="/secret/secret.txt")
        result = cat_cmd.execute(context_with_encrypted_file)

        assert result == "top secret"

    def test_cat_reads_plain_file(self):
        """CatCommand should read plain files normally."""
        context = VFSContext(max_size=50000)
        from src.factory import FileFactory

        # Create plain file
        plain_file = FileFactory.create_file(
            name="plain.txt",
            parent_path="/",
            config_manager=None,
            content="plain text"
        )
        context.root.add_child(plain_file)

        cat_cmd = CatCommand(path="/plain.txt")
        result = cat_cmd.execute(context)

        assert result == "plain text"

    def test_cat_uses_read_method_on_decorated_files(self):
        """CatCommand should call .read() method for transparent decryption."""
        context = VFSContext(max_size=50000)

        # Create encrypted file manually
        plain = File(name="test.txt", content="")
        encrypted = EncryptedFileDecorator(plain)
        encrypted.write("encrypted content")
        context.root.add_child(encrypted)

        cat_cmd = CatCommand(path="/test.txt")
        result = cat_cmd.execute(context)

        # Should get decrypted content
        assert result == "encrypted content"

    def test_cat_with_compressed_file(self):
        """CatCommand should handle compressed files."""
        context = VFSContext(max_size=50000)

        # Create compressed file
        plain = File(name="log.txt", content="")
        compressed = CompressedFileDecorator(plain)
        compressed.write("log    with    spaces")
        context.root.add_child(compressed)

        cat_cmd = CatCommand(path="/log.txt")
        result = cat_cmd.execute(context)

        # Should get decompressed content
        assert result == "log with spaces"

    def test_cat_with_both_decorators(self):
        """CatCommand should handle files with both encryption and compression."""
        context = VFSContext(max_size=50000)

        # Create file with both decorators
        plain = File(name="secure.txt", content="")
        encrypted = EncryptedFileDecorator(plain)
        compressed = CompressedFileDecorator(encrypted)
        compressed.write("secure    data")
        context.root.add_child(compressed)

        cat_cmd = CatCommand(path="/secure.txt")
        result = cat_cmd.execute(context)

        # Should get both decrypted and decompressed
        assert result == "secure data"

    def test_cat_returns_string_type(self):
        """CatCommand should return string result."""
        context = VFSContext(max_size=50000)
        from src.factory import FileFactory

        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/",
            config_manager=None,
            content="content"
        )
        context.root.add_child(file)

        cat_cmd = CatCommand(path="/test.txt")
        result = cat_cmd.execute(context)

        assert isinstance(result, str)


class TestCommandsWithContextConfig:
    """Test commands properly access config_manager from context."""

    def test_context_provides_config_manager_to_commands(self):
        """Context should pass config_manager to commands."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            config_data = {
                "rules": [{"path": "/secret", "decorators": ["encrypted"]}]
            }
            json.dump(config_data, f)

        try:
            config = ConfigManager(config_path)
            context = VFSContext(max_size=50000, config_manager=config)

            # Create secret directory
            secret_dir = Directory(name="secret", parent=context.root)
            context.root.add_child(secret_dir)

            # TouchCommand should access context.config_manager
            touch_cmd = TouchCommand(path="/secret/test.txt", content="data")
            touch_cmd.execute(context)

            # File should be encrypted because context has config
            file_node = get_node_by_path(context, "/secret/test.txt")
            assert isinstance(file_node, EncryptedFileDecorator)
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_context_without_config_disables_encryption(self):
        """Context without config_manager should disable encryption."""
        context = VFSContext(max_size=50000)  # No config_manager

        touch_cmd = TouchCommand(path="/file.txt", content="data")
        touch_cmd.execute(context)

        file_node = get_node_by_path(context, "/file.txt")
        # Should be plain File, not decorated
        assert type(file_node).__name__ == "File"
        assert not isinstance(file_node, EncryptedFileDecorator)
