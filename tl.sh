#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "  SKYRIM STRING TRANSLATOR"
echo "  output/source.txt -> translated/source_translated.txt"
echo "========================================"
echo ""
python3 scripts/translate.py
echo ""
echo "========================================"
echo "  TRANSLATE SELESAI"
echo "========================================"