"""
Project : Smart_Bourse
File    : ai/trainer.py
Version : 1.0.0

Description :
    آموزش مدل ML از داده‌های تاریخی
"""

import json
from pathlib import Path
from datetime import datetime


class AITrainer:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.outcomes_file = self.base_dir / "outcomes.jsonl"
        self.report_file = self.base_dir / "training_report.json"

    def load_outcomes(self):
        """بارگذاری نتایج"""
        if not self.outcomes_file.exists():
            return []
        
        entries = []
        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        return entries

    def prepare_data(self, outcomes):
        """آماده‌سازی داده برای ML"""
        X = []
        y = []
        
        for o in outcomes:
            # ویژگی‌ها
            features = [
                o.get("price_at_signal", 0),
                o.get("price_after_1d", 0) or 0,
                o.get("price_after_3d", 0) or 0,
                o.get("price_after_7d", 0) or 0,
            ]
            
            # برچسب
            success = o.get("success")
            if success is None:
                continue
            
            X.append(features)
            y.append(1 if success else 0)
        
        return X, y

    def train_from_outcomes(self):
        """آموزش از نتایج"""
        outcomes = self.load_outcomes()
        
        if len(outcomes) < 10:
            return {
                "status": "not_enough_data",
                "count": len(outcomes),
                "needed": 10,
            }
        
        X, y = self.prepare_data(outcomes)
        
        if len(X) < 10:
            return {
                "status": "not_enough_valid_data",
                "count": len(X),
            }
        
        # آموزش
        try:
            from ai.ml_model import MLModel
            model = MLModel()
            
            success = model.train(X, y)
            
            report = {
                "date": datetime.now().isoformat(),
                "status": "trained" if success else "failed",
                "samples": len(X),
                "features": 4,
                "success_count": sum(y),
                "fail_count": len(y) - sum(y),
            }
            
            # ذخیره گزارش
            with open(self.report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            return report
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }


if __name__ == "__main__":
    trainer = AITrainer()
    result = trainer.train_from_outcomes()
    print(json.dumps(result, ensure_ascii=False, indent=2))
