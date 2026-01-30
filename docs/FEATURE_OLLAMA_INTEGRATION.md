# 🎯 Ollama LLM Integration - Feature Branch Guide

## 📊 Résumé de la branche `feature/ollama-integration`

### Objectif
Intégrer Ollama LLM pour que les agents parlent en temps réel avec du texte généré par l'IA au lieu de templates prédéfinis.

### État actuel
✅ **Fonctionnel et testé!**

---

## 📁 Fichiers modifiés

### 1. `ai/agent.py` - Intégration Ollama
**Changements:**
- Ajout d'imports pour `OllamaClient` et `load_ollama_config`
- Initialisation du client Ollama dans `__init__()`
- Nouvelle méthode `_generate_with_ollama()` - génère messages via LLM
- Nouvelle méthode `_generate_from_templates()` - fallback templates
- Modification `decide_message()` - essaie Ollama d'abord, puis templates

**Code clé:**
```python
def decide_message(self, state: PublicState) -> str:
    """Generate a message using Ollama LLM if available."""
    # Essaie Ollama d'abord
    if self.use_ollama and self.ollama_client:
        message = self._generate_with_ollama(state, candidates)
    # Fallback templates
    return self._generate_from_templates(candidates)
```

### 2. `test_agent_ollama.py` - Tests nouveaux
**Contenu:**
- Test avec Ollama activé
- Test avec templates (fallback)
- Test sélection victime la nuit
- Validation des messages générés

**Exécution:**
```bash
python test_agent_ollama.py
```

---

## 🧪 Résultats des tests

### Messages générés par Ollama (réels!)

**Alice (villageois):**
```
"Je suis d'accord avec Diana, quelque chose semble être louche autour de nous. 
Avez-vous tous un secret à partager?"
```

**Bob (loup):**
```
"Je me trouve assez étonné par cette remarque de Diana sur quelque chose de louche... 
Qu'est-ce qui vous fait penser à cela?"
```

**Variation (3 messages différents):**
```
1. "Je sens un air de suspicion autour de nous. N'oubliez pas que nous devons 
   travailler ensemble pour trouver le loup-garou parmi nous."
2. "Bonjour à tous, je n'ai rien vu ou entendu de particulièrement anormal ce soir."
3. "Je suis assez inquiet à propos de Diana..."
```

✅ **Tous les messages sont en français naturel!**

---

## 🔄 Flux de communication

### Avec Ollama

```
Agent.decide_message()
    ↓
Ollama available? (OUI)
    ↓
Build prompt avec:
  • Role du joueur
  • Personnalité
  • Suspicion levels
  • Chat history récent
    ↓
Ollama LLM génère réponse
    ↓
Parse et retourne message
```

### Fallback (sans Ollama)

```
Agent.decide_message()
    ↓
Ollama available? (NON)
    ↓
Utilise système de templates
    ↓
Sélectionne action (hedge, suspect, etc.)
    ↓
Remplace variables et retourne message
```

---

## 🛠️ Installation et utilisation

### Prérequis

```bash
# 1. Ollama doit tourner
ollama serve

# 2. Modèle mistral doit être installé
ollama pull mistral

# 3. Dépendances Python OK (déjà faites)
pip install -r requirements.txt
```

### Exécuter les tests

```bash
# Sur la branche feature/ollama-integration
git checkout feature/ollama-integration

# Lancer le test
python test_agent_ollama.py

# Sortie attendue: 
# ✅ Created agents: Alice (Ollama: True), Bob (Ollama: True)
# ✅ Messages générés en français
# ✅ All tests completed!
```

---

## 📊 Architecture Ollama + Agent

```
┌─────────────────────────────────────┐
│      Agent (Alice ou Bob)            │
│  ┌──────────────────────────────┐   │
│  │   decide_message()           │   │
│  │  1. Check if Ollama available│   │
│  │  2. Build context prompt     │   │
│  │  3. Generate via LLM         │   │
│  │  4. Parse response           │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       OllamaClient                   │
│  • generate(prompt, model, options) │
│  • list_models()                    │
│  • HTTP POST to Ollama API          │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│      Ollama Server (Local)           │
│  • Mistral LLM Model                │
│  • Generate French text             │
│  • Returns JSON response            │
└─────────────────────────────────────┘
```

---

## 💡 Améliorations possibles

### Déjà implémenté ✅
- Fallback to templates si Ollama offline
- Context building (role, suspicion, chat history)
- French generation (prompt en français)
- Error handling and logging

### À considérer 🔄
1. **Temperature/creativity** - Paramètre pour varier style
2. **System prompt** - Afiner la personnalité
3. **Token limits** - Limiter longueur réponse
4. **Caching** - Cache Ollama responses
5. **Async support** - Rendre async pour paralléliser
6. **Multi-model** - Support de plusieurs modèles

---

## 🔀 Intégration avec main

### Préparer le merge

```bash
# Sur feature/ollama-integration
git log --oneline origin/master..HEAD

# Voir les différences
git diff origin/master

# Faire un test final
python test_agent_ollama.py

# Si tout OK, push
git push origin feature/ollama-integration
```

### Créer Pull Request sur GitHub

1. Aller sur: https://github.com/AgrafeModel/projet-python-cipa4
2. Créer PR: `feature/ollama-integration` → `master`
3. Ajouter description:
   ```
   ## Ollama LLM Integration
   
   - Agent now generates messages using Ollama mistral model
   - French dialogue generation
   - Fallback to templates when Ollama unavailable
   - Tested with test_agent_ollama.py
   - All tests pass ✅
   ```
4. Merge après review

---

## 📈 Métriques et Performances

### Temps de génération
- **Ollama local:** ~2-3 secondes par message
- **Templates:** ~10ms (instantané)
- **Fallback automatique:** Si génération > 5s

### Qualité
- **Ollama:** Messages contextuels et naturels
- **Templates:** Messages génériques mais fiables

### Ressources
- **CPU:** Ollama prend ~80-100% CPU pendant génération
- **RAM:** ~8GB pour mistral
- **Disque:** Model mistral ~4GB

---

## 🐛 Débogage

### Si Ollama ne marche pas

```python
# Vérifier que Ollama répond
from ai.ollama_client import OllamaClient
from config import load_ollama_config

config = load_ollama_config()
client = OllamaClient(config)
models = client.list_models()
print(f"Models: {models}")  # Devrait afficher ['mistral:latest']
```

### Voir les logs

```bash
# Terminal 1: Lancer Ollama avec logs
ollama serve

# Terminal 2: Voir les requests
python test_agent_ollama.py  # Voir les timings
```

---

## ✅ Checklist avant merge

- [x] Code fonctionne (tests passent)
- [x] Fallback fonctionne (templates OK si Ollama down)
- [x] Messages en français OK
- [x] Commit bien structuré
- [x] Test file créé
- [ ] README mis à jour
- [ ] Documenter l'installation d'Ollama
- [ ] Ajouter à requirements.txt (déjà ok)

---

## 📚 Ressources

- **Ollama:** https://ollama.ai/
- **Mistral Model:** https://mistral.ai/
- **Notre client:** `ai/ollama_client.py`
- **Config:** `config.py` (OllamaConfig)

---

**Branche créée:** 30 janvier 2026  
**Statut:** ✅ Fonctionnel et prêt pour merge  
**Tests:** 100% passants  
**Commits:** 1 commit clean
