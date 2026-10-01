# test_all_important.py
# تست همه‌ی فایل‌های مهم پروژه
# اجرا: python test_all_important.py

import os
import sys
import json
import importlib.util
import traceback
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

OUTPUT_FILE = PROJECT_ROOT / "test_all_report.txt"


def safe_print(text, end="\n"):
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'), end=end)


# ═══════════════════════════════════════════════════════════
# لیست فایل‌های مهم برای تست
# ═══════════════════════════════════════════════════════════

IMPORTANT_FILES = [
    # ═══ فایل‌های ریشه ═══
    "main.py",
    "run.py",
    "config.py",
    "project_config.py",
    "daily_runner.py",
    "auto_trader.py",
    "chatgpt_bridge.py",
    "auto_push.py",

    # ═══ اسکنرها ═══
    "smart_scanner_v5.py",
    "smart_scanner_v8.py",
    "golden_scanner.py",
    "tomorrow_picks.py",
    "tomorrow_picks_v2.py",
    "tomorrow_v5.py",
    "check_tomorrow.py",
    "night_check.py",

    # ═══ حالت مدرسه ═══
    "school_mode_v3.py",
    "school_mode_v5.py",
    "school_mode_v7.py",
    "install_school_v3.py",
    "install_school_v5.py",

    # ═══ منو ═══
    "smart_bourse_v10.py",

    # ═══ AI ═══
    "ai/ai_engine.py",
    "ai/learner.py",
    "ai/memory.py",
    "ai/backtest_optimizer.py",
    "ai/momentum_scanner.py",
    "ai/order_flow_analyzer.py",
    "ai/whale_detector.py",

    # ═══ تحلیل ═══
    "analysis/analysis.py",
    "analysis/signal_engine.py",
    "analysis/strategy.py",
    "analysis/trend.py",
    "analysis/trend_detector.py",
    "analysis/support_resistance.py",

    # ═══ استراتژی ═══
    "strategy/signal_engine.py",
    "strategy/signal_manager.py",
    "strategy/strategy_manager.py",
    "strategy/risk_manager.py",
    "strategy/score_manager.py",
    "strategy/scenario_engine.py",

    # ═══ موتورها ═══
    "engines/advanced_scanner.py",
    "engines/crisis_swing_engine.py",
    "engines/long_term_engine.py",
    "engines/market_psychology_engine.py",
    "engines/mid_term_engine.py",
    "engines/swing_engine.py",

    # ═══ تصمیم ═══
    "decision/ai_decision_engine.py",

    # ═══ ایتا ═══
    "eitaa/eitaa_bot.py",

    # ═══ دیتابیس ═══
    "database/database.py",
    "database/symbol_repository.py",

    # ═══ بازار ═══
    "market/api.py",
    "market/market_manager.py",
    "market/market_scanner.py",
    "market/market_status.py",

    # ═══ تاریخچه ═══
    "history/history_database.py",
    "history/history_downloader.py",
    "history/history_manager.py",

    # ═══ اندیکاتورها ═══
    "indicators/rsi.py",
    "indicators/macd.py",
    "indicators/atr.py",
    "indicators/adx.py",
    "indicators/bollinger.py",
    "indicators/ema.py",
    "indicators/ichimoku.py",
    "indicators/supertrend.py",

    # ═══ اسکنرهای مهم ═══
    "scanner/alert_config.py",
    "scanner/auto_runner.py",
    "scanner/smart_alert.py",
    "scanner/real_flow_filter.py",
    "scanner/technical_analyzer.py",
    "scanner/deep_analyzer.py",
    "scanner/decision_maker.py",
    "scanner/market_context.py",
    "scanner/portfolio_alert.py",
    "scanner/portfolio_tracker.py",
    "scanner/live_monitor.py",
    "scanner/live_dashboard.py",
    "scanner/html_reporter.py",
    "scanner/dashboard_builder.py",
    "scanner/smart_indicators.py",
    "scanner/ai_advisor.py",
    "scanner/alert_monitor.py",
    "scanner/auto_portfolio_alert.py",
    "scanner/live_analyzer.py",
    "scanner/live_portfolio.py",
    "scanner/live_recorder.py",
    "scanner/market_screener.py",
    "scanner/portfolio_history.py",
    "scanner/portfolio_report.py",

    # ═══ پرتفوی ═══
    "portfolio/portfolio.py",
    "portfolio/journal.py",
    "portfolio/position.py",

    # ═══ ریسک ═══
    "risk/risk_manager.py",

    # ═══ گزارش ═══
    "reports/excel_export.py",
    "reports/performance_report.py",
    "reports/report_generator.py",
    "reports/report_manager.py",

    # ═══ ابزار ═══
    "utils/file_manager.py",
    "utils/logger.py",
    "utils/symbol_map.py",

    # ═══ هسته ═══
    "core/data_fetcher.py",
    "core/event_analyzer.py",
    "core/logger.py",
    "core/market_health.py",
    "core/trade_recorder.py",

    # ═══ بنیادی ═══
    "fundamental/fundamental_analyzer.py",

    # ═══ پیپر ═══
    "paper/paper_trading.py",

    # ═══ اخبار ═══
    "news/news_analyzer.py",

    # ═══ مدل ═══
    "models/stock.py",

    # ═══ زمان‌بند ═══
    "scheduler/scheduler.py",

    # ═══ UI ═══
    "ui/main_dashboard.py",
]


