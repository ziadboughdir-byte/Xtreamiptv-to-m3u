# Guide de Contribution

Merci de contribuer à IPTV to M3U Converter ! Ce guide vous aidera à comprendre comment contribuer efficacement au projet.

## Présentation du Projet

IPTV to M3U Converter est une application Python avec interface graphique PyQt6 qui permet de convertir les serveurs IPTV Xtream Codes en playlists M3U. Le projet est conçu pour être simple, performant et sécurisé.

## Comment Contribuer

### 1. Forker le Dépôt

Commencez par forker le dépôt sur GitHub :

```bash
git clone https://github.com/ziadboughdir-byte/iptv-to-m3u.git
cd iptv-to-m3u
git remote add upstream https://github.com/ziadboughdir-byte/iptv-to-m3u.git
```

### 2. Créer une Branche

Créez une branche pour votre fonctionnalité ou correction :

```bash
git checkout -b feature/ma-fonctionnalite
```

### 3. Installer les Dépendances

Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

### 4. Développer

Avant de commencer à coder, assurez-vous de :

- Lire la documentation existante
- Comprendre l'architecture du projet
- Vérifier qu'il n'existe pas déjà une issue ou pull request similaire

### 5. Tests

Toutes les contributions doivent inclure des tests unitaires. Pour exécuter les tests :

```bash
cd tests
python -m unittest test_iptv_client.py test_cache.py test_config_manager.py -v
```

Assurez-vous que tous les tests passent avant de soumettre votre pull request.

### 6. Code Style

Le projet suit les conventions de style Python PEP 8. Assurez-vous que votre code respecte ces conventions :

- Utilisez 4 espaces pour l'indentation
- Lignes de code maximum de 79 caractères
- Noms de variables en snake_case
- Noms de classes en PascalCase
- Ajoutez des docstrings pour toutes les fonctions publiques

### 7. Commit

Commitez vos changements avec des messages clairs et descriptifs :

```bash
git commit -m "feat: Ajouter le système de cache pour les informations serveur"
```

### 8. Push

Poussez vos changements sur votre branche :

```bash
git push origin feature/ma-fonctionnalite
```

### 9. Créer un Pull Request

Créez un pull request sur GitHub avec :

- Un titre descriptif
- Une description détaillée des changements
- Les tests associés
- Les raisons de la modification

## Types de Contributions

### Bug Fixes

Si vous trouvez un bug, créez une issue décrivant le problème, puis soumettez un pull request avec la correction.

### Nouvelles Fonctionnalités

Si vous souhaitez ajouter une nouvelle fonctionnalité, créez d'abord une issue pour discuter de l'idée, puis soumettez un pull request.

### Améliorations de Performance

Si vous améliorez la performance du code, assurez-vous de fournir des benchmarks ou des justifications.

### Documentation

Toute amélioration de la documentation est la bienvenue (README, docstrings, commentaires).

### Tests

Ajouter des tests pour le code existant est très apprécié.

## Code de Conduite

Ce projet suit le [Code de Conduite de la Communauté Open Source](https://www.contributor-covenant.org/). En participant, vous vous engagez à respecter ce code.

## Questions Fréquentes

### Puis-je contribuer si je suis débutant ?

Oui ! Tous les niveaux de compétence sont les bienvenus. Commencez par les issues marquées "good first issue".

### Combien de temps faut-il pour qu'un pull request soit revu ?

Cela dépend de la complexité des changements. Les pull requests simples sont généralement revues en quelques jours.

### Que faire si mon pull request est refusé ?

Ne vous découragez pas ! Les rejets sont souvent accompagnés de feedbacks constructifs. Utilisez-les pour améliorer votre code.

### Puis-je demander de l'aide ?

Oui ! N'hésitez pas à créer une issue pour demander de l'aide ou poser des questions.

## Licence

En contribuant à ce projet, vous acceptez que votre code soit distribué sous la licence MIT.

## Merci !

Votre contribution est précieuse et aide à améliorer l'application pour tous les utilisateurs. Merci de prendre le temps de contribuer !
