cat > im.sh << 'EOF'
#!/bin/zsh
echo "========================================"
echo "  SKYRIM STRING IMPORTER"
echo "  source_translated.txt -> XML"
echo "========================================"
echo
cd "$(dirname "$0")"
python scripts/import.py
echo
echo "========================================"
echo "  IMPORT SELESAI"
echo "========================================"
echo -n "Tekan Enter untuk melanjutkan..."
read
EOF