# 📖 User Stories - Loup-Garou Multi-Agents LLM

---

## 🔧 EPIC 1️⃣ : Architecture & Infrastructure

### US-1.1 | Initialiser la structure du projet
**Epic:** Architecture & Infrastructure  
**Points:** 3  
**Priorité:** 🔴 Critique  
**Dépendances:** Aucune

**Description:**  
En tant que développeur, je veux initialiser un projet Python avec une structure claire et modulaire pour que le code soit organisé et maintenable.

**Critères d'acceptation:**
- [ ] Structure des dossiers créée (ai/, game/, gui/, rl/, data/)
- [ ] Fichier `__init__.py` dans chaque module
- [ ] Fichier `.gitignore` approprié
- [ ] `requirements.txt` initialisé
- [ ] Respecte PEP 8

**Tâches:**
- Créer l'arborescence des dossiers
- Initialiser les fichiers Python
- Configurer les outils de linting (flake8, black)
- Mettre en place un virtual environment

**Notes:** Fondation pour tout le reste du projet

---

### US-1.2 | Configurer Ollama et la connexion LLM
**Epic:** Architecture & Infrastructure  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-1.1

**Description:**  
En tant que développeur, je veux configurer la connexion à Ollama pour pouvoir utiliser les modèles LLM localement.

**Critères d'acceptation:**
- [ ] Client Ollama créé et testé
- [ ] Gestion des erreurs de connexion
- [ ] Configuration externalisée (config.py ou .env)
- [ ] Support de plusieurs modèles
- [ ] Tests unitaires pour la connexion

**Tâches:**
- Implémenter la classe OllamaClient
- Ajouter gestion des timeouts
- Créer des méthodes de test
- Documenter la configuration

**Notes:** Crucial pour les agents LLM

---

### US-1.3 | Mettre en place le système de logging
**Epic:** Architecture & Infrastructure  
**Points:** 4  
**Priorité:** 🟠 Haute  
**Dépendances:** US-1.1

**Description:**  
En tant que développeur, je veux configurer un système de logging centralisé pour tracer les événements du système.

**Critères d'acceptation:**
- [ ] Logger configurable par niveau (DEBUG, INFO, WARNING, ERROR)
- [ ] Logs écrits dans des fichiers
- [ ] Format standardisé des logs
- [ ] Rotation des fichiers de log
- [ ] Console et fichier simultanément

**Tâches:**
- Configurer Python logging
- Créer un gestionnaire de logs
- Mettre en place la rotation
- Ajouter des tests

**Notes:** Essentiel pour le debugging et l'analyse

---

### US-1.4 | Implémenter la communication WebSocket
**Epic:** Architecture & Infrastructure  
**Points:** 6  
**Priorité:** 🔴 Critique  
**Dépendances:** US-1.1

**Description:**  
En tant qu'architecte, je veux mettre en place un serveur WebSocket pour que les agents et l'interface puissent communiquer en temps réel.

**Critères d'acceptation:**
- [ ] Serveur WebSocket créé avec asyncio/FastAPI
- [ ] Gestion des connexions multiples
- [ ] Messages JSON sérialisés
- [ ] Gestion des déconnexions
- [ ] Tests de charge basiques

**Tâches:**
- Configurer FastAPI + WebSocket
- Implémenter les handlers de messages
- Gérer les reconexions
- Créer des tests

**Notes:** Infrastructure centrale du projet

---

### US-1.5 | Créer le système de configuration global
**Epic:** Architecture & Infrastructure  
**Points:** 4  
**Priorité:** 🟠 Haute  
**Dépendances:** US-1.1, US-1.3

**Description:**  
En tant que développeur, je veux centraliser toute la configuration du projet pour que les paramètres soient faciles à modifier.

**Critères d'acceptation:**
- [ ] Fichier config.py ou config.yaml
- [ ] Variables d'environnement supportées
- [ ] Validation des configurations
- [ ] Valeurs par défaut cohérentes
- [ ] Documentation des paramètres

**Tâches:**
- Créer la classe Configuration
- Valider les paramètres
- Ajouter des valeurs par défaut
- Documenter chaque paramètre

**Notes:** Utile pour l'Epic 6 (Paramètres Expérimentaux)

---

## 🤖 EPIC 2️⃣ : Système Multi-Agents

### US-2.1 | Créer la classe Agent de base
**Epic:** Système Multi-Agents  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-1.1, US-1.2, US-1.3

**Description:**  
En tant qu'architecte, je veux créer une classe Agent abstraite pour que tous les agents héritent d'une structure commune.

**Critères d'acceptation:**
- [ ] Classe Agent avec ID unique
- [ ] Propriétés de base (rôle, alignement, personnalité)
- [ ] Méthodes abstraites pour les actions
- [ ] Système d'état de l'agent
- [ ] Tests unitaires

