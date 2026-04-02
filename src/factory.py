from src.models import File, IVirtualFile
from src.decorators import EncryptedFileDecorator, CompressedFileDecorator

class FileFactory:
    @staticmethod
    def create_file(name: str, parent_path: str, config_manager, content: str = "") -> IVirtualFile:
        file_obj = File(name=name, content="")

        # Only apply decorators if config_manager is provided
        if config_manager:
            decorators = config_manager.get_decorators_for_path(parent_path)

            for dec_type in decorators:
                if dec_type == "encrypted":
                    file_obj = EncryptedFileDecorator(file_obj)
                elif dec_type == "compressed":
                    file_obj = CompressedFileDecorator(file_obj)

        if content:
            file_obj.write(content)

        return file_obj