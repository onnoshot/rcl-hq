#!/bin/bash
# Sesli Yazı Asistanı — Kurulum scripti

set -euo pipefail

echo ""
echo "🎙️  Sesli Yazı Asistanı — Kurulum"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# portaudio (sounddevice için gerekli)
if command -v brew &>/dev/null; then
    if ! brew list portaudio &>/dev/null 2>&1; then
        echo "→ portaudio yükleniyor (Homebrew)..."
        brew install portaudio
    else
        echo "✓ portaudio zaten yüklü"
    fi
else
    echo "⚠️  Homebrew bulunamadı — portaudio manuel kurulumu gerekebilir"
fi

echo "→ Python paketleri yükleniyor..."
pip3 install --quiet --upgrade sounddevice numpy SpeechRecognition pynput pyobjc-framework-Cocoa

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅  Kurulum tamamlandı!"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Başlatmak için:"
echo ""
echo "   python3 $SCRIPT_DIR/voice_to_chat.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  İlk çalıştırmada gerekli izinler:"
echo ""
echo "1. ERİŞİLEBİLİRLİK (global kısayol için şart):"
echo "   Sistem Ayarları → Gizlilik & Güvenlik → Erişilebilirlik"
echo "   → Terminal veya VS Code'u listeden etkinleştirin ✓"
echo ""
echo "2. MİKROFON:"
echo "   İlk ses kaydında macOS otomatik soracak, izin verin."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OPENAI_API_KEY eksikse ekleyin:"
echo ""
echo '   echo '"'"'export OPENAI_API_KEY="sk-..."'"'"' >> ~/.zshrc'
echo "   source ~/.zshrc"
echo ""
