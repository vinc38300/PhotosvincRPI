# GUIDE D'INSTALLATION IPP POUR PHOTOVINC

## 🎯 Objectif
Intégrer le support IPP (Internet Printing Protocol) pour les imprimantes réseau Epson **SANS CASSER** le support USB/classique existant.

## ⚡ Fonctionnement Intelligent

Le système détecte automatiquement le type d'imprimante:

```
┌─────────────────────────────────────┐
│  Imprimante détectée                │
└─────────────────┬───────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ URI contient     │
        │ ipp:// ou ipps:// ?│
        └────┬────────┬────┘
             │        │
          OUI│        │NON
             ▼        ▼
    ┌─────────────┐  ┌──────────────┐
    │ IPP Printer │  │ USB/Classique│
    │ (réseau)    │  │ (direct)     │
    └─────────────┘  └──────────────┘
         🌐              🖨️
```

## 📋 Compatibilité Garantie

### ✅ Types d'imprimantes supportés:

1. **USB (Canon SELPHY, Canon CP-400, etc.)**
   - URI: `gutenprint53+usb://...`
   - Méthode: Plugin printer classique
   - Status: ✅ Fonctionne comme avant

2. **Réseau IPP/IPPS (Epson R360, etc.)**
   - URI: `ipp://...` ou `ipps://...`
   - Méthode: EpsonIPPPrinter (JPEG→PDF→IPP)
   - Status: ✅ Nouvellement supporté

3. **Réseau DNS-SD**
   - URI: `dnssd://...`
   - Méthode: Plugin printer classique
   - Status: ✅ Fonctionne comme avant

4. **Réseau Socket**
   - URI: `socket://...`
   - Méthode: Plugin printer classique
   - Status: ✅ Fonctionne comme avant

## 📋 Prérequis

```bash
# 1. Installer reportlab (obligatoire pour PDF)
pip install reportlab

# 2. Vérifier que les 3 fichiers sont présents:
ls -lh epson_ipp_printer.py printer_detection.py integration_complete.py
```

## 🔧 Installation Automatique

```bash
# Exécuter le script de patch
python3 apply_ipp_integration.py

# Ceci va:
# - Créer des backups dans backups/YYYYMMDD_HHMMSS/
# - Patcher printer_detection.py
# - Patcher integration_complete.py  
# - Créer test_ipp_integration.py
```

## 🧪 Test

```bash
# Test de détection
python3 test_ipp_integration.py

# Test complet de l'application
python3 integration_complete.py
```

## 🔍 Vérifications

### 1. Vérifier la détection IPP
```bash
python3 printer_detection.py
```

Devrait afficher:
```
✓ IPP printer créé pour Epson_R360
🟢 CONNECTÉE
```

### 2. Vérifier les imports
```python
python3 -c "from epson_ipp_printer import EpsonIPPPrinter; print('OK')"
```

### 3. Vérifier reportlab
```python
python3 -c "from reportlab.pdfgen import canvas; print('OK')"
```

## 📝 Fonctionnement

### Détection Automatique

Le système choisit la bonne méthode selon l'URI:

**Imprimante USB Canon SELPHY:**
```
URI: gutenprint53+usb://Canon/SELPHY-CP400
→ ipp_printer = None
→ Utilise printer.print_image() (méthode classique)
→ 🖨️  "Impression USB/classique"
```

**Imprimante réseau Epson R360:**
```
URI: ipps://192.168.1.100:631/ipp/print
→ ipp_printer = EpsonIPPPrinter(...)
→ Utilise ipp_printer.print_image() (conversion PDF)
→ 🌐 "Impression IPP (réseau)"
```

### Pipeline d'Impression

**USB/Classique (inchangé):**
```
JPEG → lp direct → Imprimante USB
```

**IPP/IPPS (nouveau):**
```
JPEG → Conversion RGB → PDF → lp avec options IPP → Imprimante réseau
```

## 🔧 Configuration Manuelle (si nécessaire)

Si le patch automatique échoue, voici les modifications manuelles:

### 1. printer_detection.py

**Ajouter en haut:**
```python
from epson_ipp_printer import EpsonIPPPrinter
IPP_AVAILABLE = True
```

**Dans PrinterInfo:**
```python
@dataclass
class PrinterInfo:
    # ... autres champs ...
    ipp_printer: Optional[Any] = None
```

**Dans detect_printers():**
```python
# Après device_uri = ...
ipp_printer_instance = None
if IPP_AVAILABLE and ('ipp://' in device_uri or 'ipps://' in device_uri):
    ipp_printer_instance = EpsonIPPPrinter(device_uri, name)

info = PrinterInfo(
    # ... autres params ...
    ipp_printer=ipp_printer_instance
)
```

### 2. integration_complete.py

**Dans print_photo_from_gallery():**
```python
if hasattr(self, 'printer_integration'):
    ipp = self.printer_integration.selected_printer.ipp_printer
    if ipp:
        success = ipp.print_image(str(photo_path))
    else:
        success = printer.print_image(str(photo_path))
```

## 🐛 Dépannage

### Erreur: "reportlab manquant"
```bash
pip install reportlab
```

### Erreur: "Module epson_ipp_printer not found"
```bash
# Vérifier que le fichier existe
ls -lh epson_ipp_printer.py

# Vérifier les permissions
chmod +x epson_ipp_printer.py
```

### L'imprimante n'est pas détectée comme IPP
```bash
# Vérifier l'URI de l'imprimante
lpstat -v

# Doit contenir "ipp://" ou "ipps://"
```

### Les couleurs sont toujours mauvaises
```bash
# Vérifier que IPP est vraiment utilisé
# Dans les logs, vous devez voir:
🌐 Impression IPP: /path/to/photo.jpg
```

## 📊 Logs

Les logs IPP apparaissent dans la console:
```
Chargement: photo.jpg
  Conversion RGBA → RGB
  PDF: 1024×768 → 595×421
  PDF créé: /tmp/photovinc_ipp/print_photo.pdf
Envoi IPP: lp -h 192.168.1.100 ...
✓ Envoyé à l'imprimante
```

## ✅ Validation

L'intégration fonctionne si:

1. ✓ `python3 printer_detection.py` affiche "IPP printer créé"
2. ✓ `test_ipp_integration.py` réussit
3. ✓ Les impressions ont les bonnes couleurs
4. ✓ Pas d'erreur "unknown format" dans les logs

## 🔄 Rollback

Si problème, restaurer les backups:
```bash
cp backups/YYYYMMDD_HHMMSS/*.py .
```

## 📞 Support

En cas de problème:
1. Vérifier les logs dans la console
2. Tester avec `test_ipp_integration.py`
3. Vérifier que reportlab est installé
4. Vérifier l'URI de l'imprimante avec `lpstat -v`
