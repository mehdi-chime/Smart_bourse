# deep_scan.py
# اسکن عمیق پروژه Smart_Bourse
# اجرا: python deep_scan.py

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

ROOT = Path(__file__).parent.resolve()
OUTPUT = ROOT / "reports" / f"deep_scan_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"

SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'env',
             'node_modules', '.idea', '.vscode', 'backup', 'data', 'logs'}


def get_file_info(filepath):
    """اطلاعات کامل یه فایل پایتون"""
    info = {
        "path": str(filepath.relative_to(ROOT)),
        "size": filepath.stat().st_size,
        "lines": 0,
        "docstring": "",
        "imports": [],
        "classes": [],
        "functions": [],
        "has_main": False,
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            info["lines"] = len(lines)

            # docstring اول
            doc_match = re.search(r'^"""(.+?)"""', content, re.DOTALL)
            if doc_match:
                info["docstring"] = doc_match.group(1).strip()[:200]
            else:
                # کامنت‌های اول
                first_lines = []
                for line in lines[:15]:
                    if line.strip().startswith('#'):
                        first_lines.append(line.strip('# ').strip())
                    elif line.strip():
                        break
                info["docstring"] = " | ".join(first_lines)[:200]

            # importها
            for match in re.finditer(r'^(?:from|import)\s+([\w\.]+)', content, re.MULTILINE):
                info["imports"].append(match.group(1))

            # کلاس‌ها
            for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                info["classes"].append(match.group(1))

            # توابع
            for match in re.finditer(r'^def\s+(\w+)', content, re.MULTILINE):
                info["functions"].append(match.group(1))

            # main
            if '__main__' in content:
                info["has_main"] = True

    except Exception as e:
        info["error"] = str(e)

    return info


def find_connections(all_files):
    """پیدا کردن ارتباط بین فایل‌ها"""
    connections = defaultdict(set)  # فایل → فایل‌هایی که import می‌کنه
    imported_by = defaultdict(set)  # فایل → فایل‌هایی که importش می‌کنن

    # اسم ماژول‌ها
    module_map = {}
    for rel in all_files:
        module_name = rel.replace('\\', '/').replace('.py', '').replace('/', '.')
        module_map[module_name] = rel
        # فقط اسم آخر
        short_name = rel.replace('\\', '/').split('/')[-1].replace('.py', '')
        if short_name not in module_map:
            module_map[short_name] = rel

    for rel in all_files:
        full = ROOT / rel
        try:
            with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for match in re.finditer(r'^(?:from|import)\s+([\w\.]+)', content, re.MULTILINE):
                module = match.group(1)
                # چک کن ماژول داخلیه یا نه
                if module in module_map:
                    target = module_map[module]
                    if target != rel:
                        connections[rel].add(target)
                        imported_by[target].add(rel)
                else:
                    # شاید short name
                    parts = module.split('.')
                    if parts[0] in module_map:
                        target = module_map[parts[0]]
                        if target != rel:
                            connections[rel].add(target)
                            imported_by[target].add(rel)
        except:
            pass

    return connections, imported_by


def main():
    print()
    print("=" * 90)
    print("  🔍 SMART_BOURSE - DEEP SCAN")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    print()

    # ۱. جمع‌آوری همه فایل‌های پایتون
    print("  مرحله ۱: جمع‌آوری فایل‌ها...")
    all_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith('.py'):
                full = Path(dirpath) / f
                rel = str(full.relative_to(ROOT))
                all_files.append(rel)

    print(f"  ✅ {len(all_files)} فایل پایتون")
    print()

    # ۲. اطلاعات هر فایل
    print("  مرحله ۲: استخراج اطلاعات...")
    infos = []
    for i, rel in enumerate(all_files, 1):
        if i % 20 == 0:
            print(f"    {i}/{len(all_files)}...")
        info = get_file_info(ROOT / rel)
        infos.append(info)
    print(f"  ✅ تمام")
    print()

    # ۳. ارتباطات
    print("  مرحله ۳: پیدا کردن ارتباطات...")
    connections, imported_by = find_connections(all_files)
    print(f"  ✅ تمام")
    print()

    # ۴. گزارش
    print("  مرحله ۴: نوشتن گزارش...")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        # هدر
        f.write("=" * 90 + "\n")
        f.write("SMART_BOURSE - DEEP SCAN REPORT\n")
        f.write(f"تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 90 + "\n\n")

        # خلاصه
        f.write("## 📊 خلاصه\n\n")
        f.write(f"تعداد فایل‌های پایتون: {len(infos)}\n")
        total_lines = sum(i["lines"] for i in infos)
        f.write(f"جمع کل خطوط: {total_lines:,}\n")
        f.write(f"میانگین خطوط: {total_lines // len(infos)}\n\n")

        # پوشه‌ها
        f.write("## 📁 پوشه‌ها\n\n")
        by_dir = defaultdict(list)
        for info in infos:
            parts = info["path"].split('\\')
            dir_name = parts[0] if len(parts) > 1 else "ریشه"
            by_dir[dir_name].append(info)

        for dir_name in sorted(by_dir.keys()):
            files = by_dir[dir_name]
            total = sum(x["lines"] for x in files)
            f.write(f"  📁 {dir_name}: {len(files)} فایل، {total:,} خط\n")

        f.write("\n")

        # فایل‌های اصلی (بیشترین import)
        f.write("## 🎯 فایل‌های اصلی (بیشترین import)\n\n")
        sorted_by_import = sorted(imported_by.items(), key=lambda x: -len(x[1]))
        for rel, importers in sorted_by_import[:30]:
            f.write(f"  ✅ {rel} ← {len(importers)} فایل\n")

        f.write("\n")

        # فایل‌های یتیم
        f.write("## 🟡 فایل‌های یتیم (هیچ‌جا import نشدن)\n\n")
        for info in infos:
            rel = info["path"]
            if rel not in imported_by and info["lines"] > 20:
                f.write(f"  🟡 {rel} ({info['lines']} خط)\n")

        f.write("\n")

        # فایل‌های با main
        f.write("## 🚀 فایل‌هایی که مستقیم اجرا می‌شن (has __main__)\n\n")
        for info in infos:
            if info["has_main"]:
                f.write(f"  🚀 {info['path']} ({info['lines']} خط)\n")

        f.write("\n")

        # جزئیات هر فایل
        f.write("=" * 90 + "\n")
        f.write("## 📋 جزئیات هر فایل\n")
        f.write("=" * 90 + "\n\n")

        for info in sorted(infos, key=lambda x: x["path"]):
            f.write(f"### {info['path']}\n")
            f.write(f"  📏 {info['lines']} خط | 💾 {info['size']:,} بایت\n")

            if info["docstring"]:
                f.write(f"  📝 {info['docstring']}\n")

            if info["classes"]:
                f.write(f"  🏛️ کلاس‌ها: {', '.join(info['classes'][:5])}\n")

            if info["functions"]:
                f.write(f"  ⚙️ توابع: {', '.join(info['functions'][:8])}\n")

            if info["imports"]:
                internal = [i for i in info["imports"] if not i.startswith(('os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing', 'collections', 'math', 'numpy', 'pandas'))]
                if internal:
                    f.write(f"  📦 importهای داخلی: {', '.join(internal[:10])}\n")

            if info["has_main"]:
                f.write(f"  🚀 قابل اجرا\n")

            f.write("\n")

        # تکراری‌ها
        f.write("=" * 90 + "\n")
        f.write("## 🔴 فایل‌های با اسم تکراری\n")
        f.write("=" * 90 + "\n\n")

        names = defaultdict(list)
        for info in infos:
            name = info["path"].split('\\')[-1]
            names[name].append(info["path"])

        for name, paths in sorted(names.items()):
            if len(paths) > 1:
                f.write(f"🔴 {name}:\n")
                for p in paths:
                    f.write(f"    {p}\n")
                f.write("\n")

    print(f"  ✅ گزارش: {OUTPUT}")
    print()
    print("=" * 90)
    print("  ✅ تمام شد!")
    print("=" * 90)
    print()
    print(f"  📄 فایل گزارش رو باز کن و برام بفرست:")
    print(f"     {OUTPUT}")
    print()
    print("  ⚠️ اگه فایل بزرگه، فقط ۵۰۰ خط اول رو بفرست.")
    print()


if __name__ == "__main__":
    main()
