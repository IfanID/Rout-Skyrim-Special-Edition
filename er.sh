cat > er.sh << 'EOF'
#!/bin/zsh
echo "========================================"
echo "  SKYRIM REC EXTRACTOR"
echo "  XML -> rec.txt"
echo "========================================"
echo
cd "$(dirname "$0")"
python scripts/extract_rec.py
echo
echo "========================================"
echo "  EXTRACT REC SELESAI"
echo "========================================"
echo -n "Tekan Enter untuk melanjutkan..."
read
EOF