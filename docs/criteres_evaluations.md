# 📋 Cahier des Charges - Critères d'Évaluation

## 1. Critères d'Évaluation

### Répartition des points

| Critère | Pourcentage |
|---------|------------|
| Qualité du code (structure, POO, lisibilité, PEP 8, etc.) | 25% |
| Qualité du README et documentation | 20% |
| Fonctionnalité du projet | 25% |
| Originalité / complexité maîtrisée | 10% |
| Utilisation pertinente des outils vus en cours | 10% |
| Travail en équipe (Git) | 10% |

### Note individuelle

La note de chaque membre d'un même groupe pourra être légèrement modulée en fonction de sa participation réelle au projet.

**Distribution des points:**
- Chaque groupe dispose d'un nombre de points égal au nombre de membres du groupe, à répartir librement entre ses membres.
- La répartition devra être validée par l'ensemble du groupe.
- En cas de litige, l'enseignant se réserve le droit de modifier la répartition.

**Exemple pour un groupe de 4 personnes (4 points à répartir):**

*Participation égale:*
- Chaque membre reçoit 1 point supplémentaire

*Participation inégale:*
- P1: 40% → 1.6 point
- P2: 40% → 1.6 point
- P3: 10% → 0.4 point
- P4: 10% → 0.4 point

## 2. GitHub

### Gestion du dépôt

- Le projet peut être accessible publiquement ou privé. S'il est privé, pensez à le rendre public pour faciliter l'évaluation. **(Obligatoire)**

- Chaque personne doit contribuer au Git. Les contributions de chacun seront vérifiées. **(Obligatoire)**

- Lorsqu'une nouvelle feature est implémentée, créez une nouvelle branche. **(Conseillé)**

- Une fois la feature développée et stable (donc testée), mergez-la à la branche principale. **(Fortement conseillé)**

- La branche principale "main" doit toujours être fonctionnelle. **(Très conseillé)**

- Un fichier `requirements.txt` ou `environment.yml`. **(Obligatoire)**

- Seule la branche principale sera testée lors de l'évaluation. **(Important)**

## 3. README.md

Un soin particulier du fichier README sera attendu. C'est la page de garde de votre application. Elle doit être claire, détaillée et un peu catchy pour donner envie de tester votre travail.

**Exemple inspirant:** [Ultralytics](https://github.com/ultralytics/ultralytics)

### 3.1 Résumé du projet

- Un schéma général du projet **(Obligatoire)**
- Un UML pour les features principales. [Exemple](https://github.com/ultralytics/ultralytics) **(Bonus)**
- Un résumé général présentant les différentes features **(Obligatoire)**

### 3.2 Tutoriel d'installation

- Création d'un environnement virtuel (conda ou venv) **(Obligatoire)**
- Installation des packages avec le fichier `requirements` **(Obligatoire)**
- Code minimal pour tester si l'installation s'est bien passée **(Obligatoire)**
- Donner la ou les différentes distributions (versions Windows, Mac, Linux) sur lesquelles le projet a été installé avec succès **(Bonus)**

### 3.3 Fonctionnalités implémentées

Pour chaque feature implémentée:

- Un petit résumé expliquant les points clés **(Obligatoire)**
- Un exemple d'utilisation **(Obligatoire)**
  - Soit un code à copier/coller
  - Soit une ligne de commande avec un fichier mis dans un dossier `/exemples`
- Une ou plusieurs captures d'écran soignées avec une courte explication **(Bonus)**

### 3.4 Visualisations

- Au moins une visualisation pertinente **(Obligatoire)**

**Exemples:**
- Les performances d'un algorithme utilisé (temps d'exécution / précision / ablation...)
- L'analyse d'un joueur, de l'apprentissage d'un algorithme, etc.
- Une visualisation d'un clustering, d'une descente de gradient, etc.

### 3.5 Mise en forme générale

- La page doit être en **anglais** **(Obligatoire)**
- Utilisez les "Code blocks" de Markdown (bash pour les lignes de commandes, python pour les exemples de codes, LaTeX pour les équations, etc.) [Guide](https://guides.github.com/features/mastering-markdown/) **(Bonus)**
- Inspirez-vous de l'existant, soyez créatif mais surtout clair et "user friendly" **(Conseillé)**

## 4. Considérations pour le code

### Organisation et structure

- Organisez les fichiers comme vu dans le cours **(Obligatoire)**
- Utilisez au maximum la POO (Programmation Orientée Objet) **(Obligatoire)**

### Normes et conventions

- Respectez au maximum les recommandations PEP 8 **(Bonus)**
  - **Conseil:** Lisez tout le [PEP 8](https://www.python.org/dev/peps/pep-0008/) avant de commencer à coder
  - Que tout le groupe partage le même style de code **(Conseillé)**

### Nommage et documentation

- Le code (variables, fonctions, classes) doit être en **anglais** **(Bonus)**
- Les commentaires peuvent être en français ou en anglais **(Bonus)**
- Prenez du temps à bien nommer vos variables. Si ça vous paraît clair sur le moment, ça le sera moins dans une semaine ou pour un autre contributeur **(Fortement conseillé)**

## 5. Bonus

### Fonctionnalités supplémentaires

- Ajout d'une Licence (MIT / Apache / etc.) [Guide](https://choosealicense.com/)
- Ajout de test unitaires