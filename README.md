# 📷 photovinc

**Application de photomaton complète et moderne pour Raspberry Pi**

Une solution tout-en-un pour créer un photomaton DIY avec impression photo, partage QR code, synchronisation cloud et interface tactile optimisée.

---

## ✨ Fonctionnalités principales

### 📸 Capture Photo
- **Session photos flexible** : jusqu'à 4 photos avec validation après chaque prise
- **Validation individuelle** : enregistrer, refaire ou annuler chaque photo
- **Styles multiples** : Normal, Polaroid, Vintage, Timbre, Fête
- **Prévisualisation en direct** avec interface fullscreen tactile
- **Montage automatique** type planche contact
- **Création de montages personnalisés** : sélection de 4 photos depuis la galerie

### 🖨️ Impression Intelligente
- **Détection automatique** d'imprimantes USB et réseau (IPP/IPPS)
- **Support multi-protocoles** : IPP pour réseau, USB classique pour connexions directes
- **Support multi-formats** : Postcard 10x15cm, autres formats personnalisables
- **Diagnostic avancé** avec solutions en temps réel
- **Gestion des jobs** : annulation, reset, monitoring
- **Compteur détaillé** : impressions par style, sessions, statistiques complètes
- **Impression depuis galerie** : impression individuelle ou par lot

### 📱 Partage & Cloud
- **QR Code** : génération instantanée pour partage mobile
- **Export ZIP avec QR** : téléchargement groupé de toute la galerie via QR code
- **Serveur web intégré** : accès aux photos via réseau local
- **NextCloud** : synchronisation automatique optionnelle
- **Gestion automatique** : nettoyage des archives ZIP expirées

### 🎨 Interface Utilisateur
- **Design moderne** : interface fullscreen tactile optimisée
- **Galerie enrichie** : visualisation avec scroll, actions rapides, création de montages
- **Sélection intuitive** : choix photo avant impression avec prévisualisation
- **Validation interactive** : confirmation après chaque photo capturée
- **Configuration WiFi** : gestion réseau intégrée
- **Mode démo** : fonctionnement sans imprimante

---

## 🛠️ Architecture Technique

### Système de Plugins
Architecture modulaire avec plugins pour :
- **Caméra** : capture via libcamera/picamera2
- **Imprimante** : gestion CUPS avec support IPP et USB
- **Décorateur** : styles et effets visuels
- **QR Code** : génération de codes de partage
- **NextCloud** : synchronisation cloud
- **WiFi** : configuration réseau
- **Clavier** : clavier virtuel tactile

### Détection d'Imprimante Avancée
```python
# Détection automatique avec profils compatibles
- Canon SELPHY CP1300, CP1500 (USB et réseau IPP/IPPS)
- Canon Pixma (séries MG, TR, G)
- Epson PictureMate
- Support intelligent : IPP pour réseau, USB classique sinon
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
   - Détection USB et réseau (IPP/IPPS)
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
┌─────────────────────────────────┐
│ PHOTOVINC    🖨️ 42  📷 168       │
├─────────────────────────────────┤
│                                 │
│     [Prévisualisation Photo]    │
│                                 │
│                                 │
├─────────────────────────────────┤
│  [Choix Style: Normal ▼]        │
│  [TEST PHOTO]                   │
│  [PRENDRE 4 PHOTOS]             │
│  [GALERIE]                      │
│  ─────────────────────────────  │
│  [Diagnostic] [Annuler] [Reset] │
│  [WiFi] [QR Code] [NextCloud]   │
└─────────────────────────────────┘
```

### Workflow de Capture
1. Sélectionner un style
2. Cliquer "PRENDRE 4 PHOTOS"
3. Compte à rebours 3-2-1
4. **NOUVEAU** : Après chaque photo, choisir :
   - ✓ ENREGISTRER : conserver la photo
   - ↻ REFAIRE : reprendre la même photo
   - ✗ ANNULER SESSION : tout abandonner
5. Continuer jusqu'à 4 photos ou arrêter avant
6. Sélectionner une photo pour impression ou QR code

### Fonctionnalités Galerie
- **Visualisation** : miniatures avec scroll
- **Actions par photo** : Imprimer, QR Code, Supprimer
- **Création de montage** : sélectionner 4 photos pour un montage personnalisé
- **Export ZIP** : télécharger toutes les photos avec QR code mobile
- **Gestion automatique** : archives expirées supprimées après 1 heure (paramétrable)

---

## 📁 Structure du Projet

