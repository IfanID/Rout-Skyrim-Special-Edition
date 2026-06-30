#!/usr/bin/env python3
"""
Skyrim Strings Exporter — v3.3.2 (SKIP FILTER HANYA UNTUK NON-DIALOG)
Extract strings dari XML Skyrim yang layak untuk diterjemahkan.
Filter berdasarkan TRANSLATE_LIST dan daftar nama dari folder filters/.
Semua file .py di filters/ akan dimuat otomatis.
"""

import sys
import re
import os
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILTERS_DIR = os.path.join(SCRIPT_DIR, 'filters')
if os.path.exists(FILTERS_DIR):
    sys.path.insert(0, FILTERS_DIR)

DEFAULT_INPUT = "input/Skyrim_english_english.xml"
DEFAULT_OUTPUT = "output/source.txt"

TRANSLATABLE_LIST = {
    'DIAL:FULL', 'INFO:RNAM', 'MESG:FULL', 'MESG:ITXT', 'GMST:DATA',
    'QUST:NNAM', 'LSCR:DESC', 'PERK:EPFD', 'PERK:EPF2', 'MGEF:DNAM', 'REGN:RDMP',
    'BOOK:DESC', 'BOOK:CNAM', 'SCRL:DESC', 'ACTI:RNAM', 'FLOR:RNAM', 'WOOP:TNAM', 'BPTD:BPTN',
}

SKIP_LIST = {
    'CELL:FULL', 'LCTN:FULL', 'WRLD:FULL', 'REFR:FULL',
    'NPC_:FULL', 'NPC_:SHRT', 'RACE:FULL', 'EYES:FULL', 'HDPT:FULL', 'CLAS:FULL',
    'ARMO:FULL', 'WEAP:FULL', 'MISC:FULL', 'BOOK:FULL', 'SCRL:FULL',
    'AMMO:FULL', 'KEYM:FULL', 'SLGM:FULL', 'APPA:FULL', 'ALCH:FULL', 'INGR:FULL',
    'SPEL:FULL', 'MGEF:FULL', 'ENCH:FULL', 'SHOU:FULL', 'WOOP:FULL',
    'PROJ:FULL', 'EXPL:FULL', 'HAZD:FULL',
    'FACT:FULL', 'FACT:MNAM', 'FACT:FNAM',
    'FURN:FULL', 'ACTI:FULL', 'CONT:FULL', 'DOOR:FULL', 'FLOR:FULL',
    'TREE:FULL', 'LIGH:FULL', 'WATR:FULL', 'TACT:FULL',
    'QUST:FULL', 'PERK:FULL', 'AVIF:FULL', 'CLFM:FULL', 'SNCT:FULL',
}

GMST_SKIP_PATTERNS = [
    r'^\s*[-+]?\d+(\.\d+)?\s*$',
    r'^[a-zA-Z_][a-zA-Z0-9_]*$',
    r'^\s*$',
    r'^[A-Z][a-z]+[A-Z]',
]

# REC yang TIDAK BOLEH di-skip filter nama (dialog/narasi)
NO_FILTER_SKIP_REC = {'DIAL:FULL', 'INFO:RNAM', 'MESG:FULL', 'BOOK:DESC'}

def auto_load_filters(filters_dir):
    filter_dict = defaultdict(list)
    if not os.path.isdir(filters_dir):
        return filter_dict
    py_files = [f for f in os.listdir(filters_dir) if f.endswith('.py') and f != '__init__.py']
    for py_file in py_files:
        module_name = py_file[:-3]
        try:
            mod = __import__(module_name)
            for attr_name in dir(mod):
                if attr_name.endswith('_NAMES'):
                    val = getattr(mod, attr_name)
                    if isinstance(val, list):
                        category = attr_name.replace('_NAMES', '').upper()
                        filter_dict[category].extend(val)
        except ImportError:
            pass
    return filter_dict

FILTERS = auto_load_filters(FILTERS_DIR)

patterns = {}
for category, names in FILTERS.items():
    if names:
        escaped = [re.escape(name) for name in names]
        patterns[category] = re.compile(r'\b(?:' + '|'.join(escaped) + r')\b', re.IGNORECASE)
    else:
        patterns[category] = None

print("ℹ️  Memuat filter dari folder 'filters/' secara otomatis...")
if FILTERS:
    for category, names in FILTERS.items():
        print(f"   {category:12s}: {len(names):,} nama")
else:
    print("   (tidak ada filter ditemukan)")
print()

def is_gmst_translatable(text):
    if not text or not text.strip():
        return False
    for pat in GMST_SKIP_PATTERNS:
        if re.match(pat, text.strip()):
            return False
    return bool(re.search(r'[a-zA-Z]', text) and (' ' in text.strip() or len(text.strip()) > 20))

