#!/usr/bin/env python3
"""
Skyrim XML Translator Pipeline — Import Script
Mengimpor hasil terjemahan dari source_translated.txt kembali ke XML berdasarkan sID.

Usage:
  python import.py                                                          # Default paths
  python import.py input/input.xml output/translated.txt output/output.xml output/report.txt  # Custom
"""

import sys
import re
import os

DEFAULT_INPUT_XML = "input/Skyrim_english_english.xml"
DEFAULT_SOURCE_TXT = "translated/source_translated.txt"
DEFAULT_OUTPUT_XML = "final/Skyrim_english_english.xml"
DEFAULT_REPORT_TXT = "output/laporan.txt"

def xml_escape(text):
    if text.startswith('<![CDATA[') and text.endswith(']]>'):
        return text
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def xml_unescape(text):
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    text = text.replace('&amp;', '&')
    return text

def parse_source_txt(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    parts = re.split(r'(?=^sID=")', content, flags=re.MULTILINE)
    translations = {}
    seen = set()
    duplicates = []
    duplicate_set = set()
    total_entries = 0
    for part in parts:
        part = part.strip()
        if not part: continue
        sid_match = re.search(r'sID="([^"]*)"', part)
        dest_match = re.search(r'<Dest\b[^>]*>(.*?)</Dest>', part, re.DOTALL)
        if not sid_match or not dest_match: continue
        sid = sid_match.group(1)
        dest = dest_match.group(1).strip()
        total_entries += 1
        if sid in seen and sid not in duplicate_set:
            duplicate_set.add(sid)
            duplicates.append(sid)
        seen.add(sid)
        translations[sid] = dest
    return translations, duplicates, total_entries

def main():
    if len(sys.argv) == 1:
        input_xml = DEFAULT_INPUT_XML
        source_txt = DEFAULT_SOURCE_TXT
        output_xml = DEFAULT_OUTPUT_XML
        report_txt = DEFAULT_REPORT_TXT
        print("ℹ️  Menggunakan path default:")
        print(f"   Input XML  : {input_xml}")
        print(f"   Source TXT : {source_txt}")
        print(f"   Output XML : {output_xml}")
        print(f"   Report TXT : {report_txt}")
        print()
    elif len(sys.argv) == 5:
        input_xml, source_txt, output_xml, report_txt = sys.argv[1:5]
    else:
        print("Usage: python import.py [optional custom paths]")
        sys.exit(1)

    for f in [output_xml, report_txt]:
        d = os.path.dirname(f)
        if d: os.makedirs(d, exist_ok=True)

    if not os.path.exists(source_txt):
        print(f"❌ {source_txt} tidak ditemukan. Jalankan tl.bat dulu.")
        sys.exit(1)
    if not os.path.exists(input_xml):
        print(f"❌ {input_xml} tidak ditemukan. Letakkan di folder input/.")
        sys.exit(1)

    translations, duplicates, total_entries = parse_source_txt(source_txt)
    print(f"✓ Loaded {total_entries:,} entries dari {source_txt}")

    with open(input_xml, 'r', encoding='utf-8-sig') as f:
        xml_content = f.read()

    total_nodes = 0
    updated = 0
    not_in_source = []
    sids_in_xml = set()

    def process_string_block(match):
        nonlocal total_nodes, updated
        full_block = match.group(0)
        total_nodes += 1
        sid_match = re.search(r'sID="([^"]*)"', full_block)
        if not sid_match: return full_block
        sid = sid_match.group(1)
        sids_in_xml.add(sid)
        if sid not in translations:
            src_m = re.search(r'<Source\b[^>]*>(.*?)</Source>', full_block, re.DOTALL)
            source_text = xml_unescape(src_m.group(1).strip()) if src_m else ''
            not_in_source.append((sid, source_text))
            return full_block
        new_dest = translations[sid]
        escaped_dest = xml_escape(new_dest)
        new_block = re.sub(
            r'(<Dest\b[^>]*>)(.*?)(</Dest>)',
            lambda m: m.group(1) + escaped_dest + m.group(3),
            full_block, count=1, flags=re.DOTALL
        )
        updated += 1
        return new_block

    new_xml = re.sub(r'<String\b[^>]*>.*?</String>', process_string_block, xml_content, flags=re.DOTALL)
    not_in_xml = [(sid, dest) for sid, dest in translations.items() if sid not in sids_in_xml]

    with open(output_xml, 'w', encoding='utf-8') as f:
        f.write(new_xml)
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n  LAPORAN IMPORT\n" + "="*60 + "\n\n")
        f.write(f"XML input : {os.path.basename(input_xml)}\n")
        f.write(f"Terjemahan: {os.path.basename(source_txt)}\n")
        f.write(f"XML output: {os.path.basename(output_xml)}\n\n")
        if not_in_source:
            f.write("=== sID Tidak Ditemukan di Terjemahan ===\n\n")
            for sid, src in not_in_source:
                f.write(f'sID="{sid}"\nSource: {src}\n\n')
        if not_in_xml:
            f.write("=== sID Tidak Ditemukan di XML ===\n\n")
            for sid, dst in not_in_xml:
                f.write(f'sID="{sid}"\nDest: {dst}\n\n')
        if duplicates:
            f.write("=== Duplikat sID ===\n\n")
            for sid in duplicates:
                f.write(f'sID="{sid}" muncul > 1 kali\n\n')
        f.write("="*60 + "\n  RINGKASAN\n" + "="*60 + "\n\n")
        f.write(f"Total node XML       : {total_nodes}\n")
        f.write(f"Total entri terjemahan: {total_entries}\n")
        f.write(f"Berhasil update      : {updated}\n")
        f.write(f"Tidak di terjemahan  : {len(not_in_source)}\n")
        f.write(f"Tidak di XML         : {len(not_in_xml)}\n")
        f.write(f"Duplikat sID         : {len(duplicates)}\n")

    print(f"✓ XML output: {output_xml}")
    print(f"✓ Laporan   : {report_txt}")
    print(f"  Updated {updated}/{total_nodes} nodes.")
    if not_in_source or not_in_xml or duplicates:
        print(f"  ⚠️  Lihat laporan untuk detail.")

if __name__ == '__main__':
    main()