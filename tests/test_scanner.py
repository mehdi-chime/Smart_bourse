"""
Tests for scanner modules
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_import_indicators():
    from indicators import rsi
    assert rsi is not None


def test_import_strategy():
    from strategy import signal_engine
    assert signal_engine is not None


def test_import_market():
    from market import api
    assert api is not None


def test_rsi_calculation():
    from indicators.rsi import RSI
    rsi = RSI()
    assert rsi is not None
