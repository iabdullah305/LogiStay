import csv
import os
import re
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "build", "i18n", "sources_en.csv")
AR_OUT = os.path.join(ROOT, "translations", "ar.csv")

PATTERNS = [
    re.compile(r"_\(['\"]([^'\"]+)['\"]\)"),
    re.compile(r"__\(['\"]([^'\"]+)['\"]\)"),
]

def iter_files(root):
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(('.py', '.js', '.ts', '.html', '.json')):
                yield os.path.join(base, f)

def extract_strings():
    strings = set()
    for fp in iter_files(ROOT):
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                text = fh.read()
        except Exception:
            continue
        for pat in PATTERNS:
            for m in pat.findall(text):
                strings.add(m.strip())
    return sorted(strings)

def write_csv(strings):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ts = datetime.utcnow().isoformat()
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['timestamp', ts])
        w.writerow(['source_text'])
        for s in strings:
            w.writerow([s])

def write_ar(strings):
    os.makedirs(os.path.dirname(AR_OUT), exist_ok=True)
    ts = datetime.utcnow().isoformat()
    with open(AR_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['timestamp', ts])
        w.writerow(['source_text', 'translation'])
        for s in strings:
            w.writerow([s, ''])

if __name__ == '__main__':
    strings = extract_strings()
    write_csv(strings)
    write_ar(strings)
    print(f"Extracted {len(strings)} strings -> {OUT} and {AR_OUT}")