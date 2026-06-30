#!/usr/bin/env python3
"""
Ganti nilai DEFAULT_INPUT pada export.py (atau script lain) secara aman.

- Memeriksa apakah file input XML yang baru benar-benar ada sebelum mengganti.
- Jika tidak ada, batalkan penggantian dan tampilkan DEFAULT_INPUT yang lama.
- Jika argumen input hanya nama file tanpa path, otomatis ditambahkan "input/".

Usage:
  python ganti.py <input_xml> [target_script]
Contoh:
  python ganti.py Dialog.xml
  python ganti.py input/Quest.xml scripts/export.py
"""

import sys
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TARGET = os.path.join(SCRIPT_DIR, "export.py")   # scripts/export.py

def get_current_default(content):
    """Ambil nilai DEFAULT_INPUT yang ada di konten file."""
    match = re.search(r'^\s*DEFAULT_INPUT\s*=\s*"([^"]*)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    return None

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python ganti.py <input_xml> [target_script]")
        print("Contoh:")
        print("  python ganti.py Dialog.xml")
        print("  python ganti.py input/Quest.xml scripts/export.py")
        sys.exit(1)

    new_input_raw = sys.argv[1]

    # Jika hanya nama file tanpa path, tambahkan "input/"
    if not any(sep in new_input_raw for sep in (os.sep, '/', '\\')):
        new_input = os.path.join("input", new_input_raw)
    else:
        new_input = new_input_raw

    new_input = new_input.replace('\\', '/')

    # Validasi: apakah file input XML yang baru ada?
    if not os.path.exists(new_input):
        print(f"❌ File input XML tidak ditemukan: \"{new_input}\"")
        # Tampilkan DEFAULT_INPUT saat ini (dari target script) agar user tahu
        target_check = DEFAULT_TARGET if len(sys.argv) == 2 else sys.argv[2]
        if not os.path.exists(target_check):
            # Jika target juga tidak ada, coba cari di scripts/
            alt = os.path.join("scripts", target_check)
            if os.path.exists(alt):
                target_check = alt
        if os.path.exists(target_check):
            try:
                with open(target_check, 'r', encoding='utf-8') as f:
                    cur = get_current_default(f.read())
                if cur:
                    print(f"   DEFAULT_INPUT saat ini: \"{cur}\"")
            except Exception:
                pass
        print("   Penggantian dibatalkan.")
        sys.exit(1)

    # Tentukan target script
    if len(sys.argv) == 3:
        target_file = sys.argv[2]
        # Jika tidak ditemukan, coba tambahkan prefix "scripts/"
        if not os.path.exists(target_file):
            alt_path = os.path.join("scripts", target_file)
            if os.path.exists(alt_path):
                target_file = alt_path
            else:
                print(f"❌ File target tidak ditemukan: {target_file}")
                print(f"   (juga mencoba: {alt_path})")
                sys.exit(1)
    else:
        target_file = DEFAULT_TARGET
        if not os.path.exists(target_file):
            print(f"❌ Default target tidak ditemukan: {target_file}")
            sys.exit(1)

    # Baca isi file target
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Gagal membaca {target_file}: {e}")
        sys.exit(1)

    old_default = get_current_default(content)

    # Regex: cari baris DEFAULT_INPUT = "..." (boleh ada spasi, tab, dan komentar setelahnya)
    pattern = r'^(\s*DEFAULT_INPUT\s*=\s*)"[^"]*"(\s*#.*)?$'

    def replace_match(m):
        prefix = m.group(1)
        suffix = m.group(2) if m.group(2) else ''
        return f'{prefix}"{new_input}"{suffix}'

    new_content, count = re.subn(pattern, replace_match, content, count=1, flags=re.MULTILINE)

    if count == 0:
        print("❌ Tidak ditemukan baris DEFAULT_INPUT = \"...\" di dalam file.")
        print("   Pastikan formatnya: DEFAULT_INPUT = \"path/file.xml\"")
        sys.exit(1)

    # Tulis kembali
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Berhasil mengubah DEFAULT_INPUT:")
        if old_default:
            print(f"   Sebelum : \"{old_default}\"")
        print(f"   Sesudah : \"{new_input}\"")
        print(f"   File    : {target_file}")
    except Exception as e:
        print(f"❌ Gagal menulis file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()