**Tâches:**
- Implémenter la classe Agent
- Définir l'interface des agents
- Ajouter les propriétés
- Créer les tests

**Notes:** Base pour tous les rôles

---

### US-2.2 | Implémenter le système de mémoire courte
**Epic:** Système Multi-Agents  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-2.1

**Description:**  
En tant que développeur d'agents, je veux implémenter une mémoire courte pour que les agents se souviennent des messages récents.

**Critères d'acceptation:**
- [ ] Stockage des messages récents (derniers N messages)
- [ ] FIFO avec taille maximale configurable
- [ ] Accès rapide aux messages
- [ ] Sérialisation pour les logs
- [ ] Tests unitaires

**Tâches:**
- Créer une classe ShortTermMemory
- Implémenter le stockage ringBuffer
- Ajouter la sérialisation
- Tests

**Notes:** Essentiel pour la prise de décision

---

### US-2.3 | Implémenter le système de mémoire longue
**Epic:** Système Multi-Agents  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-2.1

**Description:**  
En tant que développeur, je veux implémenter une mémoire longue pour que les agents retiennent les événements clés.

**Critères d'acceptation:**
- [ ] Stockage des événements importants
- [ ] Métadonnées des événements (timestamp, type)
- [ ] Recherche efficace des événements
- [ ] Limite de taille configurable
- [ ] Tests unitaires

**Tâches:**
- Créer une classe LongTermMemory
- Implémenter l'indexation
- Ajouter la recherche
- Tests

**Notes:** Pour la continuité entre parties

---

### US-2.4 | Implémenter le système de mémoire sociale
**Epic:** Système Multi-Agents  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** US-2.1

**Description:**  
En tant que développeur, je veux implémenter une mémoire sociale pour que les agents trackent la confiance et le comportement des autres.

**Critères d'acceptation:**
- [ ] Stockage des relations (confiance, suspicion)
- [ ] Métriques de confiance par agent
- [ ] Historique des changements de confiance
- [ ] Détection d'incohérences
- [ ] Tests unitaires

**Tâches:**
- Créer SocialMemory
- Implémenter le scoring de confiance
- Tracker les changements
- Détecter les incohérences

**Notes:** Crucial pour les interactions d'agents

---

### US-2.5 | Créer le système de personnalités
**Epic:** Système Multi-Agents  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** US-2.1

**Description:**  
En tant que chercheur, je veux créer un système de personnalités pour que chaque agent ait un comportement distinct.

**Critères d'acceptation:**
- [ ] Modèle de personnalité (style, paranoia, mensonge, coopération)
- [ ] Personnalités prédéfinies
- [ ] Influence sur les décisions
- [ ] Sérialisation/désérialisation
- [ ] Tests et exemples

**Tâches:**
- Créer la classe Personality
- Implémenter des profils types
- Ajouter les weights d'influence
- Tests et documentation

**Notes:** Pour l'originalité (Epic 8)

---

### US-2.6 | Intégrer Ollama dans les agents
**Epic:** Système Multi-Agents  
**Points:** 7  
**Priorité:** 🔴 Critique  
**Dépendances:** US-2.1, US-1.2, US-2.2, US-2.3, US-2.4

**Description:**  
En tant que développeur, je veux connecter les agents à Ollama pour qu'ils puissent générer du texte autonomement.

**Critères d'acceptation:**
- [ ] Agents appellent Ollama pour penser/parler
- [ ] Prompt engineering cohérent
- [ ] Gestion du contexte (mémoire → prompt)
- [ ] Timeouts et retry logic
- [ ] Cache des réponses optionnel

**Tâches:**
- Créer les prompts templates
- Intégrer le client Ollama
- Gérer le contexte
- Tests avec de vrais modèles

**Notes:** Cœur du système autonome

---

### US-2.7 | Implémenter le processus de décision des agents
**Epic:** Système Multi-Agents  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** US-2.6, US-2.4, US-2.5

**Description:**  
En tant qu'IA architect, je veux créer un système de prise de décision pour que les agents choisissent leurs actions intelligemment.

**Critères d'acceptation:**
- [ ] Agents analysent la situation
- [ ] Personnalité influence la décision
- [ ] Mémoire sociale considérée
- [ ] Actions variées (parler, accuser, voter)
- [ ] Tests de cohérence

**Tâches:**
- Implémenter DecisionMaker
- Créer la logique de sélection d'action
- Intégrer personnalité et mémoire
- Tests

**Notes:** Complexité IA

---

## 🎮 EPIC 3️⃣ : Mécanique du Jeu

### US-3.1 | Créer le gestionnaire de parties
**Epic:** Mécanique du Jeu  
**Points:** 6  
**Priorité:** 🔴 Critique  
**Dépendances:** US-1.1, US-2.1, US-1.4

