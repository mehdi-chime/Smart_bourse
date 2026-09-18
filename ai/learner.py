"""
Project : Smart_Bourse
File    : ai/learner.py
Version : 1.0.0

Description :
    یادگیری از نتایج
"""

import json
from pathlib import Path


class AILearner:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.weights_file = self.base_dir / "weights.json"
        self.default_weights = {
            "money_flow": 0.40,
            "technical": 0.35,
            "context": 0.25,
        }
        self.weights = self.load_weights()

    def load_weights(self):
        if self.weights_file.exists():
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return dict(self.default_weights)

    def save_weights(self):
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)

    def learn_from_outcomes(self, outcomes):
        if not outcomes:
            return {}
        stats = {}
        for o in outcomes:
            cat = o.get("category", "UNKNOWN")
            if cat not in stats:
                stats[cat] = {"total": 0, "success": 0, "fail": 0}
            stats[cat]["total"] += 1
            if o.get("success") is True:
                stats[cat]["success"] += 1
            elif o.get("success") is False:
                stats[cat]["fail"] += 1
        for cat, s in stats.items():
            if s["total"] > 0:
                s["success_rate"] = round(s["success"] / s["total"], 3)
            else:
                s["success_rate"] = 0.0
        return stats

    def adjust_weights(self, outcomes):
        if len(outcomes) < 20:
            return self.weights
        safe_buy_outcomes = [o for o in outcomes if o.get("category") == "SAFE_BUY"]
        if safe_buy_outcomes:
            success = sum(1 for o in safe_buy_outcomes if o.get("success"))
            rate = success / len(safe_buy_outcomes)
            if rate > 0.6:
                self.weights["money_flow"] = min(0.55, self.weights["money_flow"] + 0.02)
            elif rate < 0.4:
                self.weights["money_flow"] = max(0.25, self.weights["money_flow"] - 0.02)
        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] = round(self.weights[k] / total, 3)
        self.save_weights()
        return self.weights

    def get_confidence(self, category, outcomes):
        cat_outcomes = [o for o in outcomes if o.get("category") == category]
        if len(cat_outcomes) < 5:
            return 0.5
        success = sum(1 for o in cat_outcomes if o.get("success"))
        return round(success / len(cat_outcomes), 3)
