# 📷 photovinc

**Application de photomaton complète et moderne pour Raspberry Pi**

Une solution tout-en-un pour créer un photomaton DIY avec impression photo, partage QR code, synchronisation cloud et interface tactile optimisée.

---

## ✨ Fonctionnalités principales

### 📸 Capture Photo
- **Session 4 photos** avec compte à rebours visuel
- **Styles multiples** : Normal, Polaroid, Vintage, Timbre, Fête
- **Prévisualisation en direct** avec interface fullscreen tactile
- **Montage automatique** type planche contact

### 🖨️ Impression Intelligente
- **Détection automatique** d'imprimantes USB et réseau (IPP/IPPS)
- **Support multi-formats** : Postcard 10x15cm, autres formats personnalisables
- **Diagnostic avancé** avec solutions en temps réel
- **Gestion des jobs** : annulation, reset, monitoring
- **Compteur détaillé** : impressions par style, sessions, statistiques complètes

### 📱 Partage & Cloud
- **QR Code** : génération instantanée pour partage mobile
- **Serveur web intégré** : accès aux photos via réseau local
- **NextCloud** : synchronisation automatique optionnelle
- **Export ZIP** : téléchargement groupé avec QR code

### 🎨 Interface Utilisateur
- **Design moderne** : interface fullscreen tactile optimisée
- **Galerie photo** : visualisation avec scroll, actions rapides
- **Sélection intuitive** : choix photo avant impression
- **Configuration WiFi** : gestion réseau intégrée
- **Mode démo** : fonctionnement sans imprimante

---

## 🛠️ Architecture Technique

### Système de Plugins
Architecture modulaire avec plugins pour :
- **Caméra** : capture via libcamera/picamera2
- **Imprimante** : gestion CUPS avec support IPP
- **Décorateur** : styles et effets visuels
- **QR Code** : génération de codes de partage
- **NextCloud** : synchronisation cloud
- **WiFi** : configuration réseau
- **Clavier** : clavier virtuel tactile

### Détection d'Imprimante
```python
# Détection automatique avec profils compatibles
- Canon SELPHY CP1300, CP1500
- Canon Pixma (séries MG, TR, G)
- Epson PictureMate
- Autres imprimantes compatibles CUPS
```

### Compteur Avancé
- **Total impressions** avec suivi par style
- **Total photos** capturées par session
- **Statistiques détaillées** : sessions, tendances
- **Persistance JSON** avec backup automatique
- **Export CSV** pour analyse

---

## 📦 Installation

### Prérequis Système
```bash
# Raspberry Pi OS (Bullseye ou supérieur)
# Python 3.9+
# CUPS installé et configuré
```

### Installation Complète
```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/photovinc.git
cd photovinc

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Installer les dépendances système
sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    python3-pil \
    python3-cups \
    libcamera-apps \
    cups

# 4. Configurer CUPS
sudo usermod -a -G lpadmin $USER

# 5. Lancer l'application
python3 integration_complete.py
```

### Dépendances Python
```txt
Pillow>=10.0.0
qrcode[pil]>=7.4.0
requests>=2.31.0
python-cups>=2.0.0
picamera2  # Pour Raspberry Pi uniquement
```

---

## 🚀 Utilisation

### Démarrage Rapide
```bash
# Lancement standard
python3 integration_complete.py

# Mode debug
CUPS_DEBUG=1 python3 integration_complete.py
```

### Première Configuration

1. **Imprimante** : Détection automatique au démarrage
   - Si plusieurs imprimantes → sélection manuelle
   - Configuration CUPS si nécessaire

2. **WiFi** (optionnel) : Configuration via interface
   - SSID et mot de passe
   - Connexion automatique

3. **NextCloud** (optionnel) :
   - URL du serveur
   - Identifiants WebDAV
   - Dossier de destination

### Interface Principale

```
┌─────────────────────────────────────┐
│ PHOTOVINC    🖨️ 42  📷 168         │
├─────────────────────────────────────┤
│                                     │
│     [Prévisualisation Photo]        │
│                                     │
│                                     │
├─────────────────────────────────────┤
│  [Choix Style: Normal ▼]            │
│  [TEST PHOTO]                       │
│  [PRENDRE 4 PHOTOS]                 │
│  [GALERIE]                          │
│  ─────────────────────────────      │
│  [Diagnostic] [Annuler] [Reset]     │
│  [WiFi] [QR Code] [NextCloud]       │
└─────────────────────────────────────┘
```

---

## 📁 Structure du Projet