**Description:**  
En tant que game designer, je veux créer un gestionnaire de parties pour orchestrer le flux du jeu.

**Critères d'acceptation:**
- [ ] Création de nouvelles parties
- [ ] Attribution aléatoire des rôles
- [ ] Gestion de l'état global
- [ ] Passage des phases
- [ ] Fin de partie détectée

**Tâches:**
- Implémenter GameEngine
- Gérer les états de jeu
- Assigner les rôles
- Tests

**Notes:** Orchestratrice centrale

---

### US-3.2 | Implémenter le système de rôles
**Epic:** Mécanique du Jeu  
**Points:** 6  
**Priorité:** 🔴 Critique  
**Dépendances:** US-2.1, US-3.1

**Description:**  
En tant que game designer, je veux implémenter les 3 rôles MVP pour que le jeu soit jouable.

**Critères d'acceptation:**
- [ ] Rôle Loup-Garou avec pouvoirs
- [ ] Rôle Villageois simple
- [ ] Rôle Voyante avec observation
- [ ] Règles de chaque rôle
- [ ] Tests unitaires

**Tâches:**
- Créer les classes de rôles
- Implémenter les pouvoirs
- Gérer les restrictions d'accès
- Tests

**Notes:** MVP essentiel

---

### US-3.3 | Implémenter la phase nuit
**Epic:** Mécanique du Jeu  
**Points:** 6  
**Priorité:** 🔴 Critique  
**Dépendances:** US-3.1, US-3.2

**Description:**  
En tant que game designer, je veux implémenter la phase nuit pour que les loups et voyante puissent agir.

**Critères d'acceptation:**
- [ ] Loups choisissent une victime
- [ ] Voyante observe un agent
- [ ] Actions exécutées secrètement
- [ ] Messages système générés
- [ ] Tests

**Tâches:**
- Implémenter NightPhase
- Actions des rôles
- Résolution des conflicts
- Tests

**Notes:** Phase clé du gameplay

---

### US-3.4 | Implémenter la phase jour
**Epic:** Mécanique du Jeu  
**Points:** 7  
**Priorité:** 🔴 Critique  
**Dépendances:** US-3.1, US-3.2

**Description:**  
En tant que game designer, je veux implémenter la phase jour pour que tous les agents débattent et votent.

**Critères d'acceptation:**
- [ ] Discussion libre entre agents
- [ ] Chaque agent peut parler
- [ ] Temps de parole respecté
- [ ] Vote lancé à la fin
- [ ] Messages publics visibles

**Tâches:**
- Implémenter DayPhase
- Gérer les discussions
- Implémenter le vote
- Tests

**Notes:** Cœur du jeu

---

### US-3.5 | Implémenter le système de vote
**Epic:** Mécanique du Jeu  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-3.1, US-3.4

**Description:**  
En tant que game designer, je veux implémenter un système de vote pour éliminer les agents par majorité.

**Critères d'acceptation:**
- [ ] Chaque agent vote
- [ ] Majorité simple appliquée
- [ ] Résultats annoncés
- [ ] Égalités gérées
- [ ] Tests

**Tâches:**
- Implémenter VotingSystem
- Gérer les cas limites
- Résoudre les égalités
- Tests

**Notes:** Mécanisme clé

---

### US-3.6 | Implémenter les conditions de fin
**Epic:** Mécanique du Jeu  
**Points:** 4  
**Priorité:** 🟠 Haute  
**Dépendances:** US-3.1, US-3.2

**Description:**  
En tant que game designer, je veux vérifier les conditions de victoire/défaite pour terminer le jeu correctement.

**Critères d'acceptation:**
- [ ] Village gagne si tous loups morts
- [ ] Loups gagnent si égalité
- [ ] Fin détectée automatiquement
- [ ] Statistiques finales calculées
- [ ] Tests

**Tâches:**
- Implémenter WinCondition checker
- Calculer les stats
- Logger la fin
- Tests

**Notes:** Conclusion du jeu

---

### US-3.7 | Intégrer les phases au GameEngine
**Epic:** Mécanique du Jeu  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-3.1, US-3.3, US-3.4, US-3.5, US-3.6

**Description:**  
En tant qu'architecte, je veux intégrer toutes les phases pour que le jeu boucle correctement.

**Critères d'acceptation:**
- [ ] Phases alternent (nuit → jour → nuit)
- [ ] Transitions lisses
- [ ] États cohérents
- [ ] Gestion d'erreurs
- [ ] Tests d'intégration

**Tâches:**
- Créer la boucle de jeu
- Gérer les transitions
- Gérer les erreurs
- Tests complets

**Notes:** Intégration complète

---

## 📊 EPIC 4️⃣ : Observation & Monitoring

### US-4.1 | Implémenter le logging des événements
**Epic:** Observation & Monitoring  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-1.3, US-3.1

