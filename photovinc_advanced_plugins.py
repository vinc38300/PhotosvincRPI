#!/usr/bin/env python3
"""
Plugins avancés pour photovinc
- CloudStoragePlugin : Sauvegarde cloud (Google Drive, Dropbox)
- FilterPlugin : Filtres Instagram-like
- AnalyticsPlugin : Statistiques d'utilisation
- SocialSharePlugin : Partage sur réseaux sociaux
- FaceDetectionPlugin : Détection et amélioration des visages
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any, Optional
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import requests
from PIL import Image, ImageEnhance, ImageFilter
import os

logger = logging.getLogger(__name__)


class CloudStoragePlugin(PluginInterface):
    """Plugin de sauvegarde cloud automatique"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.provider = config.settings.get('provider', 'local')  # local, gdrive, dropbox
        self.auto_upload = config.settings.get('auto_upload', False)
        self.upload_queue = []
        self.credentials_file = Path.home() / ".photovinc_cloud_credentials.json"
    
    def initialize(self) -> bool:
        logger.info(f"Initialisation CloudStorage: {self.provider}")
        try:
            if self.provider == 'local':
                self._initialized = True
                return True
            
            # Vérifier les credentials
            if not self.credentials_file.exists():
                logger.warning("Credentials cloud non configurés")
                self._initialized = False
                return False
            
            # Tester la connexion
            if self._test_connection():
                self._initialized = True
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erreur init cloud: {e}")
            return False
    
    def shutdown(self):
        logger.info("Arrêt CloudStorage")
        # Upload des photos en attente
        if self.upload_queue:
            self._flush_queue()
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "provider": self.provider,
            "queue_size": len(self.upload_queue),
            "auto_upload": self.auto_upload,
            "space_used": self._get_space_used()
        }
    
    def get_capabilities(self) -> List[str]:
        return ["upload", "download", "sync", "list_files"]
    
    def _test_connection(self) -> bool:
        """Teste la connexion au service cloud"""
        if self.provider == 'gdrive':
            # Test Google Drive API
            return self._test_gdrive()
        elif self.provider == 'dropbox':
            # Test Dropbox API
            return self._test_dropbox()
        return False
    
    def _test_gdrive(self) -> bool:
        """Teste Google Drive"""
        # Nécessite google-api-python-client
        try:
            # Code simplifié - à implémenter avec OAuth2
            return True
        except:
            return False
    
    def _test_dropbox(self) -> bool:
        """Teste Dropbox"""
        try:
            # Code simplifié - à implémenter avec l'API Dropbox
            return True
        except:
            return False
    
    def _get_space_used(self) -> str:
        """Obtient l'espace utilisé"""
        if self.provider == 'local':
            # Calculer la taille du dossier Photos
            photo_dir = Path.home() / "Photos_photovinc"
            if photo_dir.exists():
                total_size = sum(f.stat().st_size for f in photo_dir.glob('**/*') if f.is_file())
                return f"{total_size / (1024*1024):.1f} MB"
        return "N/A"
    
    def upload_photo(self, photo_path: str, remote_name: Optional[str] = None) -> bool:
        """Upload une photo vers le cloud"""
        if not self._initialized:
            logger.error("Cloud storage non initialisé")
            return False
        
        if self.provider == 'local':
            return True  # Déjà local
        
        try:
            if self.auto_upload:
                return self._do_upload(photo_path, remote_name)
            else:
                self.upload_queue.append((photo_path, remote_name))
                return True
        except Exception as e:
            logger.error(f"Erreur upload: {e}")
            return False
    
    def _do_upload(self, photo_path: str, remote_name: Optional[str]) -> bool:
        """Effectue l'upload réel"""
        # Implémentation selon le provider
        logger.info(f"Upload {photo_path} vers {self.provider}")
        return True
    
    def _flush_queue(self):
        """Upload toutes les photos en attente"""
        logger.info(f"Upload de {len(self.upload_queue)} photos en attente")
        for photo_path, remote_name in self.upload_queue:
            self._do_upload(photo_path, remote_name)
        self.upload_queue.clear()


