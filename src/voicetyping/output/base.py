"""Abstract interface for injecting text into the active application."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TextInjector(ABC):
    """Platform-specific text injection."""

    @abstractmethod
    def inject(self, text: str) -> None:
        """Insert text at the current cursor position."""