**Description:**  
En tant qu'analyseur, je veux logger tous les événements du jeu pour pouvoir les rejouer et les analyser.

**Critères d'acceptation:**
- [ ] Tous les événements loggés (messages, votes, actions)
- [ ] Timestamps corrects
- [ ] Format structuré
- [ ] Rotation des logs
- [ ] Tests

**Tâches:**
- Créer GameLogger
- Logger tous les événements
- Tests

**Notes:** Essentiel pour l'analyse

---

### US-4.2 | Implémenter l'exporteur JSON
**Epic:** Observation & Monitoring  
**Points:** 4  
**Priorité:** 🟠 Haute  
**Dépendances:** US-4.1

**Description:**  
En tant qu'analyseur, je veux exporter les données en JSON pour les analyser avec d'autres outils.

**Critères d'acceptation:**
- [ ] Export JSON complet
- [ ] Schéma valide
- [ ] Toutes les données incluses
- [ ] Formatage joli
- [ ] Tests

**Tâches:**
- Implémenter JSONExporter
- Valider le schéma
- Tests

**Notes:** Pour les analyses externes

---

### US-4.3 | Implémenter l'exporteur CSV
**Epic:** Observation & Monitoring  
**Points:** 3  
**Priorité:** 🟡 Moyenne  
**Dépendances:** US-4.1

**Description:**  
En tant qu'analyseur, je veux exporter les données en CSV pour les traiter avec Excel/Pandas.

**Critères d'acceptation:**
- [ ] Export CSV des votes
- [ ] Export CSV des messages
- [ ] Headers cohérents
- [ ] Tests

**Tâches:**
- Implémenter CSVExporter
- Tests

**Notes:** Pour analyses statistiques

---

### US-4.4 | Créer le gestionnaire d'historique
**Epic:** Observation & Monitoring  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-4.1, US-3.1

**Description:**  
En tant qu'analyseur, je veux accéder facilement à l'historique d'une partie pour la rejouer et l'analyser.

**Critères d'acceptation:**
- [ ] Historique complet sauvegardé
- [ ] Récupération rapide
- [ ] Replay possible
- [ ] Recherche d'événements
- [ ] Tests

**Tâches:**
- Implémenter GameHistory
- Créer les méthodes de recherche
- Tests

**Notes:** Pour l'analyse post-mortem

---

## 🖥️ EPIC 5️⃣ : Interface d'Observation

### US-5.1 | Créer le projet frontend React/Vue
**Epic:** Interface d'Observation  
**Points:** 4  
**Priorité:** 🔴 Critique  
**Dépendances:** US-1.1, US-1.4

**Description:**  
En tant que frontend developer, je veux initialiser un projet frontend pour l'interface d'observation.

**Critères d'acceptation:**
- [ ] Projet React/Vue créé
- [ ] Connexion WebSocket établie
- [ ] Structure des composants
- [ ] Tests basiques

**Tâches:**
- Initialiser le projet
- Configurer WebSocket
- Créer l'architecture
- Tests

**Notes:** Base du frontend

---

### US-5.2 | Implémenter la vue temps réel des messages
**Epic:** Interface d'Observation  
**Points:** 5  
**Priorité:** 🔴 Critique  
**Dépendances:** US-5.1, US-3.4

**Description:**  
En tant que observateur, je veux voir les messages des agents en temps réel pour suivre les discussions.

**Critères d'acceptation:**
- [ ] Messages affichés en temps réel
- [ ] Auteur et rôle visibles
- [ ] Timestamp affiché
- [ ] Scroll automatique
- [ ] Design clair

**Tâches:**
- Créer MessageList component
- Styler l'interface
- Tests

**Notes:** Fonctionnalité core

---

### US-5.3 | Implémenter l'affichage du graphe d'interactions
**Epic:** Interface d'Observation  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** US-5.1, US-2.4

**Description:**  
En tant qu'analyseur, je veux voir un graphe des relations entre agents pour visualiser les alliances.

**Critères d'acceptation:**
- [ ] Graphe des agents visible
- [ ] Liens de confiance affichés
- [ ] Couleurs par alignement
- [ ] Interactif (zoom, drag)
- [ ] Design propre

**Tâches:**
- Utiliser D3.js ou Plotly
- Créer le composant
- Tests

**Notes:** Bonus si beau

---

### US-5.4 | Implémenter la timeline jour/nuit
**Epic:** Interface d'Observation  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-5.1, US-3.1

**Description:**  
En tant qu'observateur, je veux voir la timeline jour/nuit pour suivre la progression du jeu.

**Critères d'acceptation:**
- [ ] Timeline visuelle jour/nuit
- [ ] Phase actuelle mise en évidence
- [ ] Actions de la nuit résumées
- [ ] Tour numéroté

