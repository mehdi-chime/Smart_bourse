"""
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
