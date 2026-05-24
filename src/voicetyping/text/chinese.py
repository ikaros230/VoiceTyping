"""Chinese script conversion utilities."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

import opencc

ChineseScript = Literal["simplified", "traditional"]


@lru_cache(maxsize=2)
def _get_converter(script: ChineseScript) -> opencc.OpenCC:
    config = "s2t" if script == "traditional" else "t2s"
    return opencc.OpenCC(config)


def convert_chinese(text: str, script: ChineseScript) -> str:
    """Convert Chinese text to the target script."""
    if not text:
        return text
    return _get_converter(script).convert(text)
