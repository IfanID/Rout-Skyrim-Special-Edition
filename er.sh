#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "  SKYRIM REC EXTRACTOR"
echo "  XML -> output/rec.txt"
echo "========================================"
echo ""
python3 scripts/extract_rec.py
echo ""
echo "========================================"
echo "  EXTRACT REC SELESAI"
echo "========================================"