def test_import(file_path):
    """تست import فایل"""
    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "exists": file_path.exists(),
        "can_import": False,
        "error": None,
        "error_type": None,
        "lines": 0,
        "size": 0,
    }

    if not file_path.exists():
        return result

    result["size"] = file_path.stat().st_size

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        result["lines"] = len(content.split("\n"))
    except:
        pass

    try:
        module_name = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", ".").replace("/", ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            result["error"] = "spec is None"
            return result

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result["can_import"] = True

    except Exception as e:
        result["error"] = str(e)[:200]
        result["error_type"] = type(e).__name__

    return result


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🧪 تست همه‌ی فایل‌های مهم پروژه")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  📋 {len(IMPORTANT_FILES)} فایل برای تست")
    safe_print("")

    results = []

    for i, rel_path in enumerate(IMPORTANT_FILES, 1):
        file_path = PROJECT_ROOT / rel_path
        safe_print(f"  [{i:>3}/{len(IMPORTANT_FILES)}] {rel_path}", end=" ... ")

        result = test_import(file_path)
        results.append(result)

        if not result["exists"]:
            safe_print("❌ نیست")
        elif result["can_import"]:
            safe_print(f"✅ ({result['lines']} خط)")
        else:
            safe_print(f"⚠️ {result['error_type']}")

    safe_print("")

    # ═══════════════════════════════════════════════════════
    # آمار
    # ═══════════════════════════════════════════════════════
    exists = sum(1 for r in results if r["exists"])
    can_import = sum(1 for r in results if r["can_import"])
    errors = sum(1 for r in results if r["exists"] and not r["can_import"])

    safe_print("=" * 100)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 100)
    safe_print(f"     کل: {len(results)}")
    safe_print(f"     ✅ import موفق: {can_import}")
    safe_print(f"     ⚠️ خطا: {errors}")
    safe_print(f"     ❌ نیست: {len(results) - exists}")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # ذخیره گزارش
    # ═══════════════════════════════════════════════════════
    lines = []
    lines.append("=" * 100)
    lines.append(f"  🧪 گزارش تست فایل‌های مهم")
    lines.append(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"  کل: {len(results)}")
    lines.append(f"  ✅ import موفق: {can_import}")
    lines.append(f"  ⚠️ خطا: {errors}")
    lines.append(f"  ❌ نیست: {len(results) - exists}")
    lines.append("")
    lines.append("=" * 100)
    lines.append("  📝 نتایج تفصیلی:")
    lines.append("=" * 100)
    lines.append("")

    lines.append("\n✅ import موفق:")
    lines.append("-" * 100)
    for r in results:
        if r["can_import"]:
            lines.append(f"  ✅ {r['file']:<60} ({r['lines']} خط)")

    lines.append("\n⚠️ خطا در import:")
    lines.append("-" * 100)
    for r in results:
        if r["exists"] and not r["can_import"]:
            lines.append(f"  ⚠️ {r['file']:<60}")
            lines.append(f"     نوع: {r['error_type']}")
            lines.append(f"     پیام: {r['error']}")

    lines.append("\n❌ فایل نیست:")
    lines.append("-" * 100)
    for r in results:
        if not r["exists"]:
            lines.append(f"  ❌ {r['file']}")

    lines.append("\n" + "=" * 100)
    lines.append("  📊 خطاها بر اساس نوع:")
    lines.append("=" * 100)
    lines.append("")

    error_types = {}
    for r in results:
        if r["exists"] and not r["can_import"]:
            et = r["error_type"] or "Unknown"
            error_types[et] = error_types.get(et, 0) + 1

    for et, count in sorted(error_types.items(), key=lambda x: -x[1]):
        lines.append(f"  {et}: {count}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    safe_print("=" * 100)
    safe_print(f"  💾 گزارش ذخیره شد: {OUTPUT_FILE}")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
