 
#!/usr/bin/env python3
"""
QR Code Plugin pour photovinc
Génère des QR codes pour partager les photos
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class QRCodePlugin(PluginInterface):
    """Plugin de génération de QR codes"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.qr_available = False
        self.server_url = config.settings.get('server_url', 'http://192.168.1.100:8000')
        self.qr_size = config.settings.get('qr_size', 200)
    
    def initialize(self) -> bool:
        """Initialise le plugin QR Code"""
        logger.info("Initialisation QRCodePlugin")
        
        try:
            # Vérifier que qrcode est installé
            import qrcode
            self.qr_available = True
            self._initialized = True
            logger.info("Module qrcode disponible")
            return True
        except ImportError:
            logger.warning("Module qrcode non installé: pip install qrcode[pil]")
            self.qr_available = False
            self._initialized = False
            return False
    
    def shutdown(self):
        """Arrête le plugin"""
        logger.info("Arrêt QRCodePlugin")
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du plugin"""
        return {
            "initialized": self._initialized,
            "qr_available": self.qr_available,
            "server_url": self.server_url,
            "qr_size": self.qr_size
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités du plugin"""
        return ["generate_qr", "generate_qr_for_photo", "get_photo_url"]
    
    def generate_qr_code(self, data: str, output_path: str, size: Optional[int] = None) -> bool:
        """Génère un QR code"""
        if not self._initialized or not self.qr_available:
            logger.error("Plugin QR Code non initialisé")
            return False
        
        try:
            import qrcode
            from PIL import Image
            
            # Créer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Redimensionner si nécessaire
            if size is None:
                size = self.qr_size
            
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Sauvegarder
            img.save(output_path)
            logger.info(f"QR code généré: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur génération QR code: {e}")
            return False
    
    def get_photo_url(self, photo_filename: str) -> str:
        """Construit l'URL de partage pour une photo"""
        # Extraire juste le nom du fichier
        filename = os.path.basename(photo_filename)
        url = f"{self.server_url}/photo/{filename}"
        return url
    
    def generate_qr_for_photo(self, photo_path: str, qr_output_path: Optional[str] = None) -> Optional[str]:
        """Génère un QR code pour une photo spécifique"""
        if not self._initialized:
            return None
        
        # Créer l'URL de partage
        url = self.get_photo_url(photo_path)
        
        # Chemin de sortie du QR code
        if qr_output_path is None:
            photo_name = Path(photo_path).stem
            qr_output_path = str(Path(photo_path).parent / f"{photo_name}_qr.png")
        
        # Générer le QR code
        if self.generate_qr_code(url, qr_output_path):
            return qr_output_path
        
        return None
    
    def add_qr_to_photo(self, photo_path: str, output_path: str, 
                        position: str = "bottom-right") -> bool:
        """Ajoute un QR code sur une photo"""
        if not self._initialized:
            return False
        
        try:
            from PIL import Image
            
            # Générer le QR code temporaire
            temp_qr = "/tmp/temp_qr.png"
            url = self.get_photo_url(photo_path)
            
            if not self.generate_qr_code(url, temp_qr, size=150):
                return False
            
            # Ouvrir la photo et le QR code
            photo = Image.open(photo_path)
            qr = Image.open(temp_qr)
            
            # Calculer la position
            photo_width, photo_height = photo.size
            qr_width, qr_height = qr.size
            margin = 20
            
            if position == "bottom-right":
                x = photo_width - qr_width - margin
                y = photo_height - qr_height - margin
            elif position == "bottom-left":
                x = margin
                y = photo_height - qr_height - margin
            elif position == "top-right":
                x = photo_width - qr_width - margin
                y = margin
            elif position == "top-left":
                x = margin
                y = margin
            else:
                x = photo_width - qr_width - margin
                y = photo_height - qr_height - margin
            
            # Coller le QR code
            photo.paste(qr, (x, y))
            
            # Sauvegarder
            photo.save(output_path, quality=95)
            
            # Nettoyer
            os.remove(temp_qr)
            
            logger.info(f"QR code ajouté à la photo: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur ajout QR code: {e}")
            return False


def register_qr_plugin(manager):
    """Enregistre le plugin QR Code"""
    from plugin_manager import PluginConfig
    
    if "qrcode" not in manager.plugin_configs:
        manager.plugin_configs["qrcode"] = PluginConfig(
            name="qrcode",
            enabled=True,
            priority=16,
            settings={
                "server_url": "http://192.168.1.100:8000",
                "qr_size": 200
            }
        )
        manager.save_config()
    
    manager.register_plugin("qrcode", QRCodePlugin)
    logger.info("QR Code plugin enregistré")


# Test du plugin
if __name__ == "__main__":
    from plugin_manager import PluginConfig
    
    # Configuration de test
    config = PluginConfig(
        name="qrcode",
        enabled=True,
        priority=16,
        settings={
            "server_url": "http://192.168.1.100:8000",
            "qr_size": 200
        }
    )
    
    # Créer et tester le plugin
    plugin = QRCodePlugin(config)
    
    if plugin.initialize():
        print("✓ Plugin QR Code initialisé")
        
        # Test génération QR code
        test_url = "https://example.com/photo123"
        if plugin.generate_qr_code(test_url, "/tmp/test_qr.png"):
            print("✓ QR code généré: /tmp/test_qr.png")
        
        # Test URL photo
        url = plugin.get_photo_url("/home/user/photo_test.jpg")
        print(f"URL: {url}")
        
        plugin.shutdown()
    else:
        print("✗ Échec initialisation QR Code")
        print("Installer: pip install qrcode[pil]")