```
photovinc/
├── integration_complete.py      # Application principale
├── camera_printer_real.py       # Plugin caméra/imprimante
├── decorator_real.py            # Styles et effets
├── plugin_manager.py            # Gestionnaire de plugins
├── printer_detection.py         # Détection auto imprimante
├── print_counter_advanced.py    # Compteur avec stats
├── print_counter_ui.py          # Interface compteur
├── qr_code_plugin.py           # Génération QR codes
├── nextcloud_plugin.py         # Synchronisation cloud
├── nextcloud_ui.py             # Config NextCloud
├── photo_web_server.py         # Serveur HTTP local
├── wifi_config_ui.py           # Configuration WiFi
├── gallery_download.py         # Export ZIP galerie
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

---

## ⚙️ Configuration

### Fichiers de Configuration

#### `plugin_config.json`
```json
{
  "camera": {"enabled": true, "priority": 1},
  "printer": {"enabled": true, "priority": 2},
  "decorator": {"enabled": true, "priority": 3},
  "qrcode": {"enabled": true, "priority": 6},
  "nextcloud": {
    "enabled": true,
    "settings": {
      "url": "https://cloud.example.com",
      "username": "user",
      "password": "pass",
      "path": "/Photos/photovinc"
    }
  }
}
```

#### `print_counter.json`
```json
{
  "total_prints": 42,
  "total_photos": 168,
  "sessions": [
    {
      "timestamp": "2025-12-30T14:30:00",
      "photos": 4,
      "style": "polaroid"
    }
  ]
}
```

### Variables d'Environnement
```bash
# Activer le debug CUPS
export CUPS_DEBUG=1

# Changer le port du serveur web
export PHOTOVINC_PORT=8080

# Définir le dossier photos
export PHOTOVINC_PHOTO_DIR=/home/pi/Photos
```

---

## 🔧 Résolution de Problèmes

### Imprimante Non Détectée
```bash
# Vérifier CUPS
lpstat -p -d

# Lister les imprimantes
lpstat -a

# Redémarrer CUPS
sudo systemctl restart cups

# Tester l'impression
lp -d NOM_IMPRIMANTE test.jpg
```

### Caméra Non Reconnue
```bash
# Vérifier la caméra
libcamera-hello

# Permissions
sudo usermod -a -G video $USER

# Redémarrer
sudo reboot
```

### Erreurs d'Impression
1. **"Mauvais papier"** → Charger Postcard 10x15cm
2. **"Job bloqué"** → Cliquer "Annuler jobs"
3. **"Non connectée"** → Vérifier câble USB, cliquer "Reset"

### Serveur Web Inaccessible
```bash
# Vérifier le port
netstat -tuln | grep 8000

# Autoriser dans le pare-feu
sudo ufw allow 8000/tcp

# Tester localement
curl http://localhost:8000
```

---

## 🎯 Cas d'Usage

### Événements & Fêtes
- **Mariages** : photomaton pour invités
- **Anniversaires** : souvenirs instantanés
- **Festivals** : stand photo interactif

### Professionnel
- **Boutiques** : photos produits
- **Écoles** : portraits étudiants
- **Stands** : marketing événementiel

### Personnel
- **Famille** : souvenirs à la maison
- **Projets DIY** : apprentissage technique
- **Créativité** : expérimentation photo

---

## 🤝 Contribution

Les contributions sont les bienvenues !

```bash
# Fork le projet
# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Commit
git commit -m "Ajout de ma fonctionnalité"

# Push
git push origin feature/ma-fonctionnalite

# Créer une Pull Request
```

### Guidelines
- Code Python PEP 8
- Documentation des fonctions
- Tests unitaires pour nouvelles features
- Messages de commit descriptifs

---

## 📄 Licence

Ce projet est sous licence **Creative Commons** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

Vous êtes libre de :
- **Partager** : copier et redistribuer le matériel
- **Adapter** : remixer, transformer et créer à partir du matériel

Selon les conditions suivantes :
- **Attribution** : vous devez créditer l'œuvre
- **Partage dans les mêmes conditions** : sous la même licence

---

## 🙏 Remerciements

- **Raspberry Pi Foundation** pour le matériel
- **Pillow** pour le traitement d'images
- **CUPS** pour la gestion d'impression
- **Community** pour les retours et contributions

---

## 🗺️ Roadmap

### Version 2.0 (À venir)
- [ ] Support vidéo boomerang
- [ ] Filtres en temps réel
- [ ] Application mobile compagnon
- [ ] API REST publique
- [ ] Multi-langues (EN, ES, DE)

### Version 1.5 (En cours)
- [x] Compteur avancé avec statistiques
- [x] Export ZIP galerie
- [x] Détection auto imprimante
- [ ] Thèmes d'interface personnalisables
- [ ] Backup automatique cloud

---

**Made with ❤️ for makers & photo enthusiasts**

> ⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile sur GitHub !