**Tâches:**
- Créer Timeline component
- Styler joliment
- Tests

**Notes:** Vue importante

---

### US-5.5 | Implémenter l'historique des votes
**Epic:** Interface d'Observation  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-5.1, US-3.5

**Description:**  
En tant qu'analyseur, je veux voir l'historique des votes pour analyser les patterns de vote.

**Critères d'acceptation:**
- [ ] Tableau des votes
- [ ] Qui a voté pour qui
- [ ] Résultats par tour
- [ ] Statistiques simples

**Tâches:**
- Créer VoteHistory component
- Ajouter les stats
- Tests

**Notes:** Données analytiques

---

### US-5.6 | Implémenter la heatmap des accusations
**Epic:** Interface d'Observation  
**Points:** 6  
**Priorité:** 🟡 Moyenne  
**Dépendances:** US-5.1, US-3.4

**Description:**  
En tant qu'analyseur, je veux une heatmap des accusations pour voir qui accuse qui.

**Critères d'acceptation:**
- [ ] Heatmap accusation
- [ ] Couleurs par intensité
- [ ] Axes: accusateurs/accusés
- [ ] Interactif

**Tâches:**
- Utiliser une lib heatmap
- Créer le composant
- Tests

**Notes:** Bonus points

---

### US-5.7 | Créer le layout principal de l'interface
**Epic:** Interface d'Observation  
**Points:** 4  
**Priorité:** 🔴 Critique  
**Dépendances:** US-5.2, US-5.4, US-5.5

**Description:**  
En tant que UX designer, je veux créer un layout propre pour assembler tous les composants.

**Critères d'acceptation:**
- [ ] Layout responsive
- [ ] Dashboard cohérent
- [ ] Navigation claire
- [ ] Design professionnel
- [ ] Mobile-friendly bonus

**Tâches:**
- Créer le layout
- Responsive design
- CSS styling
- Tests

**Notes:** Présentation finale

---

## ⚙️ EPIC 6️⃣ : Paramètres Expérimentaux

### US-6.1 | Créer le gestionnaire de configuration de parties
**Epic:** Paramètres Expérimentaux  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-1.5, US-3.1

**Description:**  
En tant que chercheur, je veux configurer les paramètres des parties pour conduire des expériences.

**Critères d'acceptation:**
- [ ] Nombre d'agents configurable
- [ ] Nombre de loups configurable
- [ ] Rôles sélectionnables
- [ ] Stockage des configs
- [ ] Chargement des configs

**Tâches:**
- Implémenter GameConfig
- Parser les configurations
- Tests

**Notes:** Expérimentation

---

### US-6.2 | Implémenter la modification des personnalités
**Epic:** Paramètres Expérimentaux  
**Points:** 5  
**Priorité:** 🟡 Moyenne  
**Dépendances:** US-2.5, US-6.1

**Description:**  
En tant que chercheur, je veux modifier les personnalités pour tester différents profils.

**Critères d'acceptation:**
- [ ] Édition des traits de personnalité
- [ ] Profils prédéfinis
- [ ] Application dynamique
- [ ] Tests

**Tâches:**
- Ajouter des API d'édition
- Créer UI de configuration
- Tests

**Notes:** Science comportementale

---

### US-6.3 | Implémenter l'injection d'événements
**Epic:** Paramètres Expérimentaux  
**Points:** 5  
**Priorité:** 🟡 Moyenne  
**Dépendances:** US-3.1, US-6.1

**Description:**  
En tant que chercheur, je veux injecter des événements pour perturber le jeu et tester la robustesse.

**Critères d'acceptation:**
- [ ] Injection de faux messages
- [ ] Injection de pannes
- [ ] Application dynamique
- [ ] Tests

**Tâches:**
- Créer EventInjector
- Tests

**Notes:** Tests de robustesse

---

### US-6.4 | Implémenter la configuration du bruit informationnel
**Epic:** Paramètres Expérimentaux  
**Points:** 4  
**Priorité:** 🟡 Moyenne  
**Dépendances:** US-3.4, US-6.1

**Description:**  
En tant que chercheur, je veux ajouter du bruit aux messages pour étudier l'impact sur la décision.

**Critères d'acceptation:**
- [ ] Niveau de bruit configurable
- [ ] Messages altérés aléatoirement
- [ ] Logging du bruit
- [ ] Tests

**Tâches:**
- Implémenter NoiseInjector
- Tests

**Notes:** Étude comportementale

---

### US-6.5 | Créer l'API de paramètrisation
**Epic:** Paramètres Expérimentaux  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** US-6.1, US-6.2, US-6.3, US-6.4

**Description:**  
En tant que développeur API, je veux créer une API REST pour configurer les expériences.

**Critères d'acceptation:**
- [ ] Endpoints pour créer/éditer configs
- [ ] Validation des paramètres
- [ ] Stockage persistant
- [ ] Documentation API
- [ ] Tests

