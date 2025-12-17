# Changelog - IPTV to M3U Converter

## Version 1.1.0 - 2025-01-16

### 🛡️ Sécurité
- **CRITIQUE** : Masquage du mot de passe dans l'affichage des informations serveur
- Ajout d'un système de gestion des sessions plus sécurisé

### ⚡ Performance
- **CRITIQUE** : Implémentation d'un système de cache pour les informations serveur (5 minutes de durée de vie)
- **CRITIQUE** : Limitation du nombre de tests de chaînes simultanés à 10 pour éviter la surcharge
- Optimisation des requêtes asynchrones avec semaphore

### 📋 Architecture
- **CRITIQUE** : Création d'un fichier de configuration centralisé (`config.ini`)
- **CRITIQUE** : Implémentation d'un gestionnaire de configuration (`config_manager.py`)
- Refactorisation du code pour utiliser la configuration centralisée

### 🧪 Tests
- **CRITIQUE** : Ajout de tests unitaires complets pour `iptv_client.py`
- **CRITIQUE** : Ajout de tests unitaires complets pour `cache.py`
- **CRITIQUE** : Ajout de tests unitaires complets pour `config_manager.py`

### 📝 Documentation
- **CRITIQUE** : Mise à jour du README avec les nouvelles fonctionnalités
- Création d'un fichier CHANGELOG.md
- Ajout d'un fichier IMPROVEMENTS_ANALYSIS.md

### 🔧 Améliorations de Code
- Refactorisation de `iptv_client.py` pour utiliser le cache
- Refactorisation de `main.py` pour utiliser la configuration
- Ajout de docstrings détaillées
- Amélioration de la gestion des exceptions

### 🎨 Interface Utilisateur
- Utilisation des dimensions de fenêtre depuis la configuration
- Amélioration des feedbacks visuels

## Version 1.0.0 - 2024-12-15

### Fonctionnalités Initiales
- Interface graphique PyQt6 avec thème sombre
- Récupération des informations serveur IPTV
- Génération de playlists M3U pour TV, radios et VOD
- Recherche et filtrage des chaînes
- Test de l'accessibilité des chaînes
- Édition manuelle des playlists
- Sauvegarde des playlists en fichiers .m3u
- Support des endpoints `get.php` et `player_api.php`
- Requêtes asynchrones avec `aiohttp` et `asyncio`
