# Epic 2️⃣ : Système Multi-Agents

**Description:** Développement des agents LLM autonomes avec personnalité et mémoire

**Objectif:** Agents capables de communiquer, penser et prendre des décisions

**Points d'effort estimés:** 50 points  
**Statut global:** 🟨 En cours (43% complété)

---

## User Stories

### ✅ US-2.1 | Créer la classe Agent de base
**Points:** 5  
**Priorité:** 🔴 Critique  
**Statut:** ✅ Terminée

**Description:**  
En tant qu'architecte, je veux créer une classe Agent abstraite pour que tous les agents héritent d'une structure commune.

**Critères d'acceptation:**
- [x] Classe Agent avec ID unique
- [x] Propriétés de base (rôle, alignement, personnalité)
- [x] Méthodes abstraites pour les actions
- [x] Système d'état de l'agent
- [ ] Tests unitaires

**Notes:** ✅ Classe Agent complète dans ai/agent.py avec AgentConfig

---

### ⬜ US-2.2 | Implémenter le système de mémoire courte
**Points:** 5  
**Priorité:** 🔴 Critique  
**Statut:** ❌ À faire

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

**Notes:** Utilise actuellement chat_history du GameEngine

---

### ⬜ US-2.3 | Implémenter le système de mémoire longue
**Points:** 5  
**Priorité:** 🟠 Haute  
**Statut:** ❌ À faire

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

---

### ✅ US-2.4 | Implémenter le système de mémoire sociale
**Points:** 6  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que développeur, je veux implémenter une mémoire sociale pour que les agents trackent la confiance et le comportement des autres.

**Critères d'acceptation:**
- [x] Stockage des relations (confiance, suspicion)
- [x] Métriques de confiance par agent
- [x] Historique des changements de confiance
- [x] Détection d'incohérences
- [ ] Tests unitaires

**Notes:** ⚠️ Système de suspicion implémenté dans Agent.suspicion

---

### ✅ US-2.5 | Créer le système de personnalités
**Points:** 6  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que chercheur, je veux créer un système de personnalités pour que chaque agent ait un comportement distinct.

**Critères d'acceptation:**
- [x] Modèle de personnalité (style, paranoia, mensonge, coopération)
- [x] Personnalités prédéfinies
- [x] Influence sur les décisions
- [x] Sérialisation/désérialisation
- [ ] Tests et exemples

**Notes:** ⚠️ Attribut personality présent, templates par rôle (villageois/loup)

---

### ⬜ US-2.6 | Intégrer Ollama dans les agents
**Points:** 7  
**Priorité:** 🔴 Critique  
**Statut:** ❌ À faire

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

**Notes:** Actuellement utilise templates JSON prédéfinis

---

### ✅ US-2.7 | Implémenter le processus de décision des agents
**Points:** 6  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant qu'IA architect, je veux créer un système de prise de décision pour que les agents choisissent leurs actions intelligemment.

**Critères d'acceptation:**
- [x] Agents analysent la situation
- [x] Personnalité influence la décision
- [x] Mémoire sociale considérée
- [x] Actions variées (parler, accuser, voter)
- [ ] Tests de cohérence

**Notes:** ⚠️ decide_message() et choose_night_victim() implémentés dans Agent

---

## Progression

| User Story | Statut | Points |
|------------|--------|--------|
| US-2.1 | ✅ | 5 |
| US-2.2 | ❌ | 5 |
| US-2.3 | ❌ | 5 |
| US-2.4 | ⚠️ | 6 |
| US-2.5 | ⚠️ | 6 |
| US-2.6 | ❌ | 7 |
| US-2.7 | ⚠️ | 6 |
| **Total** | **43%** | **21.5/50** |

**Légende:** ✅ Terminée | ⚠️ Partielle | ❌ À faire | 🟨 En cours
