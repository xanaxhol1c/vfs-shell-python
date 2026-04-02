"""
Unit tests for FileFactory.
Tests file creation with appropriate decorators based on configuration.
"""

import pytest
import json
import tempfile
import os
from src.factory import FileFactory
from src.config_manager import ConfigManager
from src.models import File, IVirtualFile
from src.decorators import EncryptedFileDecorator, CompressedFileDecorator


class TestFileFactoryCreation:
    """Test FileFactory.create_file() functionality."""

    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config_data = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config_data, f)

        config = ConfigManager(config_path)
        yield config
        try:
            os.unlink(config_path)
        except:
            pass

    def test_create_plain_file_no_rules(self, test_config):
        """Should create plain File when no rules match."""
        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/regular",
            config_manager=test_config,
            content="plain data"
        )

        assert isinstance(file, File)
        assert not isinstance(file, EncryptedFileDecorator)
        assert not isinstance(file, CompressedFileDecorator)
        assert file.read() == "plain data"

    def test_create_encrypted_file(self, test_config):
        """Should create EncryptedFileDecorator when rule matches."""
        file = FileFactory.create_file(
            name="secret.txt",
            parent_path="/secret",
            config_manager=test_config,
            content="confidential"
        )

        assert isinstance(file, EncryptedFileDecorator)
        assert file.read() == "confidential"

    def test_create_compressed_file(self, test_config):
        """Should create CompressedFileDecorator when rule matches."""
        file = FileFactory.create_file(
            name="log.txt",
            parent_path="/archive",
            config_manager=test_config,
            content="hello    world"
        )

        assert isinstance(file, CompressedFileDecorator)
        assert file.read() == "hello world"

    def test_create_encrypted_and_compressed_file(self, test_config):
        """Should compose decorators when multiple rules match."""
        file = FileFactory.create_file(
            name="secure.txt",
            parent_path="/secure",
            config_manager=test_config,
            content="data    with   spaces"
        )

        # Should be layered: CompressedFileDecorator(EncryptedFileDecorator(File))
        # But we need to check the right way - last decorator wraps first
        assert isinstance(file, CompressedFileDecorator)
        assert file.read() == "data with spaces"

    def test_file_created_with_name(self, test_config):
        """Created file should have correct name."""
        file = FileFactory.create_file(
            name="myfile.txt",
            parent_path="/secret",
            config_manager=test_config
        )

        assert file.name == "myfile.txt"

    def test_file_created_with_initial_content(self, test_config):
        """File should be created with initial content written."""
        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/secret",
            config_manager=test_config,
            content="initial content"
        )

        assert file.read() == "initial content"

    def test_file_created_with_empty_content(self, test_config):
        """File can be created with empty content."""
        file = FileFactory.create_file(
            name="empty.txt",
            parent_path="/secret",
            config_manager=test_config,
            content=""
        )

        assert file.read() == ""

    def test_file_created_without_content_parameter(self, test_config):
        """File should default to empty content."""
        file = FileFactory.create_file(
            name="default.txt",
            parent_path="/secret",
            config_manager=test_config
        )

        assert file.read() == ""

    def test_decorator_order_matters(self, test_config):
        """Decorators should be applied in specified order."""
        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/secure",
            config_manager=test_config,
            content="extra   spaces"
        )

        # When reading: last decorator unwraps first
        # So if order is [encrypted, compressed]:
        # Stored as: encrypted(compressed("extra spaces"))
        # Read as: decrypt(decompress(stored)) → "extra spaces"
        result = file.read()
        assert result == "extra spaces"

    def test_subpath_matching(self, test_config):
        """Rules should match subpaths."""
        file = FileFactory.create_file(
            name="data.txt",
            parent_path="/secret/subdir",
            config_manager=test_config,
            content="secret"
        )

        assert isinstance(file, EncryptedFileDecorator)
        assert file.read() == "secret"

    def test_deeply_nested_path_matching(self, test_config):
        """Rules should match deeply nested paths."""
        file = FileFactory.create_file(
            name="file.txt",
            parent_path="/archive/logs/2024/01",
            config_manager=test_config,
            content="log    entry"
        )

        assert isinstance(file, CompressedFileDecorator)
        assert file.read() == "log entry"


class TestFileFactoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_create_file_with_special_characters_in_name(self):
        """Should create file with special characters in name."""
        config = ConfigManager("nonexistent_config.json")
        file = FileFactory.create_file(
            name="file-with-special.txt",
            parent_path="/",
            config_manager=config,
            content="data"
        )

        assert file.name == "file-with-special.txt"

    def test_create_file_with_unicode_in_name(self):
        """Should create file with unicode characters in name."""
        config = ConfigManager("nonexistent_config.json")
        file = FileFactory.create_file(
            name="файл.txt",
            parent_path="/",
            config_manager=config
        )

        assert file.name == "файл.txt"

    def test_create_file_with_unicode_content(self):
        """Should handle unicode content."""
        config = ConfigManager("nonexistent_config.json")
        unicode_content = "Привет мир 你好世界"
        file = FileFactory.create_file(
            name="unicode.txt",
            parent_path="/",
            config_manager=config,
            content=unicode_content
        )

        assert file.read() == unicode_content

    def test_returns_ivirtualfile_interface(self):
        """Created file should implement IVirtualFile."""
        config = ConfigManager("nonexistent_config.json")
        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/",
            config_manager=config
        )

        # Should have IVirtualFile methods
        assert hasattr(file, 'read')
        assert hasattr(file, 'write')
        assert hasattr(file, 'get_size')
        assert callable(file.read)
        assert callable(file.write)
        assert callable(file.get_size)

    def test_no_config_preserves_plain_file(self):
        """Without config, should always create plain File."""
        config = ConfigManager("nonexistent_config.json")
        file = FileFactory.create_file(
            name="test.txt",
            parent_path="/any/path",
            config_manager=config,
            content="data"
        )

        # Should be exactly File, not decorated
        assert type(file).__name__ == 'File'
