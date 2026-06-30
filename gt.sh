#!/bin/bash
cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "Usage: ./gt.sh input/filenya.xml [target_script]"
    echo "Contoh:"
    echo "  ./gt.sh Dialog.xml"
    echo "  ./gt.sh input/Quest.xml"
    exit 1
fi

echo "========================================"
echo "  GANTI DEFAULT_INPUT"
echo "========================================"
echo ""

if [ -z "$2" ]; then
    echo "Mengganti DEFAULT_INPUT di scripts/export.py menjadi \"$1\""
    echo ""
    python3 scripts/ganti.py "$1"
else
    echo "Mengganti DEFAULT_INPUT di $2 menjadi \"$1\""
    echo ""
    python3 scripts/ganti.py "$1" "$2"
fi
echo ""