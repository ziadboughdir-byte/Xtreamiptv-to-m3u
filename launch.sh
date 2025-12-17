#!/bin/bash
# Script de lancement de l'application

echo "=== IPTV to M3U Converter ==="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Erreur: Python3 n'est pas installé"
    exit 1
fi

# Vérifier les dépendances
if [ ! -f "requirements.txt" ]; then
    echo "Erreur: requirements.txt introuvable"
    exit 1
fi

# Installer les dépendances si nécessaires
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "📦 Installation des dépendances..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "✅ Dépendances vérifiées"
echo ""

# Lancer l'application
echo "🚀 Lancement de l'application..."
echo ""
python3 main.py
