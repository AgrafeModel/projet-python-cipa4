# Projet Python - Groupe 10

**Editeurs**

- Brieuc JOONNEKINDT : OnWix
- Corentin DEGUISNE : AgrafeModel
- Matheo BERTIN : matheo6209
- Matteo GISLOT : chr8n8s
- Amaury AMRANI : dansunavion

# Commandes utiles

**Env python (Windows - PowerShell)** : 

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Env python (macOS/Linux - Bash/Zsh)** :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

source .venv/bin/activate #pour lancer l'environnement
```

# Installation Ollama

## Installer mistral

dans un premier terminal `ollama serve` pour lancer ollama. Puis dans un second `ollama pull mistral` pour télécharger le modèle de mistral

a tester : ministral

# Guide Gemini API - Installation & Utilisation

## Obtention de la clé API Gemini (gratuite)

### Créer la clé

1. Rendez-vous sur : **https://aistudio.google.com/apikey**
2. Connectez-vous avec votre compte Google
3. Cliquez sur **"Create API Key"**
4. Copiez la clé générée (format : `AIzaSy...`)

**Important** : Cette clé est secrète et n accepte pas d être partagée
-> Erreur Gemini: 403 Your API key was reported as leaked. Please use another API key.

### Limites

- **15 requêtes par minute**
- **1 500 requêtes par jour**
- **Gratuit à vie**

---

## Où placer la clé API

La clé doit être placée dans le fichier constents.py dans la variable suivante :
API_GEMINI = 'nom_de_la_clé'

## Appeler l'IA dans un code

```python
# 1. Installer la bibliothèque
pip install google-generativeai
(cf. requierments.txt)

# 2. Dans votre code Python
import google.generativeai as genai

# 3. Configurer avec votre clé
genai.configure(api_key="nom_de_la_clé")

# 4. Créer un modèle
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 5. Générer du texte
response = model.generate_content("Écris une phrase en français")

# 6. Récupérer la réponse
print(response.text)
```

### Exemple pour le projet

```python
import google.generativeai as genai

# Configuration
genai.configure(api_key="nom_de_la_clé")
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Créer le prompt (les instructions pour l'IA)
prompt = """
Tu génères une discussion de Loup-Garou.

Joueurs vivants : Marc (loup), Sophie (villageois), Luc (villageois)

Génère 3 messages de discussion au format "Nom: texte".

Exemple :
Marc: Je trouve Sophie suspecte.
Sophie: Marc, pourquoi tu dis ça ?
Luc: Perso, je pense qu'on devrait observer plus.

Génère la discussion :
"""

# Envoyer à l'IA
response = model.generate_content(prompt)

# Récupérer la réponse
discussion = response.text

# Afficher
print(discussion)
```

**Résultat :**
```
Marc: Franchement, Sophie pose trop de questions, ça me dérange.
Sophie: Marc, je cherche juste à comprendre qui est suspect.
Luc: Je suis d accord avec Sophie, elle a raison de poser des questions.
```

### Paramètres avancés

```python
# Contrôler la créativité
generation_config = {
    'temperature': 0.9,      # 0.0 = prévisible, 2.0 = très créatif
    'top_p': 0.95,           # Diversité des mots choisis
    'top_k': 40,             # Nombre de choix considérés
    'max_output_tokens': 2048  # Longueur max de la réponse
}

response = model.generate_content(
    prompt,
    generation_config=generation_config
)
```

### Gestion des erreurs

```python
try:
    response = model.generate_content(prompt)
    texte = response.text
    
except Exception as e:
    print(f"Erreur : {e}")
    # Utiliser un texte par défaut
    texte = "Erreur de génération, utilisation du mode fallback."
```

### Erreurs fréquentes

#### "API key not valid"
-> Vérifiez que la clé commence par `AIzaSy`  
-> Copiez-collez à nouveau sans espaces  
-> Générez une nouvelle clé si nécessaire

#### "ModuleNotFoundError: No module named 'google.generativeai'"
-> `pip install google-generativeai`

#### "Pas de clé API Gemini fournie"
-> Vérifiez la variable

#### "Resource exhausted"
-> Quota dépassé (15 req/min ou 1500 req/jour)  
-> Attendez 1 minute ou le lendemain  
-> Le jeu continuera en mode fallback automatiquement

#### "Autre"
-> Essayez de changer de modèle : https://ai.google.dev/gemini-api/docs/models

---

## Fonctionnement dans le projet

```
1. Le jeu démarre un nouveau jour
         ↓
2. engine.py appelle _generate_day_discussion()
         ↓
3. Construction du prompt avec :
   - Liste des joueurs vivants
   - Rôles secrets (loup/villageois)
   - Historique des conversations
   - Instructions de format
         ↓
4. Envoi à Gemini via l API
         ↓
5. Gemini génère toute la discussion
         ↓
6. Le code parse la réponse (ligne par ligne)
         ↓
7. Chaque message est affiché dans le chat
         ↓
8. Les joueurs peuvent voter
```

---

### Test d'installation

```python
import google.generativeai as genai
import os

# Récupérer la clé
api_key = "nom_de_la_clé"

if not api_key:
    print("Clé API non trouvée")
    print("Définissez : export GEMINI_API_KEY='nom_de_la_clé'")
else:
    print(f"Clé trouvée : {api_key[:10]}...")
    
    # Tester l'API
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content("Dis simplement 'Bonjour' en français.")
        
        print("API fonctionne !")
        print(f"Réponse : {response.text}")
        
    except Exception as e:
        print(f"Erreur : {e}")
```

---

## Ressources

- **Obtenir une clé** : https://aistudio.google.com/apikey
- **Documentation Gemini** : https://ai.google.dev/gemini-api/docs
- **Exemples de code** : https://ai.google.dev/gemini-api/docs/get-started
- **Modèles disponibles** : https://ai.google.dev/gemini-api/docs/models