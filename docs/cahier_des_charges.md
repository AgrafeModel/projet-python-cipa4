# 📘 Cahier des charges - Loup-Garou Multi-Agents LLM

## 1. Présentation générale

### 1.1 Intitulé du projet

Simulation de jeu du Loup-Garou par agents LLM autonomes dans un environnement distribué, observable et manipulable par des humains.

### 1.2 Objectif principal

Créer une plateforme expérimentale permettant d'observer:
- Les comportements émergents
- La coopération
- Le mensonge
- La manipulation
- La prise de décision collective

Chez des agents conversationnels autonomes, sans intervention humaine directe dans le gameplay.
Les humains jouent uniquement un rôle méta (observateurs et modificateurs du système).

## 2. Objectifs pédagogiques et scientifiques

### Objectifs techniques
- Systèmes multi-agents
- Réseau distribué
- Orchestration de LLM locaux (via Ollama)
- Gestion de mémoire et d'état
- Simulation temps réel
- Visualisation de données sociales

### Objectifs expérimentaux
- Étudier la formation d'alliances
- Observer le mensonge stratégique
- Comparer des personnalités d'agents
- Étudier l'impact du bruit et de règles instables
- Analyser la robustesse des décisions collectives

**➡️ Le système devient un laboratoire social artificiel contrôlé.**

## 3. Architecture générale

### 3.1 Vue d'ensemble

```
┌──────────────┐
│ Interface UI │ ← humains
└──────┬───────┘
       │
┌──────▼──────────────────┐
│   Game Orchestrator     │
│ (serveur central)       │
└──────┬──────────────────┘
       │ réseau (WebSocket / TCP)
┌──────▼─────┐   ┌──────▼─────┐   ┌──────▼─────┐
│ Agent LLM   │   │ Agent LLM   │   │ Agent LLM   │
│ (Ollama)    │   │ (Ollama)    │   │ (Ollama)    │
└────────────┘   └────────────┘   └────────────┘
```

## 4. Technologies envisagées

### 4.1 Modèles LLM

#### 4.1.1 Modèles locaux

**Infrastructure:**
- Ollama (obligatoire)

**Modèles possibles:**
- mistral
- llama3
- qwen
- mixtral (si GPU)

**Principes:**
- Un modèle = un agent (ou pool)

### 4.2 Backend

**Langage:** Python

**Frameworks possibles:**
- FastAPI (API + WebSocket)
- asyncio

**Communication:**
- WebSockets (recommandé)
- JSON messages

### 4.3 Frontend (observateurs humains)

**Stack:**
- Web app
- React / Vue / Svelte

**Visualisations:**
- Timeline
- Graphe d'alliances
- Heatmap de votes
- Replay des parties

## 5. Description des entités

### 5.1 Agent LLM

Chaque agent représente un joueur.

**Propriétés:**
- ID unique
- Rôle secret
- Alignement (Village / Loups)
- Personnalité
- Objectifs
- Mémoire interne
- Confiance envers les autres agents
- Historique de décisions

**Exemple de personnalité:**
```json
{
  "style": "agressif",
  "tendance_au_mensonge": 0.8,
  "paranoia": 0.6,
  "coopération": 0.3
}
```

**Capacités:**
- Parler
- Accuser
- Défendre
- Mentir
- Voter
- Changer d'opinion
- Élaborer des stratégies

### 5.2 Rôles du jeu

**Rôles minimum (MVP):**
- 🐺 Loup-Garou
- 👨‍🌾 Villageois
- 🔮 Voyante

**Extensions possibles:**
- Sorcière
- Chasseur
- Enfant sauvage
- Maire

## 6. Mécanique du jeu

### 6.1 Phases

**Phase Nuit:**
- Loups désignent une victime
- Voyante observe un joueur

**Phase Jour:**
- Discussion libre entre agents
- Débats
- Accusations
- Vote
- Chaque agent vote
- Majorité éliminée

**Fin de partie:**
- Tous les loups morts → village gagne
- Loups ≥ village → loups gagnent

## 7. Vision partielle des agents

Chaque agent ne connaît que:
- Son rôle
- Les messages publics
- Ses observations personnelles
- Ses souvenirs

**❌ Aucun accès à:**
- L'état global
- Aux rôles des autres
- Aux paramètres modifiés par les humains

## 8. Mémoire des agents

### Types de mémoire

- **Mémoire courte:** Discussion récente
- **Mémoire longue:** Événements clés
- **Mémoire sociale:**
  - Qui accuse qui
  - Qui vote contre qui
  - Incohérences détectées

**Exemple:**
```json
{
  "agent_3": {
    "trust": -0.7,
    "reason": "a changé de vote sans justification"
  }
}
```

## 9. Rôle des humains (observateurs)

### Les humains peuvent

**Observer:**
- Discussions en direct
- Votes
- Rôles après la partie
- Statistiques

**Influencer indirectement:**

*Modifier paramètres globaux:*
- Niveau de bruit
- Mémoire maximale
- Temps de parole
- Changer la personnalité d'un agent

*Injecter des événements:*
- Faux message système
- Panne de communication
- Règle temporaire

**⚠️ Les humains ne connaissent jamais les rôles secrets.**

## 10. Interface humaine

### Fonctions

- Vue temps réel
- Lecture des messages
- Graphes d'interactions
- Historique des votes
- Replays
- Comparaison de parties

### Visualisations possibles

- Graphe social dynamique
- Heatmap des accusations
- Timeline jour/nuit
- Score de mensonge estimé

## 11. Paramètres expérimentaux

**Exemples:**
- Taille du village
- Nombre de loups
- Modèle LLM utilisé
- Personnalités
- Mémoire limitée ou non
- Présence de bruit informationnel
- Règles modifiées

**➡️ Chaque partie devient une expérience reproductible.**

## 12. Logs et analyse

### Le système doit enregistrer

- Toutes les discussions
- Tous les votes
- Décisions
- États internes (si autorisé)
- Paramètres utilisés

### Export

- JSON
- CSV
- Replay textuel

### Utilisation

- Analyse post-mortem
- Statistiques
- ML / clustering de comportements

## 13. Contraintes

### Techniques
- Fonctionnement local (pas d'API cloud)
- Compatible machines étudiantes
- Modèles Ollama optimisés
- Latence maîtrisée

### Éthiques
- Aucun humain n'est manipulé
- Pas d'apprentissage réel des modèles
- Simulation uniquement

## 14. MVP (version minimale)

- ✔ 6–8 agents
- ✔ 3 rôles
- ✔ Discussions texte
- ✔ Vote simple
- ✔ Interface observateur basique
- ✔ Logs complets

## 15. Évolutions possibles

- Agents hétérogènes (modèles différents)
- Agents avec biais cognitifs
- IA qui analyse les IA
- Mode tournoi
- Évolution de personnalités
- Comparaison humain vs IA (plus tard)

## 16. Résultat attendu

À la fin du projet:
- Une plateforme fonctionnelle
- Un système multi-agents autonome
- Un outil d'observation sociale artificielle
- Un support parfait pour rapport, soutenance et démo
