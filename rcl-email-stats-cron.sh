#!/bin/zsh
# RCL e-posta istatistik otomasyonu: Brevo'dan oranları çek → ANA KAYNAK'a yaz → publish() ile canlıya git push
# LaunchAgent com.rcl.email-stats tarafından çağrılır.
# Not: yayınlama (write_block + publish) artık rcl-email-stats.py içinde rcl_config.py üzerinden yapılıyor;
# eski yerel /Users/onnoshot/Downloads/rcl-dashboard + vercel deploy yolu kaldırıldı (dizin artık mevcut değildi).
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
ROOT=/Users/onnoshot/Downloads/Agentlar

cd "$ROOT" || exit 1
"$PY" rcl-email-stats.py
