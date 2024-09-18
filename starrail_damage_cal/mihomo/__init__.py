"""Mihomo.me api 包装"""

from ..mihomo.models import MihomoData
from ..mihomo.requests import get_char_card_info as requests

__all__ = ["requests", "MihomoData"]
