#!/usr/bin/env python3
"""
Mode Démo - Plugins simulés pour tester sans matériel
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont
import logging
import time
import random
from pathlib import Path

logger = logging.getLogger(__name__)


class DemoCameraPlugin(PluginInterface):
    """Caméra simulée pour le mode démo"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.camera_ready = False
    
    def initialize(self) -> bool:
        """Initialise la caméra de démo"""
        logger.info("Initialisation DemoCameraPlugin")
        self.camera_ready = True
        self._initialized = True
        return True
    
    def shutdown(self):
        """Arrête la caméra"""
        logger.info("Arrêt DemoCameraPlugin")
        self.camera_ready = False
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de la caméra"""
        return {
            "initialized": self._initialized,
            "camera_ready": self.camera_ready,
            "connected": self.camera_ready,
            "mode": "DEMO"
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités"""
        return ["capture", "preview", "demo_mode"]
    
    def capture_image(self, output_path: str) -> bool:
        """Simule une capture d'image"""
        if not self._initialized or not self.camera_ready:
            logger.error("Caméra non initialisée")
            return False
        
        try:
            # Créer une image de démo
            img = Image.new('RGB', (1600, 1200), color=(
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            ))
            
            draw = ImageDraw.Draw(img)
            
            # Dessiner un cadre
            for i in range(20):
                color = (
                    random.randint(50, 200),
                    random.randint(50, 200),
                    random.randint(50, 200)
                )
                draw.rectangle([i*10, i*10, 1600-i*10, 1200-i*10], outline=color, width=3)
            
            # Ajouter du texte
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            except:
                font_large = font_small = ImageFont.load_default()
            
            # Texte MODE DEMO
            text = "MODE DEMO"
            bbox = draw.textbbox((0, 0), text, font=font_large)
            text_width = bbox[2] - bbox[0]
            draw.text(((1600 - text_width) // 2, 450), text, fill=(50, 50, 50), font=font_large)
            
            # Timestamp
            timestamp = time.strftime("%H:%M:%S")
            bbox2 = draw.textbbox((0, 0), timestamp, font=font_small)
            text_width2 = bbox2[2] - bbox2[0]
            draw.text(((1600 - text_width2) // 2, 600), timestamp, fill=(100, 100, 100), font=font_small)
            
            # Emoji sourire
            try:
                draw.text((750, 250), "😊", font=font_large)
            except:
                pass
            
            # Sauvegarder
            img.save(output_path, quality=95)
            logger.info(f"Photo démo capturée: {output_path}")
            
            # Simuler le temps de capture
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur capture démo: {e}")
            return False


class DemoPrinterPlugin(PluginInterface):
    """Imprimante simulée pour le mode démo"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.printer_name = "DEMO_PRINTER"
        self.paper_size = "Postcard"
        self.printer_available = False
        self.print_count = 0
    
    def initialize(self) -> bool:
        """Initialise l'imprimante"""
        logger.info("Initialisation DemoPrinterPlugin")
        self.printer_available = True
        self._initialized = True
        return True
    
    def shutdown(self):
        """Arrête l'imprimante"""
        logger.info("Arrêt DemoPrinterPlugin")
        self.printer_available = False
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'imprimante"""
        return {
            "initialized": self._initialized,
            "printer_name": self.printer_name,
            "available": self.printer_available,
            "status": "Prête (DEMO)",
            "status_ok": True,
            "jobs_count": 0,
            "mode": "DEMO",
            "print_count": self.print_count
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités"""
        return ["print", "check_status", "demo_mode"]
    
    def check_printer_status(self) -> tuple[bool, str]:
        """Vérifie le statut de l'imprimante"""
        return True, "Prête (DEMO)"
    
    def _get_jobs_count(self) -> int:
        """Compte les jobs en attente"""
        return 0
    
    def print_image(self, image_path: str) -> bool:
        """Simule une impression"""
        if not self._initialized or not self.printer_available:
            logger.error("Imprimante non disponible")
            return False
        
        try:
            logger.info(f"Impression démo: {image_path}")
            
            # Simuler le temps d'impression
            time.sleep(1)
            
            self.print_count += 1
            logger.info(f"Impression simulée réussie (Total: {self.print_count})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur impression démo: {e}")
            return False
    
    def cancel_all_jobs(self):
        """Annule tous les jobs"""
        logger.info("Annulation jobs (DEMO)")
    
    def reset_printer(self) -> bool:
        """Réinitialise l'imprimante"""
        logger.info("Reset imprimante (DEMO)")
        time.sleep(0.5)
        return True


def register_demo_plugins(manager):
    """Enregistre les plugins en mode démo"""
    from plugin_manager import PluginConfig
    
    # Configuration caméra démo
    manager.plugin_configs["camera"] = PluginConfig(
        name="camera",
        enabled=True,
        priority=1,
        settings={"mode": "demo"}
    )
    
    # Configuration imprimante démo
    manager.plugin_configs["printer"] = PluginConfig(
        name="printer",
        enabled=True,
        priority=2,
        settings={
            "printer_name": "DEMO_PRINTER",
            "paper_size": "Postcard",
            "mode": "demo"
        }
    )
    
    manager.save_config()
    
    # Enregistrer les plugins démo
    manager.register_plugin("camera", DemoCameraPlugin)
    manager.register_plugin("printer", DemoPrinterPlugin)
    
    logger.info("Plugins DEMO enregistrés")


# Test du mode démo
if __name__ == "__main__":
    from plugin_manager import PluginManager
    
    logging.basicConfig(level=logging.INFO)
    
    manager = PluginManager()
    manager.load_config()
    
    register_demo_plugins(manager)
    
    results = manager.initialize_all()
    
    print("\n=== Mode DEMO activé ===")
    for name, success in results.items():
        print(f"{'✓' if success else '✗'} {name}")
    
    # Test caméra
    camera = manager.get_plugin("camera")
    if camera and camera.is_initialized():
        print("\nTest capture caméra démo...")
        if camera.capture_image("/tmp/demo_photo.jpg"):
            print("✓ Capture réussie: /tmp/demo_photo.jpg")
        else:
            print("✗ Échec capture")
    
    # Test imprimante
    printer = manager.get_plugin("printer")
    if printer and printer.is_initialized():
        print("\nTest impression démo...")
        if printer.print_image("/tmp/demo_photo.jpg"):
            print("✓ Impression simulée")
            status = printer.get_status()
            print(f"  Compteur: {status['print_count']}")
    
    manager.shutdown_all()