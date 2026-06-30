#!/bin/bash
cd "$(dirname "$0")"
echo "========================================"
echo "  SKYRIM STRING EXPORTER"
echo "  XML -> output/source.txt"
echo "========================================"
echo ""
python3 scripts/export.py
echo ""
echo "========================================"
echo "  EXPORT SELESAI"
echo "========================================"