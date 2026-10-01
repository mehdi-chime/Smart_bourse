# train_ml_better.py
# آموزش بهتر ML با ویژگی‌های بیشتر
# اجرا: python train_ml_better.py

import os
import sys
import json
from pathlib import Path

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


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🎓 آموزش بهتر ML")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بارگذاری
    safe_print("  📂 بارگذاری نتایج...")
    from ai.memory import AIMemory
    memory = AIMemory()
    outcomes = memory.load_outcomes()
    signals = memory.load_signals()
    safe_print(f"     ✅ {len(outcomes)} نتیجه")
    safe_print(f"     ✅ {len(signals)} سیگنال")
    safe_print("")

    # ۲. ساخت dataset
    safe_print("  🔧 ساخت dataset...")

    # نقشه‌ی سیگنال‌ها
    signal_map = {}
    for s in signals:
        key = (s.get("date"), s.get("symbol"))
        signal_map[key] = s

    X = []
    y = []

    for o in outcomes:
        key = (o.get("date"), o.get("symbol"))
        sig = signal_map.get(key)
        
        if not sig:
            continue
        
        success = o.get("success")
        if success is None:
            continue
        
        # ویژگی‌های جدید
        features = [
            sig.get("ratio", 0) or 0,
            sig.get("rsi", 50) or 50,
            sig.get("technical_score", 50) or 50,
            sig.get("final_score", 50) or 50,
            sig.get("last_price", 0) or 0,
            (sig.get("context") or {}).get("market_change_pct", 0) or 0,
        ]
        
        X.append(features)
        y.append(1 if success else 0)

    safe_print(f"     ✅ {len(X)} نمونه")
    safe_print(f"     ✅ {sum(y)} موفق")
    safe_print(f"     ✅ {len(y) - sum(y)} ناموفق")
    safe_print(f"     دقت پایه: {sum(y)/len(y)*100:.1f}%")
    safe_print("")

    if len(X) < 10:
        safe_print("  ⚠️ داده کافی نیست!")
        return

    # ۳. آموزش
    safe_print("  🎓 آموزش مدل...")

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import pickle
    import numpy as np

    # تبدیل به numpy
    X_arr = np.array(X)
    y_arr = np.array(y)

    # تقسیم
    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr, test_size=0.2, random_state=42
    )

    # آموزش
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # تست
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    safe_print(f"     ✅ آموزش تمام")
    safe_print(f"     دقت train: {accuracy_score(y_train, model.predict(X_train))*100:.1f}%")
    safe_print(f"     دقت test: {accuracy*100:.1f}%")
    safe_print("")

    # ۴. اهمیت ویژگی‌ها
    safe_print("  📊 اهمیت ویژگی‌ها:")
    feature_names = ["ratio", "rsi", "tech_score", "final_score", "price", "market_pct"]
    importances = model.feature_importances_
    for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        safe_print(f"     {name:<15} : {imp:.3f}")
    safe_print("")

    # ۵. ذخیره
    safe_print("  💾 ذخیره مدل جدید...")
    model_file = PROJECT_ROOT / "data" / "ai" / "ml_model.pkl"
    model_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(model_file, "wb") as f:
        pickle.dump(model, f)
    
    safe_print(f"     ✅ {model_file}")
    safe_print("")

    # ۶. گزارش
    report = {
        "date": str(__import__('datetime').datetime.now().isoformat()),
        "samples": len(X),
        "features": len(feature_names),
        "train_accuracy": round(accuracy_score(y_train, model.predict(X_train)), 3),
        "test_accuracy": round(accuracy, 3),
        "feature_importance": dict(zip(feature_names, [round(float(i), 3) for i in importances])),
    }
    
    report_file = PROJECT_ROOT / "data" / "ai" / "training_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    safe_print(f"  📄 گزارش: {report_file}")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
