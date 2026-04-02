import base64
from src.models import IVirtualFile

class FileDecorator(IVirtualFile):
    def __init__(self, wrapped: IVirtualFile):
        super().__init__(wrapped.name, wrapped.parent, wrapped.permissions)
        self._wrapped = wrapped

    def read(self) -> str:
        return self._wrapped.read()

    def write(self, data: str) -> None:
        self._wrapped.write(data)

    def get_size(self) -> int:
        return self._wrapped.get_size()

class EncryptedFileDecorator(FileDecorator):
    def read(self) -> str:
        encrypted_data = super().read()
        if not encrypted_data:
            return ""
        return base64.b64decode(encrypted_data.encode()).decode()

    def write(self, data: str) -> None:
        encrypted = base64.b64encode(data.encode()).decode()
        super().write(encrypted)

class CompressedFileDecorator(FileDecorator):
    def write(self, data: str) -> None:
        compressed = " ".join(data.split())
        super().write(compressed)