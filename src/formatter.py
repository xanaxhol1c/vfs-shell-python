"""
Formatting and outputting results.
"""
from typing import Any, List
from src.models import INode, Directory

class OutputFormatter:
    def render_comment(self, text: str) -> None:
        """Prints comments with grey color."""
        print(f"\n\033[90m{text}\033[0m")

    def render_command_echo(self, text: str) -> None:
        """Echoes command that is currently running."""
        print(f"\n> {text}")

    def render_result(self, result: Any) -> None:
        # If command returns true then don't print anything
        if result is True:
            return
        # If the command returns nothing (mkdir, touch, cd), print OK
        if result is None:
            print("  \033[92m[OK]\033[0m")
            return

        if isinstance(result, list):
            self._render_ls(result)
        else:
            # For outputting text (cat) or messages
            print(f"  \033[94m{result}\033[0m")

    def render_error(self, message: str) -> None:
        print(f"  \033[91m[ERROR] {message}\033[0m")

    def _render_ls(self, nodes: List[INode]) -> None:
        if not nodes:
            print("  (empty)")
            return

        # Drawing tables header
        print(f"  {'TYPE':<6} {'PERM':<6} {'SIZE':<10} {'NAME'}")
        print(f"  {'-'*40}")
        
        for node in nodes:
            kind = "DIR" if isinstance(node, Directory) else "FILE"
            perm = oct(node.permissions)[2:]
            size = f"{node.get_size()} B"
            print(f"  {kind:<6} {perm:<6} {size:<10} {node.name}")