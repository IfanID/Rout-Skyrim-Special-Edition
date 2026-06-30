#!/usr/bin/env python3
"""
Skyrim Strings Exporter — v3.2 (filter NPC + Item + Armor + Jewelry)
Extract strings dari XML Skyrim yang layak untuk diterjemahkan.
Filter berdasarkan TRANSLATE_LIST dan daftar nama dari folder filters/.
"""

import sys
import re
import os
from pathlib import Path

# ============================================
# Tambahkan path ke subfolder filters agar bisa diimport
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILTERS_DIR = os.path.join(SCRIPT_DIR, 'filters')
sys.path.insert(0, FILTERS_DIR)

# ============================================
# DEFAULT PATHS
# ============================================
DEFAULT_INPUT = "input/Skyrim_english_english.xml"
DEFAULT_OUTPUT = "output/source.txt"

# ============================================
# DAFTAR REC YANG BISA DITERJEMAHKAN (TRANSLATABLE)
# ============================================
TRANSLATABLE_LIST = {
    'DIAL:FULL', 'INFO:RNAM', 'MESG:FULL', 'MESG:ITXT', 'GMST:DATA',
    'QUST:NNAM', 'LSCR:DESC', 'PERK:EPFD', 'PERK:EPF2', 'MGEF:DNAM', 'REGN:RDMP',
    'BOOK:DESC', 'BOOK:CNAM', 'SCRL:DESC', 'ACTI:RNAM', 'FLOR:RNAM', 'WOOP:TNAM', 'BPTD:BPTN',
}

# ============================================
# DAFTAR REC YANG DI-SKIP
# ============================================
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

# ============================================
# GMST:DATA Filter
# ============================================
GMST_SKIP_PATTERNS = [
    r'^\s*[-+]?\d+(\.\d+)?\s*$',    # Angka murni
    r'^[a-zA-Z_][a-zA-Z0-9_]*$',     # EditorID
    r'^\s*$',                         # Kosong
    r'^[A-Z][a-z]+[A-Z]',            # CamelCase murni
]

# ============================================
# Muat semua filter dari folder filters/
# ============================================
def load_filter(module_name, attr_name='NAMES'):
    """Muat daftar dari modul filter, return list kosong jika gagal."""
    try:
        mod = __import__(module_name)
        names = getattr(mod, attr_name, [])
        if isinstance(names, list):
            return names
        return []
    except ImportError:
        return []

# Load semua filter
NPC_NAMES = load_filter('npc', 'NPC_NAMES')
ITEM_NAMES = load_filter('items', 'ITEM_NAMES')
ARMOR_NAMES = load_filter('armor', 'ARMOR_NAMES')
JEWELRY_NAMES = load_filter('jewelry', 'JEWELRY_NAMES')

# ============================================
# Buat pola regex untuk masing-masing filter
# ============================================
def build_pattern(names):
    if not names:
        return None
    escaped = [re.escape(name) for name in names]
    return re.compile(r'\b(?:' + '|'.join(escaped) + r')\b', re.IGNORECASE)

npc_pattern = build_pattern(NPC_NAMES)
item_pattern = build_pattern(ITEM_NAMES)
armor_pattern = build_pattern(ARMOR_NAMES)
jewelry_pattern = build_pattern(JEWELRY_NAMES)

# Tampilkan info
print("ℹ️  Memuat filter dari folder 'filters/'...")
print(f"   NPC filter    : {len(NPC_NAMES) if NPC_NAMES else 0} nama")
print(f"   Item filter   : {len(ITEM_NAMES) if ITEM_NAMES else 0} nama")
print(f"   Armor filter  : {len(ARMOR_NAMES) if ARMOR_NAMES else 0} nama")
print(f"   Jewelry filter: {len(JEWELRY_NAMES) if JEWELRY_NAMES else 0} nama")
print()

# ============================================
# Fungsi filter
# ============================================
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

def contains_any(text, pattern):
    if not pattern or not text:
        return False
    return bool(pattern.search(text))

# ============================================
# Main
# ============================================
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
    print("  SKYRIM STRINGS EXPORTER v3.2 (filter NPC + Item + Armor + Jewelry)")
    print("=" * 80)
    print(f"  Total input strings : {len(matches):,}")
    print("-" * 80)

    output_lines = []
    stats = {
        'total': len(matches),
        'exported': 0,
        'skipped_proper_noun': 0,
        'skipped_gmst_filter': 0,
        'skipped_npc': 0,
        'skipped_item': 0,
        'skipped_armor': 0,
        'skipped_jewelry': 0,
    }

    for i, match in enumerate(matches):
        sid = match.group(1)
        rec_val = match.group(3).strip()
        source_text = match.group(4).strip()
        dest_text = match.group(5).strip()

        # Unescape
        source_text = (source_text
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&amp;', '&')
            .replace('&quot;', '"')
            .replace('&apos;', "'"))
        dest_text = (dest_text
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&amp;', '&')
            .replace('&quot;', '"')
            .replace('&apos;', "'"))

        # Filter REC
        if not is_translatable(rec_val, source_text):
            if rec_val in SKIP_LIST:
                stats['skipped_proper_noun'] += 1
                reason = "PROPER NOUN"
            elif rec_val == 'GMST:DATA':
                stats['skipped_gmst_filter'] += 1
                reason = "GMST FILTER"
            else:
                stats['skipped_proper_noun'] += 1
                reason = "NOT IN LIST"
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | {reason}")
            continue

        # Filter NPC
        if contains_any(source_text, npc_pattern):
            stats['skipped_npc'] += 1
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | NPC NAME")
            continue

        # Filter Item
        if contains_any(source_text, item_pattern):
            stats['skipped_item'] += 1
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | ITEM NAME")
            continue

        # Filter Armor
        if contains_any(source_text, armor_pattern):
            stats['skipped_armor'] += 1
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | ARMOR NAME")
            continue

        # Filter Jewelry
        if contains_any(source_text, jewelry_pattern):
            stats['skipped_jewelry'] += 1
            if i % 100 == 0 or i == len(matches)-1:
                print(f"[{i+1:5d}/{len(matches)}] [SKIP] {rec_val:15s} | JEWELRY NAME")
            continue

        # Export
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

    # Tulis output
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

    # Statistik
    print("\n" + "=" * 80)
    print("  STATISTIK EXPORT")
    print("=" * 80)
    print(f"  Total input               : {stats['total']:,}")
    print(f"  ✓ Di-export (translatable): {stats['exported']:,}")
    print(f"  ✗ Skip (proper noun)      : {stats['skipped_proper_noun']:,}")
    print(f"  ✗ Skip (GMST filter)      : {stats['skipped_gmst_filter']:,}")
    print(f"  ✗ Skip (NPC name)         : {stats['skipped_npc']:,}")
    print(f"  ✗ Skip (Item name)        : {stats['skipped_item']:,}")
    print(f"  ✗ Skip (Armor name)       : {stats['skipped_armor']:,}")
    print(f"  ✗ Skip (Jewelry name)     : {stats['skipped_jewelry']:,}")
    print("-" * 80)
    export_rate = (stats['exported'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Export rate: {export_rate:.1f}%")
    print("=" * 80)
    print("\n  ✓ Langkah selanjutnya: jalankan tl.bat untuk menerjemahkan")
    print("=" * 80)

if __name__ == '__main__':
    main()