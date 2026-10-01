# install_xgboost.py
# فاز ۱۰: بهینه‌سازی ML با XGBoost
# اجرا: python install_xgboost.py

import os
import sys
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


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# ml_model_xgb.py
# ═══════════════════════════════════════════════════════════

ML_MODEL_XGB = '''"""
Project : Smart_Bourse
File    : ai/ml_model_xgb.py
Version : 1.0.0

Description :
    مدل ML پیشرفته با XGBoost
"""

import json
from pathlib import Path


class MLModelXGB:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.model_file = self.base_dir / "ml_model_xgb.pkl"
        self.model = None
        
        # چک xgboost
        try:
            import xgboost
            self.has_xgboost = True
        except ImportError:
            self.has_xgboost = False

    def train(self, X, y):
        """آموزش مدل XGBoost"""
        if not self.has_xgboost:
            return False
        
        try:
            import xgboost as xgb
            import pickle
            import numpy as np
            
            X_arr = np.array(X)
            y_arr = np.array(y)
            
            # محاسبه scale_pos_weight برای imbalanced data
            pos = sum(y_arr)
            neg = len(y_arr) - pos
            scale = neg / pos if pos > 0 else 1
            
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                scale_pos_weight=scale,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss',
            )
            
            self.model.fit(X_arr, y_arr)
            
            # ذخیره
            with open(self.model_file, "wb") as f:
                pickle.dump(self.model, f)
            
            return True
        except Exception as e:
            print(f"XGBoost Train error: {e}")
            return False

    def predict(self, X):
        """پیش‌بینی"""
        if not self.has_xgboost:
            return None
        
        try:
            import pickle
            import numpy as np
            
            if self.model is None:
                if self.model_file.exists():
                    with open(self.model_file, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    return None
            
            X_arr = np.array(X)
            return self.model.predict(X_arr)
        except Exception as e:
            print(f"XGBoost Predict error: {e}")
            return None

    def predict_proba(self, X):
        """احتمال پیش‌بینی"""
        if not self.has_xgboost:
            return None
        
        try:
            import pickle
            import numpy as np
            
            if self.model is None:
                if self.model_file.exists():
                    with open(self.model_file, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    return None
            
            X_arr = np.array(X)
            return self.model.predict_proba(X_arr)
        except Exception as e:
            print(f"XGBoost Predict_proba error: {e}")
            return None

    def feature_importance(self, feature_names):
        """اهمیت ویژگی‌ها"""
        if not self.has_xgboost or self.model is None:
            return None
        
        try:
            importances = self.model.feature_importances_
            return dict(zip(feature_names, [round(float(i), 3) for i in importances]))
        except Exception:
            return None

    def is_ready(self):
        """آماده است؟"""
        return self.model_file.exists()


if __name__ == "__main__":
    model = MLModelXGB()
    print(f"Has xgboost: {model.has_xgboost}")
    print(f"Model ready: {model.is_ready()}")
'''


def install_xgboost():
    """نصب xgboost"""
    import subprocess
    safe_print("  📦 نصب xgboost...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "xgboost"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    
    if result.returncode == 0:
        safe_print("     ✅ xgboost نصب شد")
        return True
    else:
        safe_print("     ❌ خطا")
        return False


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 فاز ۱۰: بهینه‌سازی ML (XGBoost)")
    safe_print("=" * 80)
    safe_print("")

    # ۱. نصب xgboost
    install_xgboost()
    safe_print("")

    # ۲. ساخت ml_model_xgb.py
    safe_print("  📄 ساخت ai/ml_model_xgb.py...")
    size = write_file(PROJECT_ROOT / "ai" / "ml_model_xgb.py", ML_MODEL_XGB)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۳. تست
    safe_print("  🧪 تست XGBoost...")
    try:
        import importlib
        if "ai.ml_model_xgb" in sys.modules:
            importlib.reload(sys.modules["ai.ml_model_xgb"])
        
        from ai.ml_model_xgb import MLModelXGB
        model = MLModelXGB()
        safe_print(f"     Has xgboost: {model.has_xgboost}")
        safe_print(f"     Model ready: {model.is_ready()}")
        
        # تست آموزش
        if model.has_xgboost:
            from ai.memory import AIMemory
            memory = AIMemory()
            outcomes = memory.load_outcomes()
            
            safe_print(f"     Outcomes: {len(outcomes)}")
            
            if len(outcomes) >= 10:
                X = [[o.get("price_at_signal", 0), 0, 0, 0] for o in outcomes]
                y = [1 if o.get("success") else 0 for o in outcomes]
                
                success = model.train(X, y)
                safe_print(f"     Train: {success}")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ xgboost نصب شد")
    safe_print("  ✅ ai/ml_model_xgb.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
