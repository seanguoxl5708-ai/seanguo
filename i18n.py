import json, os
from flask import g, request

SUPPORTED = ["zh-CN", "en", "zh-TW"]
DEFAULT = "zh-CN"
_cache = {}

def _load(lang):
    lang = lang if lang in SUPPORTED else DEFAULT
    if lang in _cache:
        return _cache[lang]
    base = os.path.join(os.path.dirname(__file__), "translations")
    path = os.path.join(base, f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    except Exception:
        _cache[lang] = {}
    return _cache[lang]

def get_lang_from_request():
    lang = request.cookies.get("lang") or request.args.get("lang")
    if lang in SUPPORTED:
        return lang
    al = request.headers.get("Accept-Language", "")
    if al.lower().startswith("en"):
        return "en"
    if "zh" in al.lower():
        return "zh-CN"
    return DEFAULT

def set_current_lang(lang):
    g.lang = lang if lang in SUPPORTED else DEFAULT

def get_current_lang():
    return getattr(g, "lang", DEFAULT)

def t(key, default=None):
    lang = get_current_lang()
    data = _load(lang)
    cur = data
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            cur = None
            break
    if isinstance(cur, str):
        return cur
    if lang != DEFAULT:
        data = _load(DEFAULT)
        cur = data
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if isinstance(cur, str):
            return cur
    return default if default is not None else key