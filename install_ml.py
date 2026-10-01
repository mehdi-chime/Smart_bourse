# install_ml.py
# نصب ML — فاز ۲
# اجرا: python install_ml.py

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

AI_DIR = PROJECT_ROOT / "ai"
BACKUP_DIR = PROJECT_ROOT / "backup" / "ai"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def backup_ai():
    if not AI_DIR.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"ai_backup_ml_{timestamp}"
    shutil.copytree(AI_DIR, backup_path)
    return backup_path


# ═══════════════════════════════════════════════════════════
# ml_model.py
# ═══════════════════════════════════════════════════════════

ML_MODEL = '''"""
Project : Smart_Bourse
File    : ai/ml_model.py
Version : 1.0.0

Description :
    مدل یادگیری ماشین — RandomForest
"""

import json
from pathlib import Path


class MLModel:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_file = self.base_dir / "ml_model.pkl"
        self.model = None
        
        # چک scikit-learn
        try:
            from sklearn.ensemble import RandomForestClassifier
            self.has_sklearn = True
        except ImportError:
            self.has_sklearn = False

    def train(self, X, y):
        """آموزش مدل"""
        if not self.has_sklearn:
            return False
        
        try:
            from sklearn.ensemble import RandomForestClassifier
            import pickle
            
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
            )
            self.model.fit(X, y)
            
            # ذخیره
            with open(self.model_file, "wb") as f:
                pickle.dump(self.model, f)
            
            return True
        except Exception as e:
            print(f"Train error: {e}")
            return False

    def predict(self, X):
        """پیش‌بینی"""
        if not self.has_sklearn:
            return None
        
        try:
            import pickle
            
            if self.model is None:
                if self.model_file.exists():
                    with open(self.model_file, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    return None
            
            return self.model.predict(X)
        except Exception as e:
            print(f"Predict error: {e}")
            return None

    def predict_proba(self, X):
        """احتمال پیش‌بینی"""
        if not self.has_sklearn:
            return None
        
        try:
            import pickle
            
            if self.model is None:
                if self.model_file.exists():
                    with open(self.model_file, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    return None
            
            return self.model.predict_proba(X)
        except Exception as e:
            print(f"Predict_proba error: {e}")
            return None

    def is_ready(self):
        """آماده است؟"""
        return self.model_file.exists()


if __name__ == "__main__":
    model = MLModel()
    print(f"Has sklearn: {model.has_sklearn}")
    print(f"Model ready: {model.is_ready()}")
'''


# ═══════════════════════════════════════════════════════════
# trainer.py
# ═══════════════════════════════════════════════════════════

TRAINER = '''"""
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
'''


def install_ml_model():
    path = AI_DIR / "ml_model.py"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 1.0.0" in content:
            safe_print("     ℹ️ ml_model.py از قبل هست")
            return True
    path.write_text(ML_MODEL, encoding="utf-8")
    safe_print("     ✅ ml_model.py نصب شد")
    return True


def install_trainer():
    path = AI_DIR / "trainer.py"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 1.0.0" in content:
            safe_print("     ℹ️ trainer.py از قبل هست")
            return True
    path.write_text(TRAINER, encoding="utf-8")
    safe_print("     ✅ trainer.py نصب شد")
    return True


def check_sklearn():
    try:
        import sklearn
        safe_print(f"     ✅ scikit-learn نصب شده (v{sklearn.__version__})")
        return True
    except ImportError:
        safe_print("     ⚠️ scikit-learn نصب نیست")
        safe_print("     دستور: pip install scikit-learn")
        return False


def test_ml():
    safe_print("")
    safe_print("  🧪 تست ML...")
    
    try:
        from ai.ml_model import MLModel
        from ai.trainer import AITrainer
        
        safe_print("     ✅ ml_model import موفق")
        safe_print("     ✅ trainer import موفق")
        
        model = MLModel()
        safe_print(f"     Has sklearn: {model.has_sklearn}")
        safe_print(f"     Model ready: {model.is_ready()}")
        
        trainer = AITrainer()
        outcomes = trainer.load_outcomes()
        safe_print(f"     Outcomes: {len(outcomes)}")
        
        return True
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 نصب ML — فاز ۲")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ...")
    backup = backup_ai()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    # ۲. چک sklearn
    safe_print("  🔍 چک scikit-learn...")
    has_sklearn = check_sklearn()
    safe_print("")

    # ۳. نصب
    safe_print("  📝 نصب ml_model.py...")
    install_ml_model()
    safe_print("")

    safe_print("  📝 نصب trainer.py...")
    install_trainer()
    safe_print("")

    # ۴. تست
    test_ml()
    safe_print("")

    # ۵. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ ml_model.py")
    safe_print("  ✅ trainer.py")
    safe_print(f"  {'✅' if has_sklearn else '⚠️'} scikit-learn")
    safe_print("")
    if not has_sklearn:
        safe_print("  📌 دستور نصب:")
        safe_print("     pip install scikit-learn")
        safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
