# Epic 5️⃣ : Interface d'Observation Humaine

**Description:** Développement de l'interface web pour observer les parties

**Objectif:** Visualisation temps réel pour les observateurs

**Points d'effort estimés:** 40 points  
**Statut global:** 🟨 En cours (43% complété)

---

## User Stories

### ✅ US-5.1 | Créer le projet frontend React/Vue
**Points:** 4  
**Priorité:** 🔴 Critique  
**Statut:** ✅ Adaptée (Pygame)

**Description:**  
En tant que frontend developer, je veux initialiser un projet frontend pour l'interface d'observation.

**Critères d'acceptation:**
- [x] Projet créé (Pygame au lieu de React/Vue)
- [x] Connexion établie (locale)
- [x] Structure des composants
- [ ] Tests basiques

**Notes:** ✅ Interface Pygame implémentée dans gui/app.py - Version desktop au lieu de web

---

### ✅ US-5.2 | Implémenter la vue temps réel des messages
**Points:** 5  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que observateur, je veux voir les messages des agents en temps réel pour suivre les discussions.

**Critères d'acceptation:**
- [x] Messages affichés en temps réel
- [x] Auteur et rôle visibles
- [ ] Timestamp affiché
- [x] Scroll automatique
- [x] Design clair

**Notes:** ⚠️ ChatBox widget implémenté dans gui/widgets.py

---

### ⬜ US-5.3 | Implémenter l'affichage du graphe d'interactions
**Points:** 6  
**Priorité:** 🟠 Haute  
**Statut:** ❌ À faire

**Description:**  
En tant qu'analyseur, je veux voir un graphe des relations entre agents pour visualiser les alliances.

**Critères d'acceptation:**
- [ ] Graphe des agents visible
- [ ] Liens de confiance affichés
- [ ] Couleurs par alignement
- [ ] Interactif (zoom, drag)
- [ ] Design propre

**Tâches:**
- Utiliser une lib de graphe (pygame, networkx)
- Créer le composant
- Tests

**Notes:** Bonus si implémenté

---

### ✅ US-5.4 | Implémenter la timeline jour/nuit
**Points:** 5  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant qu'observateur, je veux voir la timeline jour/nuit pour suivre la progression du jeu.

**Critères d'acceptation:**
- [x] Timeline visuelle jour/nuit
- [x] Phase actuelle mise en évidence
- [ ] Actions de la nuit résumées
- [x] Tour numéroté

**Notes:** ⚠️ Info panel dans GameScreen avec day_count et phase

---

### ✅ US-5.5 | Implémenter l'historique des votes
**Points:** 5  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant qu'analyseur, je veux voir l'historique des votes pour analyser les patterns de vote.

**Critères d'acceptation:**
- [x] Tableau des votes
- [x] Qui a voté pour qui
- [ ] Résultats par tour
- [ ] Statistiques simples

**Notes:** ⚠️ VoteScreen implémenté dans gui/screens.py

---

### ⬜ US-5.6 | Implémenter la heatmap des accusations
**Points:** 6  
**Priorité:** 🟡 Moyenne  
**Statut:** ❌ À faire

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

**Notes:** Bonus points - Visualisation avancée

---

### ✅ US-5.7 | Créer le layout principal de l'interface
**Points:** 4  
**Priorité:** 🔴 Critique  
**Statut:** ✅ Terminée

**Description:**  
En tant que UX designer, je veux créer un layout propre pour assembler tous les composants.

**Critères d'acceptation:**
- [x] Layout responsive
- [x] Dashboard cohérent
- [x] Navigation claire
- [x] Design professionnel
- [ ] Mobile-friendly bonus

**Notes:** ✅ SetupScreen et GameScreen avec layout structuré

---

## Progression

| User Story | Statut | Points |
|------------|--------|--------|
| US-5.1 | ✅ | 4 |
| US-5.2 | ⚠️ | 5 |
| US-5.3 | ❌ | 6 |
| US-5.4 | ⚠️ | 5 |
| US-5.5 | ⚠️ | 5 |
| US-5.6 | ❌ | 6 |
| US-5.7 | ✅ | 4 |
| **Total** | **43%** | **17/40** |

**Légende:** ✅ Terminée | ⚠️ Partielle | ❌ À faire | 🟨 En cours

**Note:** Interface Pygame desktop au lieu de web React/Vue - Adaptation technique valide
