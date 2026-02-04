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

## Environnement

Avant de lancer le projet, il est nécessaire d'installer les dépendances du projet. Pour cela, il suffit de suivre les instructions ci-dessus pour créer un environnement virtuel et installer les dépendances à partir du fichier `requirements.txt`.

Il est aussi nécéssaire de crée un fichier `.env` à la racine du projet avec les variables d'environnement suivantes, présente dans le fichier `.env.example` :

```env
OPENROUTER_API_KEY=XXXXXX-XXXXXX-XXXXXX
```
