cat > tl.sh << 'EOF'
#!/bin/zsh
echo "========================================"
echo "  SKYRIM STRING TRANSLATOR"
echo "  source.txt -> source_translated.txt"
echo "========================================"
echo
cd "$(dirname "$0")"
python scripts/translate.py
echo
echo "========================================"
echo "  TRANSLATE SELESAI"
echo "========================================"
echo -n "Tekan Enter untuk melanjutkan..."
read
EOF