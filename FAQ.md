# FAQ - Questions Fréquentes

## Installation et Configuration

### Comment installer l'application ?

Pour installer l'application, suivez ces étapes :

1. Clonez le dépôt : `git clone https://github.com/ziadboughdir-byte/iptv-to-m3u.git`
2. Naviguez dans le répertoire : `cd iptv-to-m3u`
3. Installez les dépendances : `pip install -r requirements.txt`
4. Lancez l'application : `python main.py`

### Quelles sont les dépendances nécessaires ?

L'application nécessite uniquement deux dépendances :
- `aiohttp` : Pour les requêtes HTTP asynchrones
- `PyQt6` : Pour l'interface graphique

Ces dépendances sont automatiquement installées via `pip install -r requirements.txt`.

### L'application fonctionne-t-elle sur tous les systèmes d'exploitation ?

Oui, l'application fonctionne sur Windows, macOS et Linux. Le module `asyncio` est configuré automatiquement pour Windows.

## Utilisation

### Comment utiliser l'application ?

L'application dispose de deux onglets principaux :

1. **Single URL** : Pour générer des playlists M3U à partir d'une seule URL
2. **Multi Server Info** : Pour récupérer les informations de plusieurs serveurs en même temps

Dans l'onglet "Single URL", vous pouvez :
- Entrer l'URL du serveur IPTV
- Récupérer les informations serveur
- Générer des playlists M3U pour TV, radios ou VOD
- Rechercher et filtrer les chaînes
- Tester l'accessibilité des chaînes
- Sauvegarder la playlist

### Comment générer une playlist M3U ?

1. Dans l'onglet "Single URL", entrez l'URL du serveur IPTV
2. Cliquez sur "Fetch Server Info" pour récupérer les informations
3. Cliquez sur le bouton approprié ("Generate TV M3U", "Generate Radio M3U" ou "Generate VOD M3U")
4. La playlist s'affiche dans la prévisualisation
5. Cliquez sur "Save M3U" pour sauvegarder le fichier

### Comment tester les chaînes ?

Après avoir généré une playlist, cliquez sur le bouton "Test Channels". L'application testera l'accessibilité de chaque chaîne et affichera les résultats (total, fonctionnelles, échouées).

### Comment supprimer les chaînes qui ne fonctionnent pas ?

Après avoir testé les chaînes, cliquez sur "Remove Failed Channels". L'application supprimera automatiquement toutes les chaînes qui n'ont pas passé le test.

### Comment filtrer les chaînes ?

Utilisez la barre de recherche "Search" pour filtrer les chaînes par nom. Tapez simplement une partie du nom de la chaîne et la liste sera filtrée en temps réel.

## Configuration

### Comment modifier la configuration de l'application ?

La configuration de l'application est stockée dans le fichier `config.ini`. Vous pouvez modifier ce fichier pour personnaliser :

