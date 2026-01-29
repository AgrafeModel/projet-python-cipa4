# Epic 6️⃣ : Paramètres Expérimentaux

**Description:** Système de configuration et manipulation de la plateforme

**Objectif:** Permettre aux humains de modifier les conditions de jeu

**Points d'effort estimés:** 35 points  
**Statut global:** ⬜ À faire (0% complété)

---

## User Stories

### ⬜ US-6.1 | Créer le gestionnaire de configuration de parties
**Points:** 5  
**Priorité:** 🟠 Haute  
**Statut:** ❌ À faire

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

**Notes:** SetupScreen permet de choisir le nombre de joueurs (base)

---

### ⬜ US-6.2 | Implémenter la modification des personnalités
**Points:** 5  
**Priorité:** 🟡 Moyenne  
**Statut:** ❌ À faire

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

**Notes:** Science comportementale - Optionnel pour MVP

---

### ⬜ US-6.3 | Implémenter l'injection d'événements
**Points:** 5  
**Priorité:** 🟡 Moyenne  
**Statut:** ❌ À faire

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

**Notes:** Tests de robustesse - Bonus

---

### ⬜ US-6.4 | Implémenter la configuration du bruit informationnel
**Points:** 4  
**Priorité:** 🟡 Moyenne  
**Statut:** ❌ À faire

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

**Notes:** Étude comportementale - Bonus

---

### ⬜ US-6.5 | Créer l'API de paramètrisation
**Points:** 6  
**Priorité:** 🟠 Haute  
**Statut:** ❌ À faire

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

**Notes:** Interface programmatique - Si version serveur implémentée

---

## Progression

| User Story | Statut | Points |
|------------|--------|--------|
| US-6.1 | ❌ | 5 |
| US-6.2 | ❌ | 5 |
| US-6.3 | ❌ | 5 |
| US-6.4 | ❌ | 4 |
| US-6.5 | ❌ | 6 |
| **Total** | **0%** | **0/35** |

**Légende:** ✅ Terminée | ⚠️ Partielle | ❌ À faire | ⬜ Non commencé

**Note:** Epic optionnel pour MVP - Focus sur fonctionnalités de base d'abord
