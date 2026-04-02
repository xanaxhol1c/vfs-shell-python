import json
import os


class ConfigManager:
    def __init__(self, config_path: str = "vfs_config.json") -> None:
        self.rules = []
        self._load_config(config_path)

    def _load_config(self, path: str) -> None:
        if not os.path.exists(path):
            return

        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.rules = data.get("rules", [])
        except (json.JSONDecodeError, IOError):
            self.rules = []

    def get_decorators_for_path(self, path: str) -> list[str]:
        for rule in self.rules:
            if path.startswith(rule["path"]):
                return rule.get("decorators", [])
        return []