```
photovinc/
├── integration_complete.py      # Application principale avec nouvelles features
├── camera_printer_real.py       # Plugin caméra/imprimante
├── decorator_real.py            # Styles et effets
├── plugin_manager.py            # Gestionnaire de plugins
├── printer_detection.py         # Détection auto imprimante (USB + IPP)
├── print_counter_advanced.py    # Compteur avec stats
├── print_counter_ui.py          # Interface compteur
├── qr_code_plugin.py           # Génération QR codes
├── nextcloud_plugin.py         # Synchronisation cloud
├── nextcloud_ui.py             # Config NextCloud
├── photo_web_server.py         # Serveur HTTP local
├── wifi_config_ui.py           # Configuration WiFi
├── gallery_download.py         # Export ZIP galerie avec QR
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

### Configuration Export ZIP
- **Durée de vie par défaut** : 60 minutes
- **Nettoyage automatique** : toutes les 10 minutes
- **Archives conservées** : 3 dernières lors du nettoyage
- **Paramétrable** : via l'interface (30 min à 6 heures)

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
3. **"Non connectée"** → Vérifier câble USB/réseau, cliquer "Reset"
4. **Impression lente** → Si IPP : normal pour grandes images, utiliser USB si possible

### Serveur Web Inaccessible
```bash
# Vérifier le port
netstat -tuln | grep 8000

# Autoriser dans le pare-feu
sudo ufw allow 8000/tcp

# Tester localement
curl http://localhost:8000
```

### Archives ZIP Expirées
- Les archives sont automatiquement supprimées après expiration (défaut : 1h)
- Modifier la durée dans l'interface (Galerie → Télécharger ZIP → Paramètres)
- Nettoyage manuel disponible dans les paramètres

---

## 🎯 Cas d'Usage

### Événements & Fêtes
- **Mariages** : photomaton pour invités avec validation instantanée
- **Anniversaires** : souvenirs instantanés, export ZIP pour tous les invités
- **Festivals** : stand photo interactif avec QR codes

### Professionnel
- **Boutiques** : photos produits avec validation qualité
- **Écoles** : portraits étudiants avec statistiques de production
- **Stands** : marketing événementiel avec partage mobile

### Personnel
- **Famille** : souvenirs à la maison avec galerie organisée
- **Projets DIY** : apprentissage technique Raspberry Pi
- **Créativité** : expérimentation photo avec montages personnalisés

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

### Version 2.0 (Prochainement)
- [ ] Support vidéo boomerang
- [ ] Filtres en temps réel
- [ ] Application mobile compagnon
- [ ] API REST publique
- [ ] Multi-langues (EN, ES, DE)

### Version 1.5 (Actuelle) ✅
- [x] Compteur avancé avec statistiques
- [x] Export ZIP galerie avec QR code
- [x] Détection auto imprimante USB + réseau IPP
- [x] Validation après chaque photo capturée
- [x] Création de montages personnalisés depuis galerie
- [x] Gestion automatique des archives expirées
- [x] Support impression IPP/IPPS pour imprimantes réseau
- [x] Sessions flexibles (1 à 4 photos)

### Version 1.6 (En développement)
- [ ] Thèmes d'interface personnalisables
- [ ] Backup automatique cloud configurable
- [ ] Statistiques graphiques avancées
- [ ] Support impression sans bordure

---

## 🆕 Nouveautés Version 1.5

### Validation Interactive des Photos
Après chaque capture, l'utilisateur peut :
- **Enregistrer** la photo si elle convient
- **Refaire** la photo si nécessaire
- **Annuler** toute la session (avec confirmation si photos déjà capturées)

### Support Imprimantes Réseau
- Détection automatique des imprimantes IPP/IPPS
- Impression optimisée selon le type de connexion (réseau ou USB)
- Information claire du mode d'impression utilisé

### Export ZIP avec QR Code
- Téléchargement de toute la galerie en un fichier
- QR code pour accès mobile instantané
- Gestion automatique des archives (expiration paramétrable)
- Nettoyage périodique des fichiers obsolètes

### Création de Montages Personnalisés
- Sélection de 4 photos depuis la galerie
- Interface intuitive avec prévisualisation
- Application du style sélectionné au montage

### Sessions Flexibles
- Plus besoin de prendre exactement 4 photos
- Arrêt possible à tout moment (1, 2, 3 ou 4 photos)
- Toutes les photos sont sauvegardées et comptabilisées

---

**Made with ❤️ for makers & photo enthusiasts**

> ⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile sur GitHub !

---

## 📞 Support

Pour toute question ou problème :
1. Consultez la section [Résolution de Problèmes](#-résolution-de-problèmes)
2. Vérifiez les [Issues GitHub](https://github.com/votre-username/photovinc/issues)
3. Créez une nouvelle issue avec :
   - Description détaillée du problème
   - Version de Raspberry Pi OS
   - Logs d'erreur (`/var/log/cups/error_log` pour impression)
   - Modèle d'imprimante utilisé
