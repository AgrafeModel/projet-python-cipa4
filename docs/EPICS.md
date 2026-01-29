# 🎯 Épics - Loup-Garou Multi-Agents LLM

## Vue d'ensemble

Ce document liste les grands axes du projet (Épics) qui structurent le travail en équipe.

---

## Epic 1️⃣ : Architecture & Infrastructure

**Description:** Mise en place de l'infrastructure technique de base du système multi-agents

**Objectif:** Créer une base solide pour les agents et l'orchestration

**Points d'effort estimés:** 40 points

**Dépendances:** Aucune (Epic fondatrice)

**Critères d'acceptation:**
- [ ] Structure des dossiers respecte les bonnes pratiques
- [ ] Configuration Ollama fonctionnelle
- [ ] Communication WebSocket établie
- [ ] Logs centralisés en place

**Sous-composants:**
- Game Engine (gestionnaire de partie)
- Agent Framework (base des agents)
- Communication système
- Structure des données

---

## Epic 2️⃣ : Système Multi-Agents

**Description:** Développement des agents LLM autonomes avec personnalité et mémoire

**Objectif:** Agents capables de communiquer, penser et prendre des décisions

**Points d'effort estimés:** 50 points

**Dépendances:** Epic 1

**Critères d'acceptation:**
- [ ] Agents créés avec rôles distincts
- [ ] Système de mémoire fonctionnel
- [ ] Intégration Ollama réussie
- [ ] Agents communiquent entre eux
- [ ] Système de personnalité implémenté

**Sous-composants:**
- Agent LLM principal
- Système de mémoire (courte/longue/sociale)
- Intégration Ollama
- Personnalités d'agents

---

## Epic 3️⃣ : Mécanique du Jeu

**Description:** Implémentation des règles du Loup-Garou

**Objectif:** Un jeu fonctionnel avec cycles jour/nuit et votes

**Points d'effort estimés:** 45 points

**Dépendances:** Epic 1, Epic 2

**Critères d'acceptation:**
- [ ] Phases jour/nuit alternent correctement
- [ ] Rôles fonctionnels (Loup-Garou, Villageois, Voyante)
- [ ] Système de vote implémenté
- [ ] Conditions de victoire/défaite opérationnelles
- [ ] Gestion des éliminations

**Sous-composants:**
- Gestionnaire de phases
- Système de rôles
- Système de vote
- Règles de fin de partie

---

## Epic 4️⃣ : Observation & Monitoring

**Description:** Système de logs, traçabilité et monitoring des parties

**Objectif:** Observer et analyser le comportement des agents

**Points d'effort estimés:** 30 points

**Dépendances:** Epic 1, Epic 2, Epic 3

**Critères d'acceptation:**
- [ ] Tous les événements sont loggés
- [ ] Export JSON/CSV fonctionnel
- [ ] Historique des votes enregistré
- [ ] Discussions stockées
- [ ] Format de log cohérent

**Sous-composants:**
- Système de logging
- Exporteur de données
- Gestionnaire d'historique
- Analyseur de parties

---

## Epic 5️⃣ : Interface d'Observation Humaine

**Description:** Développement de l'interface web pour observer les parties

**Objectif:** Visualisation temps réel pour les observateurs

**Points d'effort estimés:** 40 points

**Dépendances:** Epic 1, Epic 3, Epic 4

**Critères d'acceptation:**
- [ ] Vue temps réel des messages
- [ ] Graphe d'interactions visible
- [ ] Timeline jour/nuit opérationnelle
- [ ] Historique des votes affiché
- [ ] Interface responsive

**Sous-composants:**
- Frontend React/Vue
- Connexion WebSocket
- Composants de visualisation
- Gestion de l'interface

---

## Epic 6️⃣ : Paramètres Expérimentaux

**Description:** Système de configuration et manipulation de la plateforme

**Objectif:** Permettre aux humains de modifier les conditions de jeu

**Points d'effort estimés:** 35 points

**Dépendances:** Epic 1, Epic 2, Epic 3

**Critères d'acceptation:**
- [ ] Configuration des parties sauvegardable
- [ ] Modification des personnalités possible
- [ ] Injection d'événements fonctionnelle
- [ ] Bruit informationnel configurable
- [ ] Paramètres de mémoire ajustables

**Sous-composants:**
- Gestionnaire de configuration
- API de paramètrisation
- Système d'injection d'événements
- Stockage des configurations

---

## Epic 7️⃣ : Tests & Documentation

**Description:** Tests unitaires, documentation et README complet

**Objectif:** Code de qualité avec documentation professionnelle

**Points d'effort estimés:** 35 points

**Dépendances:** Toutes (intégration continue)

**Critères d'acceptation:**
- [ ] Tests unitaires > 70% coverage
- [ ] README en anglais complétude
- [ ] Documentation des APIs
- [ ] Exemples d'utilisation fournis
- [ ] Diagrammes (schéma + UML bonus)

**Sous-composants:**
- Suite de tests
- README professionnel
- Documentation techniques
- Exemples
- Diagrammes UML

---

## Epic 8️⃣ : Bonus & Originalité

**Description:** Fonctionnalités avancées et originalité du projet

**Objectif:** Démarquer le projet avec des innovations

**Points d'effort estimés:** 30 points

**Dépendances:** Toutes les epics principales (Epic 1-7)

**Critères d'acceptation:**
- [ ] Licence MIT/Apache ajoutée
- [ ] Agents avec biais cognitifs
- [ ] Mode tournoi implémenté
- [ ] Analyses avancées de comportement
- [ ] UML diagrammes

**Sous-composants:**
- Biais cognitifs des agents
- Mode tournoi
- Analyses comportementales
- Visualisations avancées
- Licence du projet

---

## Matrice de Dépendances

```
Epic 1 (Architecture & Infrastructure)
  ↓
  ├─→ Epic 2 (Système Multi-Agents)
  │   ├─→ Epic 3 (Mécanique du Jeu)
  │   │   └─→ Epic 4 (Observation & Monitoring)
  │   │   └─→ Epic 5 (Interface d'Observation)
  │   └─→ Epic 6 (Paramètres Expérimentaux)
  │
  └─→ Epic 7 (Tests & Documentation) ← Transversal à toutes
      └─→ Epic 8 (Bonus & Originalité)
```

---

## Effort Total Estimé

| Epic | Points |
|------|--------|
| Epic 1 | 40 |
| Epic 2 | 50 |
| Epic 3 | 45 |
| Epic 4 | 30 |
| Epic 5 | 40 |
| Epic 6 | 35 |
| Epic 7 | 35 |
| Epic 8 | 30 |
| **TOTAL** | **305 points** |

---

## Répartition Recommandée par Équipe (4 personnes)

**Personne 1:** Epic 1 + 2 (Architecture & Agents) - ~90 points
**Personne 2:** Epic 3 + 4 (Mécanique & Logs) - ~75 points
**Personne 3:** Epic 5 + 6 (Interface & Configuration) - ~75 points
**Personne 4:** Epic 7 + 8 (Tests, Docs & Bonus) - ~65 points

*À adapter en fonction de l'équipe réelle*