**Tâches:**
- Créer les routes FastAPI
- Validation
- Tests

**Notes:** Interface programmatique

---

## 📚 EPIC 7️⃣ : Tests & Documentation

### US-7.1 | Créer des tests unitaires pour l'Agent
**Epic:** Tests & Documentation  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-2.1

**Description:**  
En tant que QA, je veux tester la classe Agent pour assurer sa fiabilité.

**Critères d'acceptation:**
- [ ] Tests de création
- [ ] Tests de propriétés
- [ ] Tests d'état
- [ ] Coverage > 80%

**Tâches:**
- Écrire les tests pytest
- Mesurer le coverage
- CI/CD hooks

**Notes:** Fondation des tests

---

### US-7.2 | Créer des tests unitaires pour GameEngine
**Epic:** Tests & Documentation  
**Points:** 6  
**Priorité:** 🔴 Critique  
**Dépendances:** US-3.1, US-3.7

**Description:**  
En tant que QA, je veux tester GameEngine pour assurer l'intégrité du jeu.

**Critères d'acceptation:**
- [ ] Tests des phases
- [ ] Tests de transitions
- [ ] Tests de fin
- [ ] Coverage > 85%

**Tâches:**
- Écrire tests complets
- Tests d'intégration
- CI/CD

**Notes:** Critique pour le jeu

---

### US-7.3 | Créer des tests d'intégration
**Epic:** Tests & Documentation  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** Toutes les US de code

**Description:**  
En tant que QA, je veux tester l'intégration complète du système.

**Critères d'acceptation:**
- [ ] Tests de parties complètes
- [ ] Tests de communication WebSocket
- [ ] Tests de logging
- [ ] Coverage > 70%

**Tâches:**
- Tests end-to-end
- Fixtures de test
- CI/CD

**Notes:** Validation système

---

### US-7.4 | Rédiger le README.md
**Epic:** Tests & Documentation  
**Points:** 8  
**Priorité:** 🔴 Critique  
**Dépendances:** Toutes les implémentations

**Description:**  
En tant que documentaliste, je veux un README complet et professionnel.

**Critères d'acceptation:**
- [ ] README en anglais
- [ ] Schéma général du projet
- [ ] Guide d'installation
- [ ] Exemples d'usage
- [ ] Screenshots
- [ ] Description des features

**Tâches:**
- Rédiger le README
- Ajouter schémas
- Screenshots
- Exemples

**Notes:** Note sur 20%

---

### US-7.5 | Documenter l'API et les modules
**Epic:** Tests & Documentation  
**Points:** 6  
**Priorité:** 🟠 Haute  
**Dépendances:** Tous les modules implémentés

**Description:**  
En tant que documentaliste, je veux documenter toutes les APIs pour faciliter la maintenance.

**Critères d'acceptation:**
- [ ] Docstrings sur toutes les classes
- [ ] Docstrings sur toutes les méthodes
- [ ] Format Sphinx ou similar
- [ ] Exemples de code

**Tâches:**
- Ajouter docstrings
- Générer docs HTML
- Tests de docs

**Notes:** Maintenabilité

---

### US-7.6 | Créer des exemples d'usage
**Epic:** Tests & Documentation  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** Toutes les features

**Description:**  
En tant que documentaliste, je veux créer des exemples prêts à l'emploi.

**Critères d'acceptation:**
- [ ] Exemple simple de jeu
- [ ] Exemple d'analyse de logs
- [ ] Exemple de configuration
- [ ] Tous fonctionnels
- [ ] Documentation

**Tâches:**
- Créer exemples.py
- Ajouter documentation
- Tests des exemples

**Notes:** Facilite adoption

---

### US-7.7 | Créer un schéma général du projet
**Epic:** Tests & Documentation  
**Points:** 4  
**Priorité:** 🔴 Critique  
**Dépendances:** US-7.4

**Description:**  
En tant que documentaliste, je veux un schéma d'architecture pour comprendre le système.

**Critères d'acceptation:**
- [ ] Schéma général (Markdown)
- [ ] Architecture de haut niveau
- [ ] Flux de données
- [ ] Clair et professionnel

**Tâches:**
- Créer le diagramme
- Ajouter au README

**Notes:** Comprehension

---

### US-7.8 | Créer les diagrammes UML
**Epic:** Tests & Documentation  
**Points:** 6  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** Tous les modules

**Description:**  
En tant qu'architecte, je veux des diagrammes UML pour documenter le design.

**Critères d'acceptation:**
- [ ] Diagramme de classes principal
- [ ] Diagramme d'interactions
- [ ] Diagramme de déploiement
- [ ] Fichiers plantUML ou PNG

**Tâches:**
- Créer les diagrammes
- Exporter en images
- Ajouter au README

