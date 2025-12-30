#!/bin/bash
# Script de lancement du photovinc
# Permet de choisir entre mode normal et mode démo
# Démarrer le clavier virtuel
onboard &

# Activer l'environnement virtuel
source ~/mon_env/bin/activate
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logo
echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════╗
║                                               ║
║           📸  PHOTOVINC  📸                  ║
║                                               ║
║        Application Modulaire v2.0             ║
║                                               ║
╚═══════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Fonction d'affichage de menu
show_menu() {
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Choisissez un mode de démarrage :${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} Mode NORMAL   - Avec caméra et imprimante réelles"
    echo -e "  ${YELLOW}2)${NC} Mode DEMO     - Sans matériel (simulation)"
    echo -e "  ${BLUE}3)${NC} Vérifier les dépendances"
    echo -e "  ${PURPLE}4)${NC} Configuration WiFi"
    echo -e "  ${RED}5)${NC} Quitter"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
}

# Vérification des dépendances
check_dependencies() {
    echo -e "${YELLOW}Vérification des dépendances...${NC}"
    echo ""
    
    # Python 3
    if command -v python3 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Python 3 : $(python3 --version)"
    else
        echo -e "  ${RED}✗${NC} Python 3 : NON INSTALLÉ"
    fi
    
    # PIL/Pillow
    if python3 -c "import PIL" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} PIL/Pillow : Installé"
    else
        echo -e "  ${RED}✗${NC} PIL/Pillow : Manquant (sudo apt install python3-pil)"
    fi
    
    # Tkinter
    if python3 -c "import tkinter" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Tkinter : Installé"
    else
        echo -e "  ${RED}✗${NC} Tkinter : Manquant (sudo apt install python3-tk)"
    fi
    
    # QR Code
    if python3 -c "import qrcode" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} QRCode : Installé"
    else
        echo -e "  ${YELLOW}⚠${NC} QRCode : Manquant (pip install qrcode[pil])"
    fi
    
    # gphoto2 (mode normal uniquement)
    if command -v gphoto2 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} gphoto2 : Installé"
    else
        echo -e "  ${YELLOW}⚠${NC} gphoto2 : Manquant (sudo apt install gphoto2)"
    fi
    
    # CUPS
    if command -v lpstat &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} CUPS : Installé"
    else
        echo -e "  ${YELLOW}⚠${NC} CUPS : Manquant (sudo apt install cups)"
    fi
    
    # NetworkManager
    if command -v nmcli &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} NetworkManager : Installé"
    else
        echo -e "  ${YELLOW}⚠${NC} NetworkManager : Manquant (sudo apt install network-manager)"
    fi
    
    echo ""
    echo -e "${BLUE}Note:${NC} En mode DEMO, seuls Python, PIL et Tkinter sont requis."
    echo ""
}

# Configuration WiFi
configure_wifi() {
    echo -e "${BLUE}Lancement de la configuration WiFi...${NC}"
    python3 "$SCRIPT_DIR/integration_complete.py" --wifi-only
}

# Lancement en mode normal
launch_normal() {
    echo -e "${GREEN}Démarrage en mode NORMAL...${NC}"
    echo ""
    
    # Vérifier les dépendances critiques
    if ! python3 -c "import PIL, tkinter" 2>/dev/null; then
        echo -e "${RED}ERREUR: Dépendances manquantes !${NC}"
        echo "Installez: sudo apt install python3-pil python3-tk"
        return 1
    fi
    
    if ! command -v gphoto2 &> /dev/null; then
        echo -e "${YELLOW}ATTENTION: gphoto2 non installé !${NC}"
        echo "La caméra ne fonctionnera pas."
        read -p "Continuer quand même ? (o/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Oo]$ ]]; then
            return 1
        fi
    fi
    
    cd "$SCRIPT_DIR"
    python3 integration_complete.py
}

# Lancement en mode démo
launch_demo() {
    echo -e "${YELLOW}Démarrage en mode DEMO...${NC}"
    echo ""
    echo -e "${BLUE}ℹ${NC}  Mode démonstration activé"
    echo -e "   • Caméra simulée (génère des images de test)"
    echo -e "   • Imprimante simulée (pas d'impression réelle)"
    echo -e "   • Serveur web actif pour les QR codes"
    echo ""
    
    # Vérifier les dépendances minimales
    if ! python3 -c "import PIL, tkinter" 2>/dev/null; then
        echo -e "${RED}ERREUR: Dépendances manquantes !${NC}"
        echo "Installez: sudo apt install python3-pil python3-tk"
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    python3 integration_complete.py --demo
}

# Menu principal
while true; do
    show_menu
    read -p "Votre choix : " choice
    echo ""
    
    case $choice in
        1)
            launch_normal
            break
            ;;
        2)
            launch_demo
            break
            ;;
        3)
            check_dependencies
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        4)
            configure_wifi
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        5)
            echo -e "${BLUE}Au revoir !${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Choix invalide. Réessayez.${NC}"
            sleep 1
            ;;
    esac
    
    clear
done
