cat > ex.sh << 'EOF'
#!/bin/zsh
echo "========================================"
echo "  SKYRIM STRING EXPORTER"
echo "  XML -> source.txt"
echo "========================================"
echo
cd "$(dirname "$0")"
python scripts/export.py
echo
echo "========================================"
echo "  EXPORT SELESAI"
echo "========================================"
echo -n "Tekan Enter untuk melanjutkan..."
read
EOF