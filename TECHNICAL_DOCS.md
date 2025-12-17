# Documentation Technique - IPTV to M3U Converter

## Architecture de l'Application

### Vue d'Ensemble

L'application est structurée en trois modules principaux :

1. **main.py** : Point d'entrée et interface graphique
2. **iptv_client.py** : Client pour communiquer avec les serveurs IPTV
3. **cache.py** : Système de cache pour les informations serveur
4. **config_manager.py** : Gestionnaire de configuration

### Flux de Données

```
Utilisateur → main.py (GUI) → iptv_client.py (API) → Serveur IPTV
                          ↓
                     cache.py (Cache)
                          ↓
                    config_manager.py (Config)
```

## Module main.py

### Classe MainWindow

La classe `MainWindow` est la fenêtre principale de l'application. Elle contient trois onglets :

1. **Single URL** : Pour gérer une seule URL
2. **Multi Server Info** : Pour gérer plusieurs URLs en même temps
3. **About** : Informations sur l'application

### Méthodes Principales

- `fetch_info()` : Récupère les informations du serveur
- `generate_m3u()` : Génère une playlist M3U pour TV
- `generate_radio()` : Génère une playlist M3U pour radios
- `generate_vod()` : Génère une playlist M3U pour VOD
- `test_channels()` : Teste l'accessibilité des chaînes
- `remove_failed()` : Supprime les chaînes qui n'ont pas passé le test
- `save_m3u()` : Sauvegarde la playlist

### Classe Worker

La classe `Worker` hérite de `QThread` et permet d'exécuter des tâches asynchrones sans bloquer l'interface graphique. Elle utilise `asyncio` pour exécuter les coroutines.

## Module iptv_client.py

### Classe IPTVClient

La classe `IPTVClient` est responsable de la communication avec les serveurs IPTV. Elle implémente les méthodes suivantes :

#### Méthodes de Parsing

- `parse_url()` : Parse l'URL pour extraire le host, le port, le username et le password
- `construct_base_url()` : Construit l'URL de base pour les requêtes

#### Méthodes de Requêtes

- `fetch()` : Effectue une requête HTTP asynchrone
- `get_server_info()` : Récupère les informations du serveur (avec cache)
- `generate_m3u()` : Génère une playlist M3U pour TV
- `generate_radio_m3u()` : Génère une playlist M3U pour radios
- `generate_vod_m3u()` : Génère une playlist M3U pour VOD
- `test_channels()` : Teste l'accessibilité des chaînes

#### Méthodes de Sauvegarde

- `save_m3u()` : Sauvegarde le contenu M3U dans un fichier

### Gestion du Cache

La classe `IPTVClient` utilise un cache global partagé entre toutes les instances. Le cache est géré par la classe `ServerCache` du module `cache.py`.

Le cache est activé par défaut avec une durée de vie de 300 secondes (5 minutes) et un maximum de 100 éléments.

### Limitation des Tests Simultanés

La méthode `test_channels()` limite le nombre de tests simultanés à 10 pour éviter de surcharger les serveurs. Cette limite est configurable via le fichier `config.ini`.

## Module cache.py

### Classe ServerCache

La classe `ServerCache` implémente un système de cache LRU (Least Recently Used) pour les informations serveur.

#### Attributs

- `max_age` : Durée de vie maximale d'une entrée en secondes
- `max_items` : Nombre maximum d'entrées dans le cache
- `cache` : Dictionnaire des entrées de cache
- `access_times` : Dictionnaire des temps d'accès pour LRU

#### Méthodes

- `get(key)` : Récupère une entrée du cache
- `set(key, value)` : Ajoute ou met à jour une entrée dans le cache
- `delete(key)` : Supprime une entrée du cache
- `clear()` : Vide complètement le cache
- `get_size()` : Retourne le nombre d'entrées dans le cache
- `get_info()` : Retourne des informations sur le cache

#### Classe CacheEntry

La classe `CacheEntry` représente une entrée dans le cache. Elle contient :

- `data` : Les données stockées
- `timestamp` : Le timestamp de création
- `ttl` : Time to live en secondes
- `is_expired` : Propriété pour vérifier si l'entrée est expirée

## Module config_manager.py

### Classe ConfigManager

La classe `ConfigManager` gère la configuration de l'application via un fichier `config.ini`.

#### Attributs

- `config_file` : Chemin vers le fichier de configuration
- `config` : Instance de `configparser.ConfigParser`

#### Méthodes

- `load()` : Charge la configuration depuis le fichier
- `save()` : Sauvegarde la configuration dans le fichier
- `get(section, key, default)` : Récupère une valeur de configuration
- `set(section, key, value)` : Définit une valeur de configuration
- `get_section(section)` : Récupère toutes les valeurs d'une section
- `get_all()` : Récupère toutes les configurations
- `reset_to_defaults()` : Réinitialise la configuration aux valeurs par défaut
- `delete(section, key)` : Supprime une valeur de configuration
- `delete_section(section)` : Supprime une section complète

#### Sections de Configuration

- `app` : Informations sur l'application (version, nom, auteur)
- `cache` : Paramètres du cache (enabled, max_age_seconds, max_items)
- `testing` : Paramètres des tests (max_concurrent_tests, timeout_seconds)
- `ui` : Paramètres de l'interface utilisateur (theme, font_size, show_password, window_width, window_height)
- `security` : Paramètres de sécurité (encrypt_passwords, password_mask)

