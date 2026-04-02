"""
Unit tests for ConfigManager.
Tests configuration loading, rule matching, and decorator resolution.
"""

import pytest
import json
import os
import tempfile
from src.config_manager import ConfigManager


class TestConfigManagerLoading:
    """Test ConfigManager initialization and config file loading."""

    def test_config_file_not_exists(self):
        """ConfigManager should handle missing config file gracefully."""
        config = ConfigManager("nonexistent_config.json")
        assert config.rules == []

    def test_config_file_loaded_successfully(self):
        """ConfigManager should load valid config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path":"/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            assert len(config.rules) == 2
            assert config.rules[0]["path"] == "/secret"
            assert config.rules[1]["path"] == "/archive"
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_config_file_invalid_json(self):
        """ConfigManager should handle invalid JSON gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            f.write("{ invalid json ]")

        try:
            config = ConfigManager(config_path)
            assert config.rules == []
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_config_file_missing_rules_key(self):
        """ConfigManager should handle missing 'rules' key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            json.dump({"other_key": "value"}, f)

        try:
            config = ConfigManager(config_path)
            assert config.rules == []
        finally:
            try:
                os.unlink(config_path)
            except:
                pass


class TestConfigManagerRuleMatching:
    """Test decorator resolution for filesystem paths."""

    def test_get_decorators_exact_path(self):
        """Should return decorators for exact path match."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/secret")
            assert decorators == ["encrypted"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_get_decorators_subpath(self):
        """Should return decorators for paths within matching directory."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/secret/file.txt")
            assert decorators == ["encrypted"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_get_decorators_nested_path(self):
        """Should return decorators for deeply nested paths."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/secret/subdir/file.txt")
            assert decorators == ["encrypted"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_get_decorators_no_match(self):
        """Should return empty list when path doesn't match any rule."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/other/path")
            assert decorators == []
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_get_decorators_multiple_decorators(self):
        """Should return multiple decorators in order for /secure path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/secure/data.txt")
            assert decorators == ["encrypted", "compressed"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_get_decorators_first_match_wins(self):
        """Should return decorators from first matching rule."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/secret/special", "decorators": ["compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            # First rule matches /secret/special/file.txt
            decorators = config.get_decorators_for_path("/secret/special/file.txt")
            assert decorators == ["encrypted"]
        finally:
            try:
                os.unlink(config_path)
            except:
                pass

    def test_path_prefix_matching(self):
        """Test path matching works with startswith semantics."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            test_config = {
                "rules": [
                    {"path": "/secret", "decorators": ["encrypted"]},
                    {"path": "/archive", "decorators": ["compressed"]},
                    {"path": "/secure", "decorators": ["encrypted", "compressed"]}
                ]
            }
            json.dump(test_config, f)

        try:
            config = ConfigManager(config_path)
            decorators = config.get_decorators_for_path("/archive/log.txt")
            assert decorators == ["compressed"]

            # Note: /archived does match /archive with startswith
            # This is expected behavior based on ConfigManager.get_decorators_for_path
            decorators = config.get_decorators_for_path("/archived/log.txt")
            assert decorators == ["compressed"]  # Matches /archive prefix
        finally:
            try:
                os.unlink(config_path)
            except:
                pass
