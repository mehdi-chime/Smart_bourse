# 📦 نصب Smart_Bourse

## پیش‌نیازها

- Python 3.10+
- pip

## نصب

```bash
pip install -r requirements.txt
```

## اجرا

```bash
# منوی اصلی
python smart_bourse_v10.py

# اسکنر
python smart_scanner_v8.py

# حالت مدرسه
python school_mode_v7.py

# بررسی شبانه
python night_check.py

# AI
python daily_ai_runner.py

# داشبورد
python build_dashboard.py

# بک‌تست
python backtest_v2.py
```

## تست

```bash
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```