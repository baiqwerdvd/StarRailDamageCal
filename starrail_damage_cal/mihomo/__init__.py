"""Mihomo.me api 包装"""

from starrail_damage_cal.mihomo.models import MihomoData
from starrail_damage_cal.mihomo.requests import get_char_card_info as requests

__all__ = ["requests", "MihomoData"]
