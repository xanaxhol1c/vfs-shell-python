"""
Unit tests for decorators: EncryptedFileDecorator and CompressedFileDecorator.
Tests transparent encryption/compression and decorator composition.
"""

import pytest
import base64
from src.decorators import FileDecorator, EncryptedFileDecorator, CompressedFileDecorator
from src.models import File


class TestEncryptedFileDecorator:
    """Test EncryptedFileDecorator functionality."""

    @pytest.fixture
    def encrypted_file(self):
        """Create an encrypted file for testing."""
        plain_file = File(name="secret.txt", content="")
        return EncryptedFileDecorator(plain_file)

    def test_write_encrypts_data(self, encrypted_file):
        """Writing should encrypt data using base64."""
        encrypted_file.write("hello")
        # Get the encrypted stored content
        stored = encrypted_file._wrapped.read()
        # Should be base64 encoded
        expected = base64.b64encode(b"hello").decode()
        assert stored == expected

    def test_read_decrypts_data(self, encrypted_file):
        """Reading should decrypt data transparently."""
        encrypted_file.write("confidential")
        result = encrypted_file.read()
        assert result == "confidential"

    def test_encrypted_content_not_plaintext(self, encrypted_file):
        """Encrypted content should not match plaintext."""
        encrypted_file.write("secret data")
        stored = encrypted_file._wrapped.read()
        assert stored != "secret data"
        assert base64.b64decode(stored.encode()).decode() == "secret data"

    def test_read_empty_encrypted_file(self, encrypted_file):
        """Reading empty encrypted file should return empty string."""
        encrypted_file.write("")
        result = encrypted_file.read()
        assert result == ""

    def test_multiple_write_read_cycles(self, encrypted_file):
        """Multiple writes and reads should work correctly."""
        test_data = ["first", "second", "third"]
        for data in test_data:
            encrypted_file.write(data)
            result = encrypted_file.read()
            assert result == data

    def test_encryption_with_special_characters(self, encrypted_file):
        """Should handle special characters correctly."""
        special = "!@#$%^&*()\n\t"
        encrypted_file.write(special)
        result = encrypted_file.read()
        assert result == special

    def test_encryption_with_unicode(self, encrypted_file):
        """Should handle unicode characters correctly."""
        unicode_text = "Hello 你好 مرحبا Привет"
        encrypted_file.write(unicode_text)
        result = encrypted_file.read()
        assert result == unicode_text

    def test_get_size_reflects_encrypted_size(self, encrypted_file):
        """File size should reflect encrypted content size."""
        encrypted_file.write("hello")
        # Size should be base64 encoded size, not original
        expected_encrypted = base64.b64encode(b"hello").decode()
        assert encrypted_file.get_size() == len(expected_encrypted)


class TestCompressedFileDecorator:
    """Test CompressedFileDecorator functionality."""

    @pytest.fixture
    def compressed_file(self):
        """Create a compressed file for testing."""
        plain_file = File(name="log.txt", content="")
        return CompressedFileDecorator(plain_file)

    def test_write_removes_extra_spaces(self, compressed_file):
        """Writing should normalize whitespace."""
        compressed_file.write("hello    world")
        stored = compressed_file._wrapped.read()
        assert stored == "hello world"

    def test_read_returns_compressed(self, compressed_file):
        """Reading should return compressed content."""
        compressed_file.write("hello    world     spaced")
        result = compressed_file.read()
        assert result == "hello world spaced"

    def test_compress_multiple_spaces(self, compressed_file):
        """Should collapse multiple spaces into single space."""
        compressed_file.write("a     b     c")
        result = compressed_file.read()
        assert result == "a b c"

    def test_compress_tabs_and_newlines(self, compressed_file):
        """Should handle tabs and newlines as whitespace."""
        compressed_file.write("hello\t\tworld\n\ntest")
        result = compressed_file.read()
        # split() removes all whitespace and rejoins with single space
        assert result == "hello world test"

    def test_compress_leading_trailing_spaces(self, compressed_file):
        """Should remove leading and trailing spaces."""
        compressed_file.write("  hello world  ")
        result = compressed_file.read()
        assert result == "hello world"

    def test_compress_empty_file(self, compressed_file):
        """Compressing empty file should return empty string."""
        compressed_file.write("")
        result = compressed_file.read()
        assert result == ""

    def test_compress_single_word(self, compressed_file):
        """Single word without spaces should be unchanged."""
        compressed_file.write("hello")
        result = compressed_file.read()
        assert result == "hello"

    def test_get_size_reflects_compressed_size(self, compressed_file):
        """File size should reflect compressed content size."""
        compressed_file.write("hello    world")
        # Compressed size is "hello world"
        assert compressed_file.get_size() == len("hello world")


class TestDecoratorComposition:
    """Test combining multiple decorators."""

    def test_encrypted_then_compressed(self):
        """Decrypt then decompress when reading."""
        plain_file = File(name="data.txt", content="")
        # Apply decorators: first encrypted, then compressed wrapper
        encrypted = EncryptedFileDecorator(plain_file)
        compressed = CompressedFileDecorator(encrypted)

        # Write: compress → encrypt
        compressed.write("hello    world   test")

        # Verify original text retrieved
        result = compressed.read()
        assert result == "hello world test"

    def test_compressed_then_encrypted(self):
        """CompressedFileDecorator wraps EncryptedFileDecorator.
        Write encrypts first (no spaces to compress in encrypted base64).
        Read decrypts to original.
        """
        plain_file = File(name="data.txt", content="")
        compressed = CompressedFileDecorator(plain_file)
        encrypted = EncryptedFileDecorator(compressed)

        # Write: encrypt "data    with   spaces" → base64 (no spaces) → compress (no-op) → file
        encrypted.write("data    with   spaces")

        # Read: file → decompress (decorator doesn't decompress) → decrypt → original with spaces
        result = encrypted.read()
        assert result == "data    with   spaces"

    def test_triple_composition(self):
        """Test three decorators: enc2 -> compressed -> enc1 -> file.
        Encrypted strings don't have extra spaces, so compression is no-op.
        """
        plain_file = File(name="data.txt", content="")
        enc1 = EncryptedFileDecorator(plain_file)
        compressed = CompressedFileDecorator(enc1)
        enc2 = EncryptedFileDecorator(compressed)

        enc2.write("test    value")
        # Decrypts enc2 (returns compressed's content) → compressed returns enc1's content (decrypted)
        result = enc2.read()
        assert result == "test    value"

    def test_decorator_preserves_wrapped_reference(self):
        """Decorators should preserve reference to wrapped file."""
        plain_file = File(name="test.txt", content="")
        encrypted = EncryptedFileDecorator(plain_file)

        assert encrypted._wrapped == plain_file
        assert encrypted.name == plain_file.name
        assert encrypted.permissions == plain_file.permissions

    def test_decorator_inheritance(self):
        """FileDecorator should properly inherit from IVirtualFile."""
        plain_file = File(name="test.txt", content="")
        encrypted = EncryptedFileDecorator(plain_file)

        # Should have required methods
        assert hasattr(encrypted, 'read')
        assert hasattr(encrypted, 'write')
        assert hasattr(encrypted, 'get_size')
        assert hasattr(encrypted, 'name')
        assert hasattr(encrypted, 'parent')
        assert hasattr(encrypted, 'permissions')
