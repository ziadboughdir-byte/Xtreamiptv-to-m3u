# IPTV to M3U Converter - Version 1.1.0

Une application Python avec interface graphique (PyQt6) pour récupérer les informations des serveurs IPTV Xtream Codes, générer des playlists M3U pour TV, radios et VOD (films), avec fonctionnalités de recherche, édition, test et nettoyage automatique.

## Nouvelles Fonctionnalités de la Version 1.1.0

### 🛡️ Sécurité Améliorée
- **Masquage du mot de passe** : Le mot de passe n'est plus affiché dans les informations serveur, il est remplacé par "••••••••"
- **Gestion des sessions** : Les informations serveur sont maintenant gérées de manière plus sécurisée

### ⚡ Performance Optimisée
- **Système de cache** : Les informations serveur sont maintenant mises en cache pendant 5 minutes pour éviter les requêtes redondantes
- **Tests limités** : Le nombre de tests de chaînes simultanés est limité à 10 pour éviter de surcharger les serveurs
- **Pagination** : Les grandes playlists sont maintenant gérées de manière plus efficace

### 📋 Configuration Centralisée
- **Fichier de configuration** : Un fichier `config.ini` permet de personnaliser les paramètres de l'application
- **Gestionnaire de configuration** : Le module `config_manager.py` facilite la gestion des paramètres

### 🧪 Tests Unitaires
- **Tests complets** : L'application est maintenant accompagnée de tests unitaires pour `iptv_client.py`, `cache.py` et `config_manager.py`
- **Qualité de code** : Les tests garantissent la stabilité et la fiabilité du code

## Fonctionnalités

- Interface graphique moderne avec thème sombre et onglets bien organisés
- Récupération des informations serveur incluant le nombre total de chaînes TV, radios et VOD
- Génération de playlists M3U pour TV en direct, radios (avec filtrage par mots-clés) et VOD/films
- Recherche et filtrage des chaînes/stations par nom
- Prévisualisation M3U éditable : suppression/ajout manuel de chaînes
- Test de l'accessibilité des chaînes et suppression automatique des échecs
- Requêtes asynchrones utilisant `aiohttp` et `asyncio`
- Support des endpoints `get.php` et `player_api.php`
- Gestion des URLs avec ou sans port explicite

## Installation

### Cloner le Dépôt

```bash
git clone https://github.com/ziadboughdir-byte/iptv-to-m3u.git
cd iptv-to-m3u
```

### Installer les Dépendances

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'Application

```bash
python main.py
```

### Utilisation de l'Interface

1. **Onglet "Single URL"** : Entrez l'URL, récupérez les informations, générez le M3U, recherchez/éditez/testez/sauvegardez
2. **Onglet "Multi Server Info"** : Collez plusieurs URLs (une par ligne), cliquez sur "Fetch All Server Infos" pour voir les résultats en lot

### Configuration

Vous pouvez personnaliser l'application en modifiant le fichier `config.ini` :

```ini
[cache]
enabled = True
max_age_seconds = 300
max_items = 100

[testing]
max_concurrent_tests = 10
timeout_seconds = 5

[ui]
theme = dark
font_size = 12
show_password = False
window_width = 1000
window_height = 700

[security]
encrypt_passwords = False
password_mask = ••••••••
```

## Tests

Pour exécuter les tests unitaires :

```bash
cd tests
python -m unittest test_iptv_client.py test_cache.py test_config_manager.py -v
```

## Exemples d'URLs

- `http://example.com:8080/player_api.php?username=USER&password=PASS`
- `http://example.com/get.php?username=USER&password=PASS&type=m3u_plus`

## Sortie

- Génère du contenu M3U dans la prévisualisation (éditable)
- Sauvegarde via une boîte de dialogue en tant que .m3u
- Informations serveur affichées dans l'interface

## Structure du Projet

```
Xtreamiptv-to-m3u/
├── main.py                    # Point d'entrée de l'application
├── iptv_client.py             # Client pour communiquer avec les serveurs IPTV
├── cache.py                   # Système de cache pour les informations serveur
├── config_manager.py          # Gestionnaire de configuration
├── config.ini                 # Fichier de configuration
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation
├── tests/                     # Tests unitaires
│   ├── test_iptv_client.py
│   ├── test_cache.py
│   └── test_config_manager.py
└── IMPROVEMENTS_ANALYSIS.md   # Analyse des améliorations
```

## Auteur

Développé par [ziadboughdir-byte](https://github.com/ziadboughdir-byte)

## Contribuer

Si vous souhaitez contribuer à ce projet, n'hésitez pas à forker le dépôt et à soumettre des pull requests. Assurez-vous que votre code suit la structure existante et testez-le soigneusement.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
