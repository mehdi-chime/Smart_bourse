"""
engines/long_term_engine.py
موتور سرمایه‌گذاری بلندمدت - قیمت‌ها بر اساس ریال
"""

class LongTermEngine:
    def __init__(self, data, config=None):
        self.data = data
        self.config = config or self.default_config()
        self.candidates = []

    def default_config(self):
        return {
            "min_volume": 20_000_000_000,
            "min_price": 100,
            "max_pe": 15,
            "min_growth": 0.10,
            "min_roe": 0.15,
            "max_debt_to_equity": 0.80,
            "max_candidates": 5,
            "weights": {
                "growth": 0.30,
                "pe": 0.25,
                "roe": 0.20,
                "debt": 0.15,
                "volume": 0.10
            }
        }

    def filter_stocks(self):
        filtered = []
        for stock in self.data:
            pe = stock.get('pe_ratio', 999)
            growth = stock.get('profit_growth', -1)
            roe = stock.get('roe', 0)
            debt_ratio = stock.get('debt_to_equity', 1)
            volume = stock.get('volume', 0)
            price = stock.get('close_price', 0)
            if volume < self.config["min_volume"]:
                continue
            if price < self.config["min_price"]:
                continue
            if pe > self.config["max_pe"] or pe <= 0:
                continue
            if growth < self.config["min_growth"]:
                continue
            if roe < self.config["min_roe"]:
                continue
            if debt_ratio > self.config["max_debt_to_equity"]:
                continue
            filtered.append(stock)
        return filtered

    def score_stock(self, stock):
        weights = self.config["weights"]
        score = 0
        growth = stock.get('profit_growth', 0)
        growth_score = min(10, max(0, growth * 100))
        score += growth_score * weights["growth"]
        pe = stock.get('pe_ratio', 20)
        if pe <= 5:
            pe_score = 10
        elif pe <= 10:
            pe_score = 8
        elif pe <= 15:
            pe_score = 6
        elif pe <= 20:
            pe_score = 4
        else:
            pe_score = 2
        score += pe_score * weights["pe"]
        roe = stock.get('roe', 0)
        roe_score = min(10, max(0, roe * 100))
        score += roe_score * weights["roe"]
        debt = stock.get('debt_to_equity', 1)
        if debt <= 0.3:
            debt_score = 10
        elif debt <= 0.5:
            debt_score = 7
        elif debt <= 0.8:
            debt_score = 5
        else:
            debt_score = 3
        score += debt_score * weights["debt"]
        volume = stock.get('volume', 0)
        volume_score = min(10, max(0, volume / 10_000_000_000))
        score += volume_score * weights["volume"]
        return round(score, 2)

    def get_candidates(self):
        filtered = self.filter_stocks()
        for stock in filtered:
            stock['long_term_score'] = self.score_stock(stock)
        sorted_stocks = sorted(filtered, key=lambda x: x.get('long_term_score', 0), reverse=True)
        self.candidates = sorted_stocks[:self.config["max_candidates"]]
        return self.candidates

    def report(self):
        if not self.candidates:
            return "❌ هیچ سهم مناسبی برای سرمایه‌گذاری بلندمدت پیدا نشد."
        lines = ["📊 پیشنهادات سرمایه‌گذاری بلندمدت (بیش از ۶ ماه):"]
        lines.append("=" * 60)
        lines.append("")
        for i, stock in enumerate(self.candidates, 1):
            symbol = stock.get('symbol', 'نامشخص')
            price = stock.get('close_price', 0)
            pe = stock.get('pe_ratio', 0)
            growth = stock.get('profit_growth', 0) * 100
            roe = stock.get('roe', 0) * 100
            debt = stock.get('debt_to_equity', 0) * 100
            score = stock.get('long_term_score', 0)
            lines.append(f"{i}. **{symbol}**")
            lines.append(f"   قیمت: {price:,.0f} ریال")
            lines.append(f"   نسبت P/E: {pe:.1f}")
            lines.append(f"   رشد سودآوری: {growth:+.1f}%")
            lines.append(f"   بازده حقوق صاحبان سهام (ROE): {roe:.1f}%")
            lines.append(f"   نسبت بدهی به حقوق صاحبان سهام: {debt:.1f}%")
            lines.append(f"   امتیاز نهایی: {score:.1f}")
            lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
