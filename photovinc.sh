#!/bin/bash
source ~/mon_env/bin/activate

# Configuration des chemins
VENV_PATH="$HOME/photovinc/mon_env"
APP_PATH="$HOME/photovinc"

# Log
LOG_FILE="$HOME/photovinc/photovinc.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Démarrage du photovinc..."

# Vérifier l'environnement virtuel
if [ ! -d "$VENV_PATH" ]; then
    echo "ERREUR: Environnement virtuel introuvable: $VENV_PATH"
    exit 1
fi

# Activer l'environnement virtuel
source "$VENV_PATH/bin/activate"

# Vérifier que Python est disponible
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python3 introuvable"
    exit 1
fi

# Afficher la version Python
echo "Python: $(python3 --version)"
echo "Environnement: $VIRTUAL_ENV"

# Aller dans le dossier de l'application
cd "$APP_PATH" || exit 1

# Attendre que X11 soit prêt (important pour le démarrage automatique)
if [ -n "$DISPLAY" ]; then
    echo "Display: $DISPLAY"
else
    export DISPLAY=:0
    echo "Display défini sur :0"
fi

# Attendre 2 secondes que l'environnement graphique soit prêt
sleep 2

# Lancer l'application
echo "Lancement de integration_complete.py..."
python3 integration_complete.py "$@"

# Code de sortie
EXIT_CODE=$?
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Application terminée avec le code: $EXIT_CODE"

exit $EXIT_CODE