**Notes:** Bonus points (10%)

---

### US-7.9 | Configurer CI/CD
**Epic:** Tests & Documentation  
**Points:** 5  
**Priorité:** 🟠 Haute  
**Dépendances:** US-7.1, US-7.2, US-7.3

**Description:**  
En tant que DevOps, je veux automatiser les tests pour assurer la qualité.

**Critères d'acceptation:**
- [ ] GitHub Actions configurées
- [ ] Tests lancés à chaque push
- [ ] Linting (flake8, black)
- [ ] Coverage rapportée
- [ ] Branche main protégée

**Tâches:**
- Créer workflows
- Configurer règles de branche
- Tests locaux pré-commit

**Notes:** Qualité continue

---

## 🌟 EPIC 8️⃣ : Bonus & Originalité

### US-8.1 | Implémenter les biais cognitifs des agents
**Epic:** Bonus & Originalité  
**Points:** 7  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-2.5, US-2.7

**Description:**  
En tant que chercheur en IA, je veux ajouter des biais cognitifs pour que les agents soient plus réalistes.

**Critères d'acceptation:**
- [ ] Biais de confirmation implémenté
- [ ] Biais d'ancrage implémenté
- [ ] Biais de groupe implémenté
- [ ] Impact sur les décisions
- [ ] Tests et documentation

**Tâches:**
- Implémenter CognitiveBiases
- Tests
- Documentation scientifique

**Notes:** Originalité (10%)

---

### US-8.2 | Implémenter le mode tournoi
**Epic:** Bonus & Originalité  
**Points:** 8  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-3.7, US-4.4

**Description:**  
En tant que game designer, je veux un mode tournoi pour comparer des agents.

**Critères d'acceptation:**
- [ ] Tournoi round-robin
- [ ] Statistiques par agent
- [ ] Classement final
- [ ] Interface de tournoi
- [ ] Export des résultats

**Tâches:**
- Implémenter TournamentMode
- UI pour résultats
- Tests

**Notes:** Originalité

---

### US-8.3 | Analyser et visualiser les comportements
**Epic:** Bonus & Originalité  
**Points:** 8  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-4.1, US-5.1

**Description:**  
En tant qu'analyseur, je veux analyser les comportements des agents pour extraire des insights.

**Critères d'acceptation:**
- [ ] Score de mensonge estimé
- [ ] Patterns détectés
- [ ] Alliances analysées
- [ ] Graphes de comportement
- [ ] Export d'analyses

**Tâches:**
- Implémenter BehaviorAnalyzer
- Créer visualisations
- Tests

**Notes:** Science

---

### US-8.4 | Ajouter une licence au projet
**Epic:** Bonus & Originalité  
**Points:** 1  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-1.1

**Description:**  
En tant que mainteneur, je veux ajouter une licence au projet.

**Critères d'acceptation:**
- [ ] Fichier LICENSE créé
- [ ] MIT ou Apache choisi
- [ ] Référence dans README

**Tâches:**
- Ajouter LICENSE
- Ajouter lien dans README

**Notes:** Légal

---

### US-8.5 | Supporter plusieurs modèles Ollama
**Epic:** Bonus & Originalité  
**Points:** 6  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-2.6, US-1.2

**Description:**  
En tant que chercheur, je veux supporter plusieurs modèles LLM pour comparer leurs comportements.

**Critères d'acceptation:**
- [ ] Agents peuvent utiliser différents modèles
- [ ] Configuration par agent
- [ ] Comparaison de modèles
- [ ] Performances mesurées

**Tâches:**
- Adapter client Ollama
- Permettre sélection de modèle
- Tests

**Notes:** Étude comparative

---

### US-8.6 | Créer une visualisation avancée
**Epic:** Bonus & Originalité  
**Points:** 7  
**Priorité:** 🟡 Moyenne (Bonus)  
**Dépendances:** US-5.1

**Description:**  
En tant que designer, je veux une visualisation avancée impressionnante.

**Critères d'acceptation:**
- [ ] Visualisation interactive
- [ ] Données temps réel
- [ ] Design professionnel
- [ ] Performance optimale

**Tâches:**
- Implémenter avec D3.js ou Plotly
- Optimiser performance
- Tester

**Notes:** Wow factor

---

---

## 📋 Tableau Récapitulatif

