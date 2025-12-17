#!/bin/bash
# Script de test pour l'application

echo "=== IPTV to M3U Converter - Tests ==="
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

echo "✅ Python3 détecté"
echo ""

# Exécuter les tests
if [ -d "tests" ]; then
    echo "=== Exécution des tests unitaires ==="
    cd tests
    python3 -m unittest test_iptv_client.py test_cache.py test_config_manager.py -v
    cd ..
    echo ""
else
    echo "⚠️  Aucun test disponible"
fi

echo "=== Vérification des fichiers ==="

echo ""
echo "Fichiers principaux:"
ls -lh main.py iptv_client.py cache.py config_manager.py

echo ""
echo "Documentation:"
ls -lh README.md CHANGELOG.md CONTRIBUTING.md FAQ.md TECHNICAL_DOCS.md

echo ""
echo "Configuration:"
ls -lh config.ini config_manager.py

echo ""
echo "Tests:"
ls -lh tests/

echo ""
echo "✅ Vérification terminée"
