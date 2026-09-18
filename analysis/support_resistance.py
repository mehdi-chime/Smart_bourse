"""
analysis/support_resistance.py
تشخیص نقاط حمایت و مقاومت
"""

import numpy as np

class SupportResistance:
    """کلاس اصلی برای سازگاری با analysis.py"""
    def __init__(self, prices=None):
        self.prices = prices or []
        self.support_levels = []
        self.resistance_levels = []

    def calculate(self, prices=None, lookback=10):
        if prices is None:
            prices = self.prices
        
        if len(prices) < lookback * 2:
            return {
                'support': [],
                'resistance': [],
                'near_support': False,
                'near_resistance': False,
                'support_level': None,
                'resistance_level': None
            }

        prices = np.array(prices)
        current_price = prices[-1]

        supports = []
        resistances = []

        for i in range(lookback, len(prices) - lookback):
            if all(prices[i] < prices[i - j] for j in range(1, lookback + 1)) and \
               all(prices[i] < prices[i + j] for j in range(1, lookback + 1)):
                supports.append(prices[i])
            
            if all(prices[i] > prices[i - j] for j in range(1, lookback + 1)) and \
               all(prices[i] > prices[i + j] for j in range(1, lookback + 1)):
                resistances.append(prices[i])

        supports = self._filter_close_levels(supports)
        resistances = self._filter_close_levels(resistances)

        near_support = False
        near_resistance = False
        support_level = None
        resistance_level = None

        if supports:
            nearest_support = max([s for s in supports if s < current_price], default=None)
            if nearest_support:
                support_level = nearest_support
                if (current_price - nearest_support) / current_price < 0.05:
                    near_support = True

        if resistances:
            nearest_resistance = min([r for r in resistances if r > current_price], default=None)
            if nearest_resistance:
                resistance_level = nearest_resistance
                if (nearest_resistance - current_price) / current_price < 0.05:
                    near_resistance = True

        return {
            'support': supports[:5],
            'resistance': resistances[:5],
            'near_support': near_support,
            'near_resistance': near_resistance,
            'support_level': support_level,
            'resistance_level': resistance_level
        }

    def _filter_close_levels(self, levels, threshold=0.02):
        if not levels:
            return []
        levels = sorted(levels)
        filtered = [levels[0]]
        for level in levels[1:]:
            if (level - filtered[-1]) / filtered[-1] > threshold:
                filtered.append(level)
        return filtered


class SupportResistanceAnalyzer:
    """کلاس جدید برای سازگاری با advanced_scanner.py"""
    def __init__(self):
        self.support_levels = []
        self.resistance_levels = []

    def calculate(self, prices, lookback=10):
        sr = SupportResistance(prices)
        return sr.calculate(prices, lookback)

    def get_support_resistance(self, prices, lookback=10):
        return self.calculate(prices, lookback)
