# analyze_ai_deep.py
# تحلیل عمیق ai/ — محتوا، کلاس‌ها، متدها، منطق
# اجرا: python analyze_ai_deep.py

import os
import sys
import re
import json
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
OUTPUT_FILE = PROJECT_ROOT / "ai_deep_report.txt"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def extract_docstring(content):
    """استخراج docstring اول"""
    match = re.search(r'"""(.+?)"""', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_classes(content):
    """استخراج کلاس‌ها با متدهاشون"""
    classes = []
    
    # پیدا کردن کلاس‌ها
    class_pattern = r'^class\s+(\w+)(?:\(([^)]*)\))?:'
    for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        parent = match.group(2) or ""
        start = match.end()
        
        # پیدا کردن بدنه‌ی کلاس (تا کلاس بعدی یا EOF)
        next_class = re.search(r'^class\s+\w+', content[start:], re.MULTILINE)
        if next_class:
            body = content[start:start + next_class.start()]
        else:
            body = content[start:]
        
        # استخراج متدها
        methods = []
        method_pattern = r'^\s+def\s+(\w+)\s*\(([^)]*)\)'
        for m in re.finditer(method_pattern, body, re.MULTILINE):
            method_name = m.group(1)
            params = m.group(2)
            if not method_name.startswith("_"):
                methods.append({
                    "name": method_name,
                    "params": params.strip()[:100],
                })
        
        # docstring کلاس
        doc_match = re.search(r'"""(.+?)"""', body[:500], re.DOTALL)
        docstring = doc_match.group(1).strip() if doc_match else ""
        
        classes.append({
            "name": class_name,
            "parent": parent,
            "docstring": docstring[:200],
            "methods": methods,
        })
    
    return classes


def extract_functions(content):
    """استخراج توابع سطح بالا"""
    functions = []
    pattern = r'^def\s+(\w+)\s*\(([^)]*)\)'
    for m in re.finditer(pattern, content, re.MULTILINE):
        functions.append({
            "name": m.group(1),
            "params": m.group(2).strip()[:100],
        })
    return functions


def extract_imports(content):
    """استخراج importها"""
    imports = []
    pattern = r'^(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)'
    for m in re.finditer(pattern, content, re.MULTILINE):
        if m.group(1):
            imports.append(f"from {m.group(1)} import {m.group(2).strip()}")
        else:
            imports.append(f"import {m.group(2).strip()}")
    return list(set(imports))[:20]


def extract_keywords(content):
    """استخراج کلمات کلیدی مهم"""
    keywords = {
        "save": ["save", "dump", "write", "json.dump"],
        "load": ["load", "read", "json.load"],
        "learn": ["learn", "train", "fit", "update"],
        "predict": ["predict", "forecast", "suggest", "recommend"],
        "feedback": ["feedback", "backtest", "compare", "evaluate"],
        "memory": ["memory", "history", "record", "storage"],
        "score": ["score", "weight", "rating", "confidence"],
        "signal": ["signal", "buy", "sell", "hold"],
        "eitaa": ["eitaa", "eitaayar", "send_message"],
        "algotik": ["algotik", "att.", "get_live_market"],
    }
    
    found = {}
    for category, kws in keywords.items():
        matches = []
        for kw in kws:
            if kw in content:
                matches.append(kw)
        if matches:
            found[category] = matches
    
    return found


def extract_save_load_paths(content):
    """استخراج مسیرهای save/load"""
    paths = []
    
    # الگوهای رایج
    patterns = [
        r'["\']([^"\']*\.json)["\']',
        r'["\']([^"\']*\.pkl)["\']',
        r'["\']([^"\']*data/[^"\']*)["\']',
        r'Path\(["\']([^"\']+)["\']\)',
    ]
    
    for pattern in patterns:
        for m in re.finditer(pattern, content):
            path = m.group(1)
            if path and len(path) < 100:
                paths.append(path)
    
    return list(set(paths))[:15]


def extract_logic_snippets(content):
    """استخراج تکه‌کدهای منطقی"""
    snippets = []
    
    # if/else با score
    if_pattern = r'if\s+.*?(?:score|confidence|weight).*?:'
    for m in re.finditer(if_pattern, content, re.IGNORECASE):
        line = m.group(0)[:100]
        snippets.append(f"IF: {line}")
    
    # return با score
    return_pattern = r'return\s+.*?(?:score|confidence|weight|signal)'
    for m in re.finditer(return_pattern, content, re.IGNORECASE):
        line = m.group(0)[:100]
        snippets.append(f"RETURN: {line}")
    
    return snippets[:10]


def analyze_file(file_path):
    """تحلیل کامل یه فایل"""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    
    return {
        "name": file_path.name,
        "path": str(file_path.relative_to(PROJECT_ROOT)),
        "size": file_path.stat().st_size,
        "lines": len(content.split("\n")),
        "docstring": extract_docstring(content),
        "classes": extract_classes(content),
        "functions": extract_functions(content),
        "imports": extract_imports(content),
        "keywords": extract_keywords(content),
        "paths": extract_save_load_paths(content),
        "logic": extract_logic_snippets(content),
    }


def build_report(analyses):
    """ساخت گزارش کامل"""
    lines = []
    
    lines.append("=" * 100)
    lines.append(f"  🧠 تحلیل عمیق ai/")
    lines.append(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    
    # خلاصه
    lines.append(f"  📊 خلاصه:")
    lines.append(f"     فایل‌ها: {len(analyses)}")
    lines.append(f"     کلاس‌ها: {sum(len(a['classes']) for a in analyses)}")
    lines.append(f"     توابع: {sum(len(a['functions']) for a in analyses)}")
    lines.append(f"     خطوط: {sum(a['lines'] for a in analyses)}")
    lines.append("")
    
    # هر فایل
    for a in analyses:
        lines.append("\n" + "=" * 100)
        lines.append(f"  📄 {a['name']}")
        lines.append("=" * 100)
        lines.append("")
        
        lines.append(f"  📁 مسیر: {a['path']}")
        lines.append(f"  📏 خطوط: {a['lines']}")
        lines.append(f"  💾 حجم: {a['size']:,} bytes")
        lines.append("")
        
        if a['docstring']:
            lines.append(f"  📝 توضیحات:")
            for line in a['docstring'].split("\n")[:15]:
                lines.append(f"     {line}")
            lines.append("")
        
        if a['imports']:
            lines.append(f"  📦 importها:")
            for imp in a['imports']:
                lines.append(f"     {imp}")
            lines.append("")
        
        if a['classes']:
            lines.append(f"  🏗️ کلاس‌ها:")
            for cls in a['classes']:
                parent = f" ({cls['parent']})" if cls['parent'] else ""
                lines.append(f"     📦 {cls['name']}{parent}")
                if cls['docstring']:
                    lines.append(f"        {cls['docstring'][:100]}")
                if cls['methods']:
                    lines.append(f"        متدها:")
                    for m in cls['methods']:
                        lines.append(f"           • {m['name']}({m['params'][:60]})")
            lines.append("")
        
        if a['functions']:
            lines.append(f"  ⚙️ توابع سطح بالا:")
            for f in a['functions']:
                lines.append(f"     • {f['name']}({f['params'][:60]})")
            lines.append("")
        
        if a['keywords']:
            lines.append(f"  🏷️ کلمات کلیدی:")
            for cat, kws in a['keywords'].items():
                lines.append(f"     {cat}: {', '.join(kws)}")
            lines.append("")
        
        if a['paths']:
            lines.append(f"  📂 مسیرهای فایل:")
            for p in a['paths']:
                lines.append(f"     {p}")
            lines.append("")
        
        if a['logic']:
            lines.append(f"  🧩 منطق (تکه‌کدها):")
            for l in a['logic'][:5]:
                lines.append(f"     {l}")
            lines.append("")
    
    return "\n".join(lines)


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🧠 تحلیل عمیق ai/")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")
    
    if not AI_DIR.exists():
        safe_print(f"  ❌ پوشه پیدا نشد: {AI_DIR}")
        return
    
    py_files = sorted(AI_DIR.glob("*.py"))
    safe_print(f"  📊 {len(py_files)} فایل py")
    safe_print("")
    
    analyses = []
    for f in py_files:
        safe_print(f"  🔍 تحلیل {f.name}...")
        try:
            a = analyze_file(f)
            analyses.append(a)
            safe_print(f"     ✅ {a['lines']} خط، {len(a['classes'])} کلاس")
        except Exception as e:
            safe_print(f"     ❌ خطا: {e}")
    
    safe_print("")
    safe_print("  📝 ساخت گزارش...")
    
    report = build_report(analyses)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    
    safe_print(f"     ✅ ذخیره: {OUTPUT_FILE}")
    safe_print(f"     📏 حجم: {len(report):,} کاراکتر")
    safe_print("")
    
    # خلاصه
    safe_print("=" * 100)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 100)
    safe_print("")
    
    for a in analyses:
        safe_print(f"  📄 {a['name']:<30} | {a['lines']:>4} خط | {len(a['classes'])} کلاس | {len(a['functions'])} تابع")
    
    safe_print("")
    safe_print("=" * 100)
    safe_print(f"  ✅ تمام!")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()