| US | Titre | Epic | Points | Priorité | État |
|-----|-------|------|--------|----------|------|
| US-1.1 | Initialiser structure | 1 | 3 | 🔴 | ⬜ |
| US-1.2 | Configurer Ollama | 1 | 5 | 🔴 | ⬜ |
| US-1.3 | Système de logging | 1 | 4 | 🟠 | ⬜ |
| US-1.4 | Communication WebSocket | 1 | 6 | 🔴 | ⬜ |
| US-1.5 | Système de configuration | 1 | 4 | 🟠 | ⬜ |
| US-2.1 | Classe Agent | 2 | 5 | 🔴 | ⬜ |
| US-2.2 | Mémoire courte | 2 | 5 | 🔴 | ⬜ |
| US-2.3 | Mémoire longue | 2 | 5 | 🟠 | ⬜ |
| US-2.4 | Mémoire sociale | 2 | 6 | 🟠 | ⬜ |
| US-2.5 | Système personnalités | 2 | 6 | 🟠 | ⬜ |
| US-2.6 | Intégrer Ollama | 2 | 7 | 🔴 | ⬜ |
| US-2.7 | Processus décision | 2 | 6 | 🟠 | ⬜ |
| US-3.1 | Gestionnaire de parties | 3 | 6 | 🔴 | ⬜ |
| US-3.2 | Système de rôles | 3 | 6 | 🔴 | ⬜ |
| US-3.3 | Phase nuit | 3 | 6 | 🔴 | ⬜ |
| US-3.4 | Phase jour | 3 | 7 | 🔴 | ⬜ |
| US-3.5 | Système vote | 3 | 5 | 🔴 | ⬜ |
| US-3.6 | Conditions fin | 3 | 4 | 🟠 | ⬜ |
| US-3.7 | Intégration phases | 3 | 5 | 🔴 | ⬜ |
| US-4.1 | Logging événements | 4 | 5 | 🟠 | ⬜ |
| US-4.2 | Exporteur JSON | 4 | 4 | 🟠 | ⬜ |
| US-4.3 | Exporteur CSV | 4 | 3 | 🟡 | ⬜ |
| US-4.4 | Gestionnaire historique | 4 | 5 | 🟠 | ⬜ |
| US-5.1 | Projet frontend | 5 | 4 | 🔴 | ⬜ |
| US-5.2 | Vue messages | 5 | 5 | 🔴 | ⬜ |
| US-5.3 | Graphe interactions | 5 | 6 | 🟠 | ⬜ |
| US-5.4 | Timeline jour/nuit | 5 | 5 | 🟠 | ⬜ |
| US-5.5 | Historique votes | 5 | 5 | 🟠 | ⬜ |
| US-5.6 | Heatmap accusations | 5 | 6 | 🟡 | ⬜ |
| US-5.7 | Layout principal | 5 | 4 | 🔴 | ⬜ |
| US-6.1 | Config de parties | 6 | 5 | 🟠 | ⬜ |
| US-6.2 | Modifier personnalités | 6 | 5 | 🟡 | ⬜ |
| US-6.3 | Injection événements | 6 | 5 | 🟡 | ⬜ |
| US-6.4 | Config bruit | 6 | 4 | 🟡 | ⬜ |
| US-6.5 | API paramètrisation | 6 | 6 | 🟠 | ⬜ |
| US-7.1 | Tests Agent | 7 | 5 | 🟠 | ⬜ |
| US-7.2 | Tests GameEngine | 7 | 6 | 🔴 | ⬜ |
| US-7.3 | Tests intégration | 7 | 6 | 🟠 | ⬜ |
| US-7.4 | Rédiger README | 7 | 8 | 🔴 | ⬜ |
| US-7.5 | Documenter APIs | 7 | 6 | 🟠 | ⬜ |
| US-7.6 | Créer exemples | 7 | 5 | 🟠 | ⬜ |
| US-7.7 | Schéma projet | 7 | 4 | 🔴 | ⬜ |
| US-7.8 | Diagrammes UML | 7 | 6 | 🟡 | ⬜ |
| US-7.9 | Configurer CI/CD | 7 | 5 | 🟠 | ⬜ |
| US-8.1 | Biais cognitifs | 8 | 7 | 🟡 | ⬜ |
| US-8.2 | Mode tournoi | 8 | 8 | 🟡 | ⬜ |
| US-8.3 | Analyser comportements | 8 | 8 | 🟡 | ⬜ |
| US-8.4 | Ajouter licence | 8 | 1 | 🟡 | ⬜ |
| US-8.5 | Multiples modèles | 8 | 6 | 🟡 | ⬜ |
| US-8.6 | Visualisation avancée | 8 | 7 | 🟡 | ⬜ |

**Total: 276 points**

---

## 🎓 Notes Importantes

- **États:** ⬜ À faire | 🟨 En cours | ✅ Fait
- **Priorités:** 🔴 Critique | 🟠 Haute | 🟡 Moyenne
- **Les Epics 1-7 sont obligatoires** pour le MVP
- **L'Epic 8 est bonus** pour la complexité et l'originalité
- **Adapter la répartition** en fonction du nombre réel de personnes dans l'équipe
- **Utiliser Git branches** pour chaque US importante
- **Faire des PR reviews** entre membres de l'équipe