- Les paramètres du cache (durée de vie, nombre maximum d'éléments)
- Les paramètres des tests (nombre de tests simultanés, timeout)
- Les paramètres de l'interface (thème, taille de police, dimensions de fenêtre)
- Les paramètres de sécurité (masquage du mot de passe)

### Quels sont les paramètres de cache ?

Le cache est activé par défaut avec les paramètres suivants :
- **Durée de vie** : 300 secondes (5 minutes)
- **Nombre maximum d'éléments** : 100

Cela signifie que les informations serveur sont mises en cache pendant 5 minutes et que le cache peut contenir jusqu'à 100 entrées différentes.

### Comment désactiver le cache ?

Pour désactiver le cache, modifiez le fichier `config.ini` :

```ini
[cache]
enabled = False
```

### Comment augmenter le nombre de tests simultanés ?

Pour augmenter le nombre de tests de chaînes simultanés, modifiez le fichier `config.ini` :

```ini
[testing]
max_concurrent_tests = 20
```

**Attention** : Augmenter ce nombre peut surcharger les serveurs et causer des problèmes de performance.

## Sécurité

### Pourquoi le mot de passe est-il masqué ?

Le mot de passe est masqué pour des raisons de sécurité. Il n'est plus affiché dans les informations serveur, mais remplacé par "••••••••".

### Le mot de passe est-il stocké en clair ?

Oui, actuellement le mot de passe est transmis en clair dans les requêtes HTTP. Pour une meilleure sécurité, utilisez des connexions HTTPS lorsque c'est possible.

### Existe-t-il un système de chiffrement des mots de passe ?

Non, il n'y a pas de système de chiffrement des mots de passe pour le moment. C'est une amélioration future planifiée.

## Problèmes et Dépannage

### L'application ne démarre pas, que faire ?

Vérifiez que vous avez installé toutes les dépendances :

```bash
pip install -r requirements.txt
```

Si le problème persiste, vérifiez que vous utilisez une version récente de Python (3.8 ou supérieure).

### Les tests de chaînes échouent, pourquoi ?

Les tests peuvent échouer pour plusieurs raisons :
- Le serveur est surchargé ou lent
- La connexion internet est instable
- Le nombre de tests simultanés est trop élevé

Essayez de réduire le nombre de tests simultanés dans `config.ini`.

### L'application est lente, comment l'accélérer ?

Activez le cache dans `config.ini` :

```ini
[cache]
enabled = True
```

Cela évitera de récupérer les informations serveur à chaque fois.

### Les chaînes ne s'affichent pas correctement, que faire ?

Vérifiez que l'URL du serveur est correcte et que le serveur est accessible. Si le problème persiste, essayez de vider le cache :

```python
from cache import ServerCache
ServerCache().clear()
```

## Fonctionnalités Avancées

### Comment générer des playlists pour plusieurs serveurs ?

Utilisez l'onglet "Multi Server Info" :

1. Collez plusieurs URLs (une par ligne) dans la zone de texte
2. Cliquez sur "Fetch All Server Infos"
3. Les informations de tous les serveurs seront affichées

### Existe-t-il un mode batch pour générer plusieurs playlists ?

Pas encore. Cette fonctionnalité est planifiée pour une future version.

### Puis-je importer/exporter des configurations ?

Pas encore. Cette fonctionnalité est planifiée pour une future version.

## Tests

### Comment exécuter les tests unitaires ?

Pour exécuter les tests unitaires, naviguez dans le répertoire `tests` et exécutez :

```bash
cd tests
python -m unittest test_iptv_client.py test_cache.py test_config_manager.py -v
```

### Quels modules sont testés ?

Les tests couvrent les modules suivants :
- `iptv_client.py` : Le client pour communiquer avec les serveurs IPTV
- `cache.py` : Le système de cache
- `config_manager.py` : Le gestionnaire de configuration

### Tous les tests passent-ils ?

Oui, tous les tests sont configurés pour passer. Si un test échoue, cela indique un problème dans le code qui doit être corrigé.

## Licence

### Sous quelle licence est distribuée l'application ?

L'application est distribuée sous la licence MIT, une licence libre et permissive.

### Puis-je utiliser l'application commercialement ?

Oui, vous pouvez utiliser l'application commercialement. Consultez le fichier LICENSE pour plus de détails.

## Support

### Où puis-je poser des questions ?

Vous pouvez créer une issue sur GitHub : https://github.com/ziadboughdir-byte/iptv-to-m3u/issues

### Puis-je contribuer au projet ?

Oui ! Consultez le fichier CONTRIBUTING.md pour savoir comment contribuer.

### Existe-t-il une documentation plus détaillée ?

Consultez le fichier README.md pour la documentation complète de l'application.

## Versions

### Quelle est la dernière version ?

La dernière version est la 1.1.0, publiée le 2025-01-16.

### Quelles sont les nouvelles fonctionnalités de la version 1.1.0 ?

La version 1.1.0 apporte les améliorations suivantes :
- Masquage du mot de passe pour la sécurité
- Système de cache pour les informations serveur
- Limitation des tests de chaînes simultanés
- Configuration centralisée
- Tests unitaires complets

Consultez le fichier CHANGELOG.md pour plus de détails.

## Remerciements

Merci d'utiliser IPTV to M3U Converter ! Votre feedback et vos contributions sont les bienvenus.
