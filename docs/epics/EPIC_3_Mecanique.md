# Epic 3️⃣ : Mécanique du Jeu

**Description:** Implémentation des règles du Loup-Garou

**Objectif:** Un jeu fonctionnel avec cycles jour/nuit et votes

**Points d'effort estimés:** 45 points  
**Statut global:** 🟨 En cours (57% complété)

---

## User Stories

### ✅ US-3.1 | Créer le gestionnaire de parties
**Points:** 6  
**Priorité:** 🔴 Critique  
**Statut:** ✅ Terminée

**Description:**  
En tant que game designer, je veux créer un gestionnaire de parties pour orchestrer le flux du jeu.

**Critères d'acceptation:**
- [x] Création de nouvelles parties
- [x] Attribution aléatoire des rôles
- [x] Gestion de l'état global
- [x] Passage des phases
- [x] Fin de partie détectée

**Notes:** ✅ GameEngine complet dans game/engine.py

---

### ✅ US-3.2 | Implémenter le système de rôles
**Points:** 6  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que game designer, je veux implémenter les 3 rôles MVP pour que le jeu soit jouable.

**Critères d'acceptation:**
- [x] Rôle Loup-Garou avec pouvoirs
- [x] Rôle Villageois simple
- [ ] Rôle Voyante avec observation
- [x] Règles de chaque rôle
- [ ] Tests unitaires

**Notes:** ⚠️ Loups et Villageois implémentés, Voyante manquante

---

### ✅ US-3.3 | Implémenter la phase nuit
**Points:** 6  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que game designer, je veux implémenter la phase nuit pour que les loups et voyante puissent agir.

**Critères d'acceptation:**
- [x] Loups choisissent une victime
- [ ] Voyante observe un agent
- [x] Actions exécutées secrètement
- [x] Messages système générés
- [ ] Tests

**Notes:** ⚠️ _last_night_victim visible dans engine.py, système de nuit partiel

---

### ✅ US-3.4 | Implémenter la phase jour
**Points:** 7  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que game designer, je veux implémenter la phase jour pour que tous les agents débattent et votent.

**Critères d'acceptation:**
- [x] Discussion libre entre agents
- [x] Chaque agent peut parler
- [x] Temps de parole respecté
- [x] Vote lancé à la fin
- [x] Messages publics visibles

**Notes:** ⚠️ Phase "JourDiscussion" implémentée, public_chat_history présent

---

### ✅ US-3.5 | Implémenter le système de vote
**Points:** 5  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que game designer, je veux implémenter un système de vote pour éliminer les agents par majorité.

**Critères d'acceptation:**
- [x] Chaque agent vote
- [x] Majorité simple appliquée
- [x] Résultats annoncés
- [ ] Égalités gérées
- [ ] Tests

**Notes:** ⚠️ Système de vote visible dans screens.py avec VoteScreen

---

### ⬜ US-3.6 | Implémenter les conditions de fin
**Points:** 4  
**Priorité:** 🟠 Haute  
**Statut:** ⚠️ Partielle

**Description:**  
En tant que game designer, je veux vérifier les conditions de victoire/défaite pour terminer le jeu correctement.

**Critères d'acceptation:**
- [x] Village gagne si tous loups morts
- [x] Loups gagnent si égalité
- [x] Fin détectée automatiquement
- [ ] Statistiques finales calculées
- [ ] Tests

**Notes:** ⚠️ Logique de fin visible dans engine.py (found_wolves_names)

---

### ✅ US-3.7 | Intégrer les phases au GameEngine
**Points:** 5  
**Priorité:** 🔴 Critique  
**Statut:** ⚠️ Partielle

**Description:**  
En tant qu'architecte, je veux intégrer toutes les phases pour que le jeu boucle correctement.

**Critères d'acceptation:**
- [x] Phases alternent (nuit → jour → nuit)
- [x] Transitions lisses
- [x] États cohérents
- [ ] Gestion d'erreurs
- [ ] Tests d'intégration

**Notes:** ⚠️ Phases implémentées mais pas de tests d'intégration

---

## Progression

| User Story | Statut | Points |
|------------|--------|--------|
| US-3.1 | ✅ | 6 |
| US-3.2 | ⚠️ | 6 |
| US-3.3 | ⚠️ | 6 |
| US-3.4 | ⚠️ | 7 |
| US-3.5 | ⚠️ | 5 |
| US-3.6 | ⚠️ | 4 |
| US-3.7 | ⚠️ | 5 |
| **Total** | **57%** | **25.5/45** |

**Légende:** ✅ Terminée | ⚠️ Partielle | ❌ À faire | 🟨 En cours
