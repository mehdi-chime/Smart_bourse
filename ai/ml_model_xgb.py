"""
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
