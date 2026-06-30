#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "  SKYRIM STRING IMPORTER"
echo "  translated/source_translated.txt -> final/Skyrim_english_english.xml"
echo "========================================"
echo ""
python3 scripts/import.py
echo ""
echo "========================================"
echo "  IMPORT SELESAI"
echo "========================================"