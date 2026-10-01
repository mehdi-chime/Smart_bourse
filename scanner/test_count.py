import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

HOLDINGS = [
    {"user_name": "تابان", "aliases": ["تابان"], "qty": 3697, "buy_price": None},
    {"user_name": "پکویر", "aliases": ["پكوير", "پکویر"], "qty": 23518, "buy_price": None},
    {"user_name": "سمهریز", "aliases": ["سهرمز", "سمهریز"], "qty": 5350, "buy_price": None},
    {"user_name": "احیا", "aliases": ["احیا"], "qty": 49122, "buy_price": None},
    {"user_name": "پیزد", "aliases": ["پیزد"], "qty": 23220, "buy_price": None},
    {"user_name": "خگستر", "aliases": ["خگستر"], "qty": 217948, "buy_price": None},
    {"user_name": "فولاد", "aliases": ["فولاد"], "qty": 431948, "buy_price": 3394},
]

print(len(HOLDINGS), "holdings")
