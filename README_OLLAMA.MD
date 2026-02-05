
## Installation d'Ollama

### Sur Windows

1. **Téléchargement**
   - Rendez-vous sur le site officiel : https://ollama.ai
   - Cliquez sur "Download for Windows"
   - Téléchargez le fichier `OllamaSetup.exe`

2. **Installation**
   - Exécutez le fichier `OllamaSetup.exe` en tant qu'administrateur
   - Suivez les instructions de l'assistant d'installation
   - Choisissez le répertoire d'installation (par défaut : `C:\Program Files\Ollama`)
   - Terminez l'installation

3. **Vérification de l'installation**
   - Ouvrez une invite de commandes (cmd) ou PowerShell
   - Tapez `ollama --version` pour vérifier que l'installation s'est bien déroulée

### Sur PC Linux/macOS

1. **Installation via script (Recommandé)**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Installation manuelle**
   - Téléchargez le binaire depuis https://ollama.ai/download
   - Placez-le dans votre PATH système
   - Rendez-le exécutable : `chmod +x ollama`

## Installation du modèle Mistral

Une fois Ollama installé, vous devez télécharger le modèle Mistral :

1. **Ouverture du terminal/invite de commandes**
   - Windows : Ouvrez cmd ou PowerShell
   - Linux/macOS : Ouvrez un terminal

2. **Téléchargement de Mistral**
   ```bash
   ollama pull mistral
   ```
   
   Cette commande va télécharger le modèle Mistral (environ 4 GB). Le téléchargement peut prendre quelques minutes selon votre connexion internet.

3. **Vérification du téléchargement**
   ```bash
   ollama list
   ```
   
   Vous devriez voir "mistral" dans la liste des modèles disponibles.

## Test rapide de l'installation

Pour vérifier que tout fonctionne correctement :

1. **Test de base d'Ollama**
   ```bash
   ollama --version
   ```
   Doit afficher la version installée.

2. **Test du modèle Mistral**
   ```bash
   ollama run mistral "Bonjour, peux-tu me dire comment tu vas ?"
   ```
   
   Le modèle devrait répondre en français. Si c'est le cas, l'installation est réussie.

3. **Test interactif**
   ```bash
   ollama run mistral
   ```
   
   Cela lance une session interactive. Vous pouvez poser des questions directement. Pour quitter, tapez `/bye` ou utilisez `Ctrl+C`.

## Dépannage courant

### Problèmes Windows
- Si la commande `ollama` n'est pas reconnue, redémarrez votre invite de commandes ou ajoutez manuellement le chemin d'installation à votre variable PATH
- Assurez-vous d'avoir les droits administrateur lors de l'installation

### Problèmes généraux
- Vérifiez votre connexion internet lors du téléchargement des modèles
- Assurez-vous d'avoir suffisamment d'espace disque (au moins 8 GB libres)
- Si le téléchargement échoue, relancez la commande `ollama pull mistral`

### Performance
- Ollama fonctionne mieux avec au moins 8 GB de RAM
- Un processeur récent améliore significativement les performances
- L'utilisation d'un SSD accélère le chargement des modèles

## Utilisation dans le projet

Une fois Ollama configuré avec Mistral, vous pourrez utiliser les fonctionnalités d'IA du projet. Le modèle sera accessible localement sans nécessiter de connexion internet pour les inférences.