### Instance Globale

Une instance globale `CONFIG` est créée pour faciliter l'accès à la configuration depuis n'importe où dans l'application :

```python
from config_manager import CONFIG

max_age = CONFIG.get('cache', 'max_age_seconds')
```

## Tests Unitaires

### Structure des Tests

Les tests unitaires sont organisés dans le répertoire `tests/` :

- `test_iptv_client.py` : Tests pour le module `iptv_client.py`
- `test_cache.py` : Tests pour le module `cache.py`
- `test_config_manager.py` : Tests pour le module `config_manager.py`

### Exécution des Tests

Pour exécuter les tests, utilisez la commande suivante :

```bash
cd tests
python -m unittest test_iptv_client.py test_cache.py test_config_manager.py -v
```

### Couverture des Tests

Les tests couvrent les fonctionnalités suivantes :

- **iptv_client.py** : Parsing d'URL, construction d'URL de base, requêtes HTTP, récupération d'informations serveur, génération de playlists, tests de chaînes
- **cache.py** : Ajout et récupération d'entrées, expiration, éviction LRU, nettoyage, suppression, informations
- **config_manager.py** : Chargement et sauvegarde, récupération et définition de valeurs, conversion de types, gestion des sections, réinitialisation

## Sécurité

### Masquage du Mot de Passe

Le mot de passe est masqué dans l'affichage des informations serveur. Il est remplacé par "••••••••" pour des raisons de sécurité.

### Gestion des Sessions

Les informations serveur sont gérées de manière plus sécurisée avec le système de cache. Les requêtes sont limitées pour éviter les abus.

### Limitation des Tests Simultanés

Le nombre de tests de chaînes simultanés est limité à 10 pour éviter de surcharger les serveurs et de causer des problèmes de performance.

## Performance

### Système de Cache

Le système de cache permet de réduire le nombre de requêtes vers les serveurs IPTV. Les informations sont mises en cache pendant 5 minutes et peuvent être réutilisées.

### Requêtes Asynchrones

Toutes les requêtes sont asynchrones grâce à `aiohttp` et `asyncio`. Cela permet d'exécuter plusieurs requêtes en parallèle sans bloquer l'interface graphique.

### Limitation des Tests

Les tests de chaînes sont limités à 10 simultanés pour éviter de surcharger les serveurs. Cette limite est configurable via le fichier `config.ini`.

## Architecture Asynchrone

### Boucle d'Événements

L'application utilise une boucle d'événements asyncio pour gérer les requêtes asynchrones :

```python
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(self.func(*self.args, **self.kwargs))
loop.close()
```

### Sessions HTTP

Les sessions HTTP sont gérées avec `aiohttp.ClientSession` pour réutiliser les connexions :

```python
async with aiohttp.ClientSession() as session:
    resp = await session.get(url)
```

### Sémaphores

Les sémaphores sont utilisés pour limiter le nombre de tâches simultanées :

```python
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TESTS)

async def limited_task(task):
    async with semaphore:
        return await task
```

## Conventions de Code

### Style de Code

L'application suit les conventions de style Python PEP 8 :

- Indentation de 4 espaces
- Lignes de code maximum de 79 caractères
- Noms de variables en snake_case
- Noms de classes en PascalCase
- Docstrings pour toutes les fonctions publiques

### Typage

L'application utilise le typage statique Python pour améliorer la lisibilité et la maintenabilité :

```python
from typing import Optional, Tuple, Dict, List, Any

def parse_url(self) -> Tuple[Optional[str], Optional[int], Optional[str], Optional[str]]:
    ...
```

### Gestion des Exceptions

Les exceptions sont gérées de manière appropriée avec des messages d'erreur clairs :

```python
try:
    result = await self.fetch(session, url)
except aiohttp.ClientError as e:
    raise Exception(f"HTTP request failed: {e}")
```

## Déploiement

### Installation

Pour installer l'application, suivez ces étapes :

1. Clonez le dépôt : `git clone https://github.com/ziadboughdir-byte/iptv-to-m3u.git`
2. Naviguez dans le répertoire : `cd iptv-to-m3u`
3. Installez les dépendances : `pip install -r requirements.txt`
4. Lancez l'application : `python main.py`

### Dépendances

Les dépendances sont listées dans le fichier `requirements.txt` :

```
aiohttp
PyQt6
```

### Fichiers de Configuration

Le fichier `config.ini` permet de personnaliser l'application. Il est créé automatiquement lors du premier lancement.

## Roadmap

### Fonctionnalités Futures

Les fonctionnalités suivantes sont planifiées pour les prochaines versions :

- Système de favoris pour sauvegarder les serveurs
- Import/export de configurations
- Génération M3U en batch
- Vérification des mises à jour automatiques
- Localisation multi-langue
- Chiffrement des mots de passe
- Prévisualisation graphique des chaînes

## Conclusion

L'application est bien structurée avec une architecture modulaire et asynchrone. Les améliorations de la version 1.1.0 ont renforcé la sécurité, la performance et la maintenabilité du code.
