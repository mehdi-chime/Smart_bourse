# 🤖 مستندات AI

## 📁 ساختار

| فایل | کار |
|:---|:---|
| `ai_engine.py` | موتور اصلی (advise, check_outcomes) |
| `memory.py` | حافظه (JSONL) |
| `learner.py` | یادگیری (تنظیم وزن) |
| `ml_model.py` | مدل ML (RandomForest) |
| `trainer.py` | آموزش |
| `ml_model_xgb.py` | مدل XGBoost (اختیاری) |

## 🔄 چرخه

1. جمع‌آوری داده
2. تحلیل (`advise`)
3. ثبت سیگنال (`memory.save_signal`)
4. انتظار (1-7 روز)
5. چک نتیجه (`check_outcomes`)
6. یادگیری (`learner.adjust_weights`)
7. تنظیم وزن‌ها
8. ML training (`trainer`)
9. سیگنال بهتر

## 🎯 فرمول امتیاز

```
final_score =
    0.6 * ml_score +
    0.4 * (
        money_flow * mf_score +
        technical * tech_score +
        context * context_score
    )
```

## 📊 وزن‌ها

| وزن | مقدار پیش‌فرض |
|:---|:---:|
| money_flow | 0.40 |
| technical | 0.35 |
| context | 0.25 |

## 🧠 ML Model

- **الگوریتم:** RandomForest
- **ویژگی‌ها:** 6 (ratio, rsi, tech_score, weight_score, price, market_pct)
- **آموزش:** از `outcomes.jsonl`
- **ذخیره:** `data/ai/ml_model.pkl`

## 📌 استفاده

```python
from ai_integration import get_ai_advice

result = get_ai_advice(
    symbol='خگستر',
    category='SAFE_BUY',
    ratio=5.0,
    rsi=25,
    last_price=10000,
)
```