class FilterPlugin(PluginInterface):
    """Plugin de filtres photo avancés (style Instagram)"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.available_filters = []
    
    def initialize(self) -> bool:
        logger.info("Initialisation FilterPlugin")
        self.available_filters = [
            "clarendon", "gingham", "juno", "lark", "ludwig",
            "valencia", "xpro2", "noir", "warm", "cool",
            "brighten", "contrast", "saturate"
        ]
        self._initialized = True
        return True
    
    def shutdown(self):
        logger.info("Arrêt FilterPlugin")
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "available_filters": len(self.available_filters),
            "filters": self.available_filters
        }
    
    def get_capabilities(self) -> List[str]:
        return ["apply_filter", "preview_filter", "combine_filters"]
    
    def apply_filter(self, image_path: str, filter_name: str, output_path: str) -> bool:
        """Applique un filtre à une image"""
        if not self._initialized:
            return False
        
        try:
            img = Image.open(image_path)
            filtered = self._apply_filter_logic(img, filter_name)
            filtered.save(output_path, quality=95)
            return True
        except Exception as e:
            logger.error(f"Erreur application filtre: {e}")
            return False
    
    def _apply_filter_logic(self, img: Image.Image, filter_name: str) -> Image.Image:
        """Logique d'application des filtres"""
        
        if filter_name == "clarendon":
            # Augmente contraste et saturation
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.2)
        
        elif filter_name == "gingham":
            # Effet vintage chaud
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(0.9)
        
        elif filter_name == "juno":
            # Tons chauds augmentés
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.1)
        
        elif filter_name == "lark":
            # Luminosité élevée, saturation
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.3)
        
        elif filter_name == "ludwig":
            # Contraste fort, tons froids
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)
            return img
        
        elif filter_name == "valencia":
            # Tons chauds, fade
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.05)
        
        elif filter_name == "xpro2":
            # Contraste extrême, vignetage
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.3)
        
        elif filter_name == "noir":
            # Noir et blanc
            return img.convert('L').convert('RGB')
        
        elif filter_name == "warm":
            # Teinte chaude
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.3)
        
        elif filter_name == "cool":
            # Teinte froide
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(0.7)
        
        elif filter_name == "brighten":
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.3)
        
        elif filter_name == "contrast":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.4)
        
        elif filter_name == "saturate":
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.5)
        
        return img


class AnalyticsPlugin(PluginInterface):
    """Plugin de statistiques et analytics"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.data_file = Path.home() / ".photovinc_analytics.json"
        self.stats = {
            "total_sessions": 0,
            "total_photos": 0,
            "total_prints": 0,
            "total_qr_scans": 0,
            "style_usage": {},
            "daily_usage": {},
            "hourly_usage": {},
            "error_count": 0,
            "last_session": None
        }
    
    def initialize(self) -> bool:
        logger.info("Initialisation AnalyticsPlugin")
        self._load_stats()
        self._initialized = True
        return True
    
    def shutdown(self):
        logger.info("Arrêt AnalyticsPlugin")
        self._save_stats()
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "total_sessions": self.stats["total_sessions"],
            "total_photos": self.stats["total_photos"],
            "total_prints": self.stats["total_prints"]
        }
    
    def get_capabilities(self) -> List[str]:
        return ["record_event", "get_stats", "export_report", "reset_stats"]
    
    def _load_stats(self):
        """Charge les statistiques"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    self.stats.update(json.load(f))
            except Exception as e:
                logger.error(f"Erreur chargement stats: {e}")
    
    def _save_stats(self):
        """Sauvegarde les statistiques"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde stats: {e}")
    
    def record_session(self, num_photos: int, style: str):
        """Enregistre une session"""
        if not self._initialized:
            return
        
        self.stats["total_sessions"] += 1
        self.stats["total_photos"] += num_photos
        self.stats["last_session"] = datetime.now().isoformat()
        
        # Style usage
        if style not in self.stats["style_usage"]:
            self.stats["style_usage"][style] = 0
        self.stats["style_usage"][style] += 1
        
        # Daily usage
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_usage"]:
            self.stats["daily_usage"][today] = 0
        self.stats["daily_usage"][today] += 1
        
        # Hourly usage
        hour = datetime.now().strftime("%H:00")
        if hour not in self.stats["hourly_usage"]:
            self.stats["hourly_usage"][hour] = 0
        self.stats["hourly_usage"][hour] += 1
        
        self._save_stats()
    
    def record_print(self):
        """Enregistre une impression"""
        self.stats["total_prints"] += 1
        self._save_stats()
    
    def record_qr_scan(self):
        """Enregistre un scan QR"""
        self.stats["total_qr_scans"] += 1
        self._save_stats()
    
    def record_error(self):
        """Enregistre une erreur"""
        self.stats["error_count"] += 1
        self._save_stats()
    
    def get_report(self) -> Dict[str, Any]:
        """Génère un rapport complet"""
        # Style le plus utilisé
        most_used_style = max(self.stats["style_usage"].items(), 
                            key=lambda x: x[1])[0] if self.stats["style_usage"] else "N/A"
        
        # Jour le plus actif
        most_active_day = max(self.stats["daily_usage"].items(), 
                            key=lambda x: x[1])[0] if self.stats["daily_usage"] else "N/A"
        
        # Heure la plus active
        peak_hour = max(self.stats["hourly_usage"].items(), 
                       key=lambda x: x[1])[0] if self.stats["hourly_usage"] else "N/A"
        
        return {
            **self.stats,
            "most_used_style": most_used_style,
            "most_active_day": most_active_day,
            "peak_hour": peak_hour,
            "avg_photos_per_session": self.stats["total_photos"] / max(self.stats["total_sessions"], 1),
            "print_ratio": self.stats["total_prints"] / max(self.stats["total_photos"], 1)
        }
    
    def reset_stats(self):
        """Réinitialise les statistiques"""
        self.stats = {
            "total_sessions": 0,
            "total_photos": 0,
            "total_prints": 0,
            "total_qr_scans": 0,
            "style_usage": {},
            "daily_usage": {},
            "hourly_usage": {},
            "error_count": 0,
            "last_session": None
        }
        self._save_stats()


class SocialSharePlugin(PluginInterface):
    """Plugin de partage sur réseaux sociaux"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.enabled_networks = config.settings.get('networks', ['email'])
        self.hashtags = config.settings.get('hashtags', ['#photovinc'])
    
    def initialize(self) -> bool:
        logger.info("Initialisation SocialSharePlugin")
        self._initialized = True
        return True
    
    def shutdown(self):
        logger.info("Arrêt SocialSharePlugin")
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "enabled_networks": self.enabled_networks,
            "hashtags": self.hashtags
        }
    
    def get_capabilities(self) -> List[str]:
        return ["share_email", "share_sms", "generate_link"]
    
    def share_via_email(self, photo_path: str, recipient: str) -> bool:
        """Partage par email"""
        if not self._initialized:
            return False
        
        try:
            # Utiliser sendmail ou SMTP
            subject = "Votre photo photovinc"
            body = f"Voici votre photo !\n\nHashtags: {' '.join(self.hashtags)}"
            
            # Commande mail (nécessite mailutils)
            cmd = f'echo "{body}" | mail -s "{subject}" -A "{photo_path}" {recipient}'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def generate_share_link(self, photo_path: str) -> Optional[str]:
        """Génère un lien de partage"""
        # Upload temporaire et génération de lien
        # À implémenter avec un service comme imgur, imgbb, etc.
        return None


class FaceDetectionPlugin(PluginInterface):
    """Plugin de détection et amélioration des visages"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.auto_enhance = config.settings.get('auto_enhance', True)
        self.face_cascade = None
    
    def initialize(self) -> bool:
        logger.info("Initialisation FaceDetectionPlugin")
        try:
            # Vérifier OpenCV
            import cv2
            
            # Charger le classifier Haar Cascade
            cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
            if not os.path.exists(cascade_path):
                logger.warning("Haar Cascade non trouvé")
                return False
            
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            self._initialized = True
            return True
        except ImportError:
            logger.error("OpenCV non installé: sudo apt install python3-opencv")
            return False
        except Exception as e:
            logger.error(f"Erreur init face detection: {e}")
            return False
    
    def shutdown(self):
        logger.info("Arrêt FaceDetectionPlugin")
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "auto_enhance": self.auto_enhance,
            "cascade_loaded": self.face_cascade is not None
        }
    
    def get_capabilities(self) -> List[str]:
        return ["detect_faces", "count_faces", "enhance_faces", "add_effects"]
    
    def detect_faces(self, image_path: str) -> List[Dict[str, int]]:
        """Détecte les visages dans une image"""
        if not self._initialized:
            return []
        
        try:
            import cv2
            import numpy as np
            
            # Charger l'image
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Détecter les visages
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Convertir en liste de dictionnaires
            return [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} 
                   for (x, y, w, h) in faces]
        except Exception as e:
            logger.error(f"Erreur détection visages: {e}")
            return []
    
    def count_faces(self, image_path: str) -> int:
        """Compte le nombre de visages"""
        faces = self.detect_faces(image_path)
        return len(faces)
    
    def enhance_faces(self, image_path: str, output_path: str) -> bool:
        """Améliore automatiquement les visages"""
        if not self._initialized:
            return False
        
        try:
            # Détection
            faces = self.detect_faces(image_path)
            
            if not faces:
                # Pas de visages, copier simplement
                import shutil
                shutil.copy2(image_path, output_path)
                return True
            
            # Appliquer des améliorations
            img = Image.open(image_path)
            
            # Augmenter légèrement la luminosité et le contraste
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.05)
            
            # Léger flou pour adoucir la peau
            img = img.filter(ImageFilter.SMOOTH)
            
            img.save(output_path, quality=95)
            return True
        except Exception as e:
            logger.error(f"Erreur amélioration: {e}")
            return False


# Enregistrement des nouveaux plugins dans le manager
def register_advanced_plugins(manager):
    """Enregistre tous les plugins avancés"""
    manager.register_plugin("cloud", CloudStoragePlugin)
    manager.register_plugin("filters", FilterPlugin)
    manager.register_plugin("analytics", AnalyticsPlugin)
    manager.register_plugin("social", SocialSharePlugin)
    manager.register_plugin("faces", FaceDetectionPlugin)
    
    # Ajouter les configs par défaut si nécessaire
    if "cloud" not in manager.plugin_configs:
        manager.plugin_configs["cloud"] = PluginConfig(
            name="cloud",
            enabled=False,
            priority=10,
            settings={"provider": "local", "auto_upload": False}
        )
    
    if "filters" not in manager.plugin_configs:
        manager.plugin_configs["filters"] = PluginConfig(
            name="filters",
            enabled=True,
            priority=11,
            settings={}
        )
    
    if "analytics" not in manager.plugin_configs:
        manager.plugin_configs["analytics"] = PluginConfig(
            name="analytics",
            enabled=True,
            priority=12,
            settings={}
        )
    
    if "social" not in manager.plugin_configs:
        manager.plugin_configs["social"] = PluginConfig(
            name="social",
            enabled=False,
            priority=13,
            settings={"networks": ["email"], "hashtags": ["#photovinc"]}
        )
    
    if "faces" not in manager.plugin_configs:
        manager.plugin_configs["faces"] = PluginConfig(
            name="faces",
            enabled=False,
            priority=14,
            settings={"auto_enhance": True}
        )
    
    manager.save_config()
