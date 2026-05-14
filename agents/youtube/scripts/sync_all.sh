#!/bin/bash
# Tüm verileri güncelle — YouTube + Shopify
# Çalıştır: bash agents/youtube/scripts/sync_all.sh

SCRIPT_DIR="$(dirname "$0")"

echo "=== Retrocameraland Veri Senkronizasyonu ==="
echo ""

bash "${SCRIPT_DIR}/fetch_youtube.sh"
echo ""
bash "${SCRIPT_DIR}/fetch_shopify.sh"

echo ""
echo "=== Senkronizasyon tamamlandı ==="
echo "Veriler: agents/youtube/data/imports/"
