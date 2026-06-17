#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A zero-dependency i18n translation checker for a Flask/Jinja project.
# It scans templates and Python files for translation keys used as t('...'),
# compares them with translations/*.json, and reports missing/unused keys.
# Optionally autofixes missing keys by copying from the default language
# or inserting TODO placeholders.
#
# Usage:
#   python i18n_check.py               # run in project root
#   python i18n_check.py --root .
#   python i18n_check.py --default zh-CN --autofix --write
#
# Exit code is 0 if no missing keys, 1 otherwise (handy for CI).

import argparse, sys, json, re
from pathlib import Path

TEMPLATE_DIR = "templates"
TRANSLATIONS_DIR = "translations"

# Regex to find t('key') or t("key"), allowing spaces and a trailing default value.
T_CALL_RE = re.compile(r"""t\(\s*['\"]([^'\"]+)['\"]\s*(?:,|\))""")


def flatten_keys(obj, prefix=""):
    """Flatten dict to dotted keys. Lists are treated as leaf values (no indices)."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys |= flatten_keys(v, p)
            else:
                keys.add(p)
    else:
        if prefix:
            keys.add(prefix)
    return keys


def load_lang(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, str(e)


def scan_used_keys(project_root: Path):
    used = set()
    # 1) templates
    tdir = project_root / TEMPLATE_DIR
    if tdir.exists():
        for p in tdir.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".html", ".jinja", ".jinja2", ".htm"}:
                try:
                    s = p.read_text(encoding="utf-8", errors="ignore")
                    for m in T_CALL_RE.finditer(s):
                        used.add(m.group(1))
                except Exception:
                    pass
    # 2) python files
    for p in project_root.rglob("*.py"):
        # Skip virtual envs and dist dirs
        if any(part in {"venv", ".venv", "site-packages", "node_modules", "dist", "build", ".git"} for part in p.parts):
            continue
        try:
            s = p.read_text(encoding="utf-8", errors="ignore")
            for m in T_CALL_RE.finditer(s):
                used.add(m.group(1))
        except Exception:
            pass
    return used


def write_report(report_path: Path, default_lang: str, used_keys, lang_keys_map, missing_map, extra_map):
    lines = []
    lines.append("# i18n Report\n")
    lines.append(f"- Default language: **{default_lang}**")
    lines.append(f"- Total used keys: **{len(used_keys)}**\n")
    for lang, present in lang_keys_map.items():
        lines.append(f"## {lang}")
        lines.append(f"- Present keys: {len(present)}")
        missing = sorted(missing_map.get(lang, []))
        extra = sorted(extra_map.get(lang, []))
        lines.append(f"- Missing keys: {len(missing)}")
        if missing:
            lines.append("  - " + "\n  - ".join(missing))
        lines.append(f"- Unused keys: {len(extra)}")
        if extra:
            lines.append("  - " + "\n  - ".join(extra))
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def set_nested(dct, dotted_key, value):
    parts = dotted_key.split(".")
    cur = dct
    for i, part in enumerate(parts):
        if i == len(parts)-1:
            cur[part] = value
        else:
            cur = cur.setdefault(part, {})


def get_nested(dct, dotted_key):
    parts = dotted_key.split(".")
    cur = dct
    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Project root (contains templates/, translations/)")
    ap.add_argument("--default", dest="default_lang", default="zh-CN", help="Default language to copy from when autofix")
    ap.add_argument("--autofix", action="store_true", help="Autofill missing keys (copy from default or insert TODO)")
    ap.add_argument("--write", action="store_true", help="Write changes to translation files when used with --autofix")
    ap.add_argument("--report", default="i18n_report.md", help="Output report file path")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tdir = root / TRANSLATIONS_DIR
    if not tdir.exists():
        print(f"[ERR] translations/ not found under {root}", file=sys.stderr)
        return 2

    # Discover languages
    lang_files = {p.stem: p for p in tdir.glob("*.json")}
    if not lang_files:
        print(f"[ERR] No translations/*.json found", file=sys.stderr)
        return 2

    used_keys = scan_used_keys(root)

    # Load languages and flatten
    lang_data = {}
    lang_keys_map = {}
    errors = []
    for lang, path in lang_files.items():
        data, err = load_lang(path)
        if err:
            errors.append(f"{lang}: {err}")
            continue
        lang_data[lang] = data
        lang_keys_map[lang] = flatten_keys(data)

    if errors:
        for e in errors:
            print(f"[ERR] {e}", file=sys.stderr)
        return 2

    missing_map = {}
    extra_map = {}
    for lang, present in lang_keys_map.items():
        missing = sorted(used_keys - present)
        extra = sorted(present - used_keys)
        missing_map[lang] = missing
        extra_map[lang] = extra

    # Report
    report_path = root / args.report
    write_report(report_path, args.default_lang, used_keys, lang_keys_map, missing_map, extra_map)
    print(f"[OK] Wrote report: {report_path}")

    # Autofix
    if args.autofix:
        default_data = lang_data.get(args.default_lang)
        if default_data is None:
            print(f"[ERR] Default language {args.default_lang} not found among: {list(lang_data)}", file=sys.stderr)
            return 2
        changed = False
        for lang in lang_data:
            if lang == args.default_lang:
                continue
            data = lang_data[lang]
            for key in missing_map.get(lang, []):
                src = get_nested(default_data, key)
                if src is None:
                    src = f"TODO: translate '{key}'"
                set_nested(data, key, src)
                changed = True
        if changed and args.write:
            for lang, path in lang_files.items():
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(lang_data[lang], f, ensure_ascii=False, indent=2)
            print("[OK] Missing keys have been autofilled and files updated.")
        elif changed:
            print("[DRY-RUN] Missing keys would be autofilled. Re-run with --write to save changes.")
        else:
            print("[OK] No missing keys to autofix.")

    # Exit code: 0 if all languages have no missing keys
    any_missing = any(missing_map[lang] for lang in missing_map)
    return 1 if any_missing else 0


if __name__ == "__main__":
    sys.exit(main())