def is_translatable(rec_val, source_text=""):
    if not rec_val:
        return False
    if rec_val in TRANSLATABLE_LIST:
        if rec_val == 'GMST:DATA':
            return is_gmst_translatable(source_text)
        return True
    if rec_val in SKIP_LIST:
        return False
    return False

def main():
    if len(sys.argv) == 1:
        input_file = DEFAULT_INPUT
        output_file = DEFAULT_OUTPUT
        print("ℹ️  Menggunakan path default:")
        print(f"   Input  : {input_file}")
        print(f"   Output : {output_file}")
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python export.py [input_xml] [output_txt]")
        sys.exit(1)

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if not Path(input_file).exists():
        print(f"❌ File tidak ditemukan: {input_file}")
        sys.exit(1)

    print(f"📖 Membaca: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    string_pattern = r'<String\s+List="[^"]*"\s+sID="([^"]*)">.*?<EDID>([^<]*)</EDID>.*?<REC[^>]*>([^<]*)</REC>.*?<Source>([^<]*)</Source>.*?<Dest>([^<]*)</Dest>.*?</String>'
    matches = list(re.finditer(string_pattern, content, re.DOTALL))

    if not matches:
        print("❌ Tidak ada <String> blocks ditemukan.")
        sys.exit(1)

    print(f"✓ Ditemukan {len(matches):,} <String> blocks\n")
    print("=" * 80)
    print("  SKYRIM STRINGS EXPORTER v3.3.2 (skip filter hanya non-dialog)")
    print("=" * 80)
    print(f"  Total input strings : {len(matches):,}")
    print("-" * 80)

    output_lines = []
    stats = {
        'total': len(matches),
        'exported': 0,
        'skipped_proper_noun': 0,
        'skipped_gmst_filter': 0,
    }
    for category in FILTERS:
        stats[f'skipped_{category.lower()}'] = 0

    for i, match in enumerate(matches):
        sid = match.group(1)
        rec_val = match.group(3).strip()
        source_text = match.group(4).strip()
        dest_text = match.group(5).strip()

        source_text = (source_text
            .replace('&lt;', '<').replace('&gt;', '>')
            .replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'"))
        dest_text = (dest_text
            .replace('&lt;', '<').replace('&gt;', '>')
            .replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'"))

        if not is_translatable(rec_val, source_text):
            if rec_val in SKIP_LIST:
                stats['skipped_proper_noun'] += 1
            elif rec_val == 'GMST:DATA':
                stats['skipped_gmst_filter'] += 1
            else:
                stats['skipped_proper_noun'] += 1
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s}")
            continue

        # Deteksi filter hanya untuk statistik dan skip selektif
        skipped = False
        for category, pattern in patterns.items():
            if pattern and pattern.search(source_text):
                stats[f'skipped_{category.lower()}'] += 1
                skipped = True
                break

        # Skip hanya jika bukan dialog/narasi
        if skipped and rec_val not in NO_FILTER_SKIP_REC:
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | FILTER")
            continue

        # Jika sampai sini, string diekspor
        output_lines.append('-')
        output_lines.append(f'sID="{sid}"')
        output_lines.append(f'<REC>{rec_val}</REC>')
        output_lines.append(f'<Source>{source_text}</Source>')
        output_lines.append(f'<Dest>{dest_text}</Dest>')
        output_lines.append('-')
        output_lines.append('')

        stats['exported'] += 1
        if i % 100 == 0 or i == len(matches)-1:
            print(f"[{i+1:5d}/{len(matches)}] [OK]   {rec_val:15s} | Exported: {stats['exported']:,}")

    print("\n" + "=" * 80)
    print(f"  Menulis {stats['exported']:,} strings ke {output_file}...")
    print("=" * 80)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"✓ File tersimpan: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("  STATISTIK EXPORT")
    print("=" * 80)
    print(f"  Total input               : {stats['total']:,}")
    print(f"  ✓ Di-export (translatable): {stats['exported']:,}")
    print(f"  ✗ Skip (proper noun)      : {stats['skipped_proper_noun']:,}")
    print(f"  ✗ Skip (GMST filter)      : {stats['skipped_gmst_filter']:,}")
    for category in FILTERS:
        key = f'skipped_{category.lower()}'
        if key in stats:
            print(f"  📊 String mengandung {category:12s}: {stats[key]:,} (hanya non-dialog yang diskip)")
    print("-" * 80)
    export_rate = (stats['exported'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Export rate: {export_rate:.1f}%")
    print("=" * 80)
    print("\n  ✓ Langkah selanjutnya: jalankan tl.bat untuk menerjemahkan")
    print("=" * 80)

if __name__ == '__main__':
    main()