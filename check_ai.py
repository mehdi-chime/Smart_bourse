# check_ai.py
# بررسی کامل محتوای ai/
# اجرا: python check_ai.py

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
AI_DIR = PROJECT_ROOT / "ai"
OUTPUT_FILE = PROJECT_ROOT / "ai_report.txt"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def analyze_file(file_path):
    """تحلیل یه فایل AI"""
    result = {
        "name": file_path.name,
        "path": str(file_path.relative_to(PROJECT_ROOT)),
        "size": file_path.stat().st_size,
        "lines": 0,
        "classes": [],
        "functions": [],
        "imports": [],
        "has_save": False,
        "has_load": False,
        "has_learn": False,
        "has_predict": False,
        "has_feedback": False,
        "docstring": "",
    }

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        result["lines"] = len(content.split("\n"))

        # docstring اول
        if '"""' in content[:500]:
            start = content.find('"""') + 3
            end = content.find('"""', start)
            if end > start:
                result["docstring"] = content[start:end].strip()[:200]

        # کلاس‌ها
        import re
        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        result["classes"] = classes

        # توابع
        functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
        result["functions"] = functions

        # importها
        imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
        result["imports"] = list(set(imports))[:10]

        # کلمات کلیدی
        result["has_save"] = any(kw in content for kw in ["save", "dump", "write", "ذخیره"])
        result["has_load"] = any(kw in content for kw in ["load", "read", "json.load", "بارگذاری"])
        result["has_learn"] = any(kw in content for kw in ["learn", "train", "fit", "یادگیری"])
        result["has_predict"] = any(kw in content for kw in ["predict", "forecast", "پیش‌بینی"])
        result["has_feedback"] = any(kw in content for kw in ["feedback", "backtest", "compare", "بازخورد"])

    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🔍 بررسی کامل ai/")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    if not AI_DIR.exists():
        safe_print(f"  ❌ پوشه پیدا نشد: {AI_DIR}")
        return

    py_files = list(AI_DIR.glob("*.py"))
    safe_print(f"  📊 {len(py_files)} فایل py")
    safe_print("")

    results = []
    for f in sorted(py_files):
        r = analyze_file(f)
        results.append(r)

    # نمایش
    for r in results:
        safe_print(f"  📄 {r['name']}")
        safe_print(f"     خطوط: {r['lines']}, حجم: {r['size']:,} b")

        if r['docstring']:
            safe_print(f"     📝 {r['docstring'][:100]}")

        if r['classes']:
            safe_print(f"     📦 کلاس‌ها: {', '.join(r['classes'])}")

        if r['functions']:
            safe_print(f"     ⚙️ توابع: {', '.join(r['functions'][:5])}")

        flags = []
        if r['has_save']: flags.append("💾 save")
        if r['has_load']: flags.append("📂 load")
        if r['has_learn']: flags.append("🎓 learn")
        if r['has_predict']: flags.append("🔮 predict")
        if r['has_feedback']: flags.append("🔄 feedback")

        if flags:
            safe_print(f"     🏷️ {', '.join(flags)}")

        safe_print("")

    # ذخیره گزارش
    lines = []
    lines.append("=" * 100)
    lines.append(f"  🔍 گزارش ai/")
    lines.append(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")

    for r in results:
        lines.append(f"\n{'='*80}")
        lines.append(f"📄 {r['path']}")
        lines.append(f"{'='*80}")
        lines.append(f"خطوط: {r['lines']}")
        lines.append(f"حجم: {r['size']:,} bytes")
        lines.append(f"کلاس‌ها: {r['classes']}")
        lines.append(f"توابع: {r['functions']}")
        lines.append(f"importها: {r['imports']}")
        lines.append(f"save: {r['has_save']}")
        lines.append(f"load: {r['has_load']}")
        lines.append(f"learn: {r['has_learn']}")
        lines.append(f"predict: {r['has_predict']}")
        lines.append(f"feedback: {r['has_feedback']}")
        lines.append("")

    # محتوای کامل
    lines.append("\n" + "=" * 100)
    lines.append("  📝 محتوای کامل:")
    lines.append("=" * 100)

    for f in sorted(py_files):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            lines.append(f"\n\n{'='*80}")
            lines.append(f"📄 {f.relative_to(PROJECT_ROOT)}")
            lines.append(f"{'='*80}\n")
            lines.append(content)
        except:
            pass

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    safe_print("=" * 100)
    safe_print(f"  ✅ گزارش ذخیره شد: {OUTPUT_FILE}")
    safe_print(f"  📏 حجم: {len('\n'.join(lines)):,} کاراکتر")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
