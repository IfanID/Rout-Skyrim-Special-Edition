#!/usr/bin/env python3
"""
Ekstrak semua nilai dari tag <REC>...</REC> dari file XML dan simpan ke rec.txt
- Nilai duplikat hanya ditulis sekali (mempertahankan urutan kemunculan pertama)

Usage:
  python extract_rec.py                                        # Default paths
  python extract_rec.py input/custom.xml output/hasil.txt      # Custom paths
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import re
import sys
import os

# ============================================
# DEFAULT PATHS
# ============================================
DEFAULT_INPUT = "input/Skyrim_english_english.xml"
DEFAULT_OUTPUT = "output/rec.txt"

REMOVE_DUP = True

def extract_with_elementtree(xml_path: str) -> list[str]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    results = []
    seen = set()
    for rec in root.iter("REC"):
        if rec.text and rec.text.strip():
            val = rec.text.strip()
            if REMOVE_DUP:
                if val not in seen:
                    seen.add(val)
                    results.append(val)
            else:
                results.append(val)
    return results

def extract_with_regex(xml_path: str) -> list[str]:
    results = []
    seen = set()
    pattern = re.compile(r"<REC>\s*(.*?)\s*</REC>", re.DOTALL)
    with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            for m in pattern.finditer(line):
                val = m.group(1).strip()
                if val:
                    if REMOVE_DUP:
                        if val not in seen:
                            seen.add(val)
                            results.append(val)
                    else:
                        results.append(val)
    return results

def main():
    if len(sys.argv) == 1:
        input_xml = DEFAULT_INPUT
        output_txt = DEFAULT_OUTPUT
        print("ℹ️  Menggunakan path default:")
        print(f"   Input  : {input_xml}")
        print(f"   Output : {output_txt}")
        print()
    elif len(sys.argv) == 3:
        input_xml = sys.argv[1]
        output_txt = sys.argv[2]
    else:
        print("Usage:")
        print("  python extract_rec.py                                   # Default paths")
        print("  python extract_rec.py <input_xml> <output_rec_txt>      # Custom paths")
        sys.exit(1)
    
    output_dir = os.path.dirname(output_txt)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    if not Path(input_xml).exists():
        print(f"[ERROR] File '{input_xml}' tidak ditemukan.")
        sys.exit(1)

    try:
        recs = extract_with_elementtree(input_xml)
        method = "ElementTree"
    except ET.ParseError:
        print("[WARN] XML parse error, beralih ke regex.")
        recs = extract_with_regex(input_xml)
        method = "Regex"

    with open(output_txt, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(r + "\n")

    print(f"[OK] Metode: {method} | Output: {output_txt} | Jumlah: {len(recs)}")

if __name__ == "__main__":
    main()