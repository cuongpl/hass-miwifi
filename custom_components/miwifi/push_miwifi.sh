#!/bin/bash

echo "🛠 Copiando integración MiWiFi al repositorio..."
cp -r /config/custom_components/miwifi/* ~/hass-miwifi/custom_components/miwifi/

cd ~/hass-miwifi || exit

echo "📦 Añadiendo cambios..."
git add custom_components/miwifi

echo "📝 Escribe el mensaje del commit:"
read -r msg
git commit -m "$msg"

echo "🚀 Subiendo a GitHub..."
git push origin main

echo "✅ ¡Integración actualizada en GitHub correctamente!"
