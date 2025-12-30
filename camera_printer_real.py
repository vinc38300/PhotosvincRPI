 
#!/usr/bin/env python3
"""
Plugins Camera et Printer - CODE FONCTIONNEL
Extrait de photovinc_complet5.py avec le vrai code
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any, Optional
import subprocess
import logging
import time
import os

logger = logging.getLogger(__name__)


class CameraPluginReal(PluginInterface):
    """Plugin caméra avec le vrai code gphoto2"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.camera_ready = False
    
    def initialize(self) -> bool:
        """Initialise la caméra en tuant gvfs"""
        logger.info("Initialisation CameraPlugin")
        
        try:
            # Tuer gvfs qui bloque gphoto2
            subprocess.run(['killall', '-9', 'gvfs-gphoto2-volume-monitor'], 
                         capture_output=True, timeout=2)
            subprocess.run(['killall', '-9', 'gvfsd-gphoto2'], 
                         capture_output=True, timeout=2)
            time.sleep(1)
        except:
            pass
        
        try:
            # Tester la détection de la caméra
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                  capture_output=True, timeout=5)
            self.camera_ready = True
            self._initialized = True
            logger.info("Caméra détectée et prête")
            return True
        except Exception as e:
            logger.error(f"Erreur initialisation caméra: {e}")
            self.camera_ready = False
            self._initialized = False
            return False
    
    def shutdown(self):
        """Arrête la caméra"""
        logger.info("Arrêt CameraPlugin")
        self.camera_ready = False
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de la caméra"""
        return {
            "initialized": self._initialized,
            "camera_ready": self.camera_ready,
            "connected": self.camera_ready
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités"""
        return ["capture", "preview", "auto_detect"]
    
    def capture_image(self, output_path: str) -> bool:
        """Capture une image avec gphoto2"""
        if not self._initialized or not self.camera_ready:
            logger.error("Caméra non initialisée")
            return False
        
        try:
            result = subprocess.run(
                ['gphoto2', '--capture-image-and-download', 
                 '--filename', output_path, '--force-overwrite'],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Photo capturée: {output_path}")
                return True
            else:
                logger.error(f"Échec capture: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout capture photo")
            return False
        except Exception as e:
            logger.error(f"Erreur capture: {e}")
            return False


class PrinterPluginReal(PluginInterface):
    """Plugin imprimante avec le vrai code CUPS"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.printer_name = config.settings.get('printer_name', 'CP_400')
        self.paper_size = config.settings.get('paper_size', 'Postcard')
        self.printer_available = False
    
    def initialize(self) -> bool:
        """Initialise l'imprimante"""
        logger.info(f"Initialisation PrinterPlugin: {self.printer_name}")
        
        try:
            # Vérifier que l'imprimante existe
            result = subprocess.run(
                ['lpstat', '-p', self.printer_name],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                self.printer_available = True
                self._initialized = True
                logger.info(f"Imprimante {self.printer_name} détectée")
                return True
            else:
                logger.warning(f"Imprimante {self.printer_name} non trouvée")
                self.printer_available = False
                self._initialized = False
                return False
                
        except Exception as e:
            logger.error(f"Erreur initialisation imprimante: {e}")
            return False
    
    def shutdown(self):
        """Arrête l'imprimante"""
        logger.info("Arrêt PrinterPlugin")
        self.printer_available = False
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'imprimante"""
        status_ok, status_msg = self.check_printer_status()
        
        return {
            "initialized": self._initialized,
            "printer_name": self.printer_name,
            "available": self.printer_available,
            "status": status_msg,
            "status_ok": status_ok,
            "jobs_count": self._get_jobs_count()
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités"""
        return ["print", "check_status", "cancel_jobs", "reset"]
    
    def check_printer_status(self) -> tuple[bool, str]:
        """Vérifie le statut de l'imprimante (code original)"""
        try:
            result = subprocess.run(
                ['lpstat', '-p', self.printer_name],
                capture_output=True, 
                text=True, 
                timeout=3
            )
            
            output = result.stdout + result.stderr
            
            if 'idle' in output.lower():
                # Vérifier les jobs bloqués
                jobs_result = subprocess.run(
                    ['lpstat', '-o'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if jobs_result.returncode == 0:
                    jobs_output = jobs_result.stdout
                    if self.printer_name in jobs_output and 'held' in jobs_output.lower():
                        return False, "Job bloqué"
                    elif self.printer_name in jobs_output:
                        return True, "Impression..."
                
                # Vérifier les logs CUPS
                try:
                    log_result = subprocess.run(
                        ['tail', '-20', '/var/log/cups/error_log'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    log_output = log_result.stdout
                    
                    if self.printer_name in log_output or 'Job' in log_output:
                        if 'Incorrect paper' in log_output:
                            return False, "Mauvais papier"
                        elif 'No matching' in log_output:
                            return False, "Non connectée"
                        elif 'open failure' in log_output:
                            return False, "Non trouvée"
                        elif 'ERROR' in log_output and self.printer_name in log_output:
                            return False, "Erreur"
                except:
                    pass
                
                return True, "Prête"
                
            elif 'disabled' in output.lower():
                return False, "Désactivée"
            elif 'paused' in output.lower():
                return False, "En pause"
            else:
                return True, "OK"
                    
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            logger.error(f"Erreur statut imprimante: {e}")
            return False, "Erreur"
    
    def _get_jobs_count(self) -> int:
        """Compte les jobs en attente"""
        try:
            result = subprocess.run(
                ['lpstat', '-o'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                lines = [l for l in result.stdout.split('\n') if self.printer_name in l]
                return len(lines)
        except:
            pass
        
        return 0
    
    def print_image(self, image_path: str) -> bool:
        """Imprime une image"""
        if not self._initialized or not self.printer_available:
            logger.error("Imprimante non disponible")
            return False
        
        try:
            result = subprocess.run([
                'lp',
                '-d', self.printer_name,
                '-o', f'PageSize={self.paper_size}',
                str(image_path)
            ], capture_output=True, timeout=5)
            
            if result.returncode == 0:
                logger.info(f"Impression lancée: {image_path}")
                return True
            else:
                logger.error(f"Échec impression: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur impression: {e}")
            return False
    
    def cancel_all_jobs(self):
        """Annule tous les jobs"""
        try:
            subprocess.run(['cancel', '-a'], capture_output=True, timeout=5)
            logger.info("Jobs annulés")
        except Exception as e:
            logger.error(f"Erreur annulation jobs: {e}")
    
    def reset_printer(self) -> bool:
        """Réinitialise l'imprimante (code original)"""
        try:
            # Annuler les jobs
            subprocess.run(['cancel', '-a'], capture_output=True, timeout=5)
            time.sleep(1)
            
            # Redémarrer CUPS
            subprocess.run(['sudo', 'systemctl', 'restart', 'cups'], 
                         capture_output=True, timeout=10)
            time.sleep(2)
            
            # Réactiver l'imprimante
            subprocess.run(['cupsenable', self.printer_name], 
                         capture_output=True, timeout=5)
            time.sleep(1)
            
            subprocess.run(['cupsaccept', self.printer_name], 
                         capture_output=True, timeout=5)
            
            logger.info("Imprimante réinitialisée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur reset imprimante: {e}")
            return False


# Fonction pour remplacer les plugins vides par les vrais
def register_real_plugins(manager):
    """Enregistre les vrais plugins fonctionnels"""
    from plugin_manager import PluginConfig
    
    # Configuration caméra
    if "camera" not in manager.plugin_configs:
        manager.plugin_configs["camera"] = PluginConfig(
            name="camera",
            enabled=True,
            priority=1,
            settings={}
        )
    
    # Configuration imprimante
    if "printer" not in manager.plugin_configs:
        manager.plugin_configs["printer"] = PluginConfig(
            name="printer",
            enabled=True,
            priority=2,
            settings={
                "printer_name": "CP_400",
                "paper_size": "Postcard"
            }
        )
    
    manager.save_config()
    
    # Enregistrer les vrais plugins
    manager.register_plugin("camera", CameraPluginReal)
    manager.register_plugin("printer", PrinterPluginReal)
    
    logger.info("Vrais plugins Camera et Printer enregistrés")


# Test
if __name__ == "__main__":
    from plugin_manager import PluginManager
    
    manager = PluginManager()
    manager.load_config()
    
    register_real_plugins(manager)
    
    results = manager.initialize_all()
    
    print("\n=== Test des plugins ===")
    for name, success in results.items():
        print(f"{'✓' if success else '✗'} {name}")
    
    # Test caméra
    camera = manager.get_plugin("camera")
    if camera and camera.is_initialized():
        print("\nTest capture caméra...")
        if camera.capture_image("/tmp/test_camera.jpg"):
            print("✓ Capture réussie")
        else:
            print("✗ Échec capture")
    
    # Test imprimante
    printer = manager.get_plugin("printer")
    if printer and printer.is_initialized():
        print("\nStatut imprimante:")
        status = printer.get_status()
        print(f"  Status: {status['status']}")
        print(f"  Jobs: {status['jobs_count']}")
    
    manager.shutdown_all()
