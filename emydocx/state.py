"""Mutable runtime state of the application (UI-free)."""
from dataclasses import dataclass
from typing import Optional

from emydocx.config import DEFAULT_FILE_LABEL


@dataclass
class AppState:
    current_path: Optional[str] = None
    document_name: str = DEFAULT_FILE_LABEL

    def reset(self) -> None:
        self.current_path = None
        self.document_name = DEFAULT_FILE_LABEL

    def set_document(self, path: Optional[str], name: str) -> None:
        self.current_path = path
        self.document_name = name