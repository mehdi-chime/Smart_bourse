"""
Project : Smart_Bourse
File    : ai/learner.py
Version : 2.0.0

Description :
    یادگیری از نتایج - نسخه بهبودیافته
    
Changes v2.0:
    - همه دسته‌ها (SAFE_BUY, SAFE_SELL, QUEUE_BUY)
    - همه وزن‌ها (money_flow, technical, context)
    - تغییر بیشتر (0.05)
    - حداقل کمتر (10)
    - وزن‌دهی زمانی
    - ذخیره تاریخ یادگیری
"""

import json
from datetime import datetime
from pathlib import Path


class AILearner:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.weights_file = self.base_dir / "weights.json"
        self.history_file = self.base_dir / "learning_history.json"
        
        self.default_weights = {
            "money_flow": 0.40,
            "technical": 0.35,
            "context": 0.25,
        }
        
        self.weight_limits = {
            "money_flow": (0.20, 0.60),
            "technical": (0.20, 0.60),
            "context": (0.10, 0.40),
        }
        
        self.min_outcomes = 10
        self.min_confidence = 3
        self.weight_step = 0.05
        
        self.weights = self.load_weights()

    def load_weights(self):
        if self.weights_file.exists():
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "money_flow" in data:
                        return data
            except Exception:
                pass
        return dict(self.default_weights)

    def save_weights(self):
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)

    def save_learning_history(self, entry):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append(entry)
        history = history[-100:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

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
        if len(outcomes) < self.min_outcomes:
            return self.weights
        
        category_stats = self.learn_from_outcomes(outcomes)
        total_adjustments = 0
        
        for cat in ["SAFE_BUY", "SAFE_SELL", "QUEUE_BUY"]:
            if cat not in category_stats:
                continue
            
            rate = category_stats[cat]["success_rate"]
            total = category_stats[cat]["total"]
            
            if total < self.min_confidence:
                continue
            
            adjustments = self._adjust_for_category(cat, rate)
            total_adjustments += adjustments
        
        self._normalize_weights()
        self.save_weights()
        
        self.save_learning_history({
            "date": datetime.now().isoformat(),
            "total_outcomes": len(outcomes),
            "category_stats": category_stats,
            "weights_after": dict(self.weights),
            "adjustments": total_adjustments,
        })
        
        return self.weights

    def _adjust_for_category(self, category, rate):
        adjustments = 0
        
        if rate > 0.60:
            self._increase_weight("money_flow", self.weight_step)
            self._increase_weight("technical", self.weight_step * 0.5)
            adjustments += 2
        elif rate < 0.40:
            self._decrease_weight("money_flow", self.weight_step)
            self._decrease_weight("technical", self.weight_step * 0.5)
            adjustments += 2
        else:
            self._decrease_weight("context", self.weight_step * 0.3)
            adjustments += 1
        
        return adjustments

    def _increase_weight(self, key, amount):
        if key not in self.weights:
            return
        min_val, max_val = self.weight_limits.get(key, (0.0, 1.0))
        new_val = min(max_val, self.weights[key] + amount)
        self.weights[key] = round(new_val, 3)

    def _decrease_weight(self, key, amount):
        if key not in self.weights:
            return
        min_val, max_val = self.weight_limits.get(key, (0.0, 1.0))
        new_val = max(min_val, self.weights[key] - amount)
        self.weights[key] = round(new_val, 3)

    def _normalize_weights(self):
        total = sum(self.weights.values())
        if total > 0:
            for k in self.weights:
                self.weights[k] = round(self.weights[k] / total, 3)

    def get_confidence(self, category, outcomes):
        cat_outcomes = [o for o in outcomes if o.get("category") == category]
        
        if len(cat_outcomes) < self.min_confidence:
            return 0.5
        
        total_weight = 0
        success_weight = 0
        
        recent = cat_outcomes[-20:]
        
        for i, o in enumerate(recent):
            weight = 1 + (i * 0.05)
            total_weight += weight
            if o.get("success"):
                success_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        raw_confidence = success_weight / total_weight
        count_bonus = min(0.1, len(cat_outcomes) * 0.005)
        confidence = min(1.0, raw_confidence + count_bonus)
        
        return round(confidence, 3)

    def report(self):
        print()
        print("=" * 70)
        print("  AILearner - Report (v2.0)")
        print("=" * 70)
        print()
        
        print("Weights:")
        for k, v in self.weights.items():
            print(f"   {k:<15} : {v}")
        print()
        
        print("Limits:")
        for k, (mn, mx) in self.weight_limits.items():
            print(f"   {k:<15} : {mn} - {mx}")
        print()
        
        print(f"Min outcomes    : {self.min_outcomes}")
        print(f"Min confidence  : {self.min_confidence}")
        print(f"Weight step     : {self.weight_step}")
        print()
        print("=" * 70)
        print()


if __name__ == "__main__":
    learner = AILearner()
    learner.report()
