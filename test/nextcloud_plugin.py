 
#!/usr/bin/env python3
"""
NextCloud Plugin pour photovinc
Upload automatique des photos vers un serveur NextCloud/OwnCloud
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any, Optional
import logging
import requests
from pathlib import Path
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)


class NextCloudPlugin(PluginInterface):
    """Plugin de synchronisation avec NextCloud/OwnCloud"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        
        # Configuration NextCloud
        self.server_url = config.settings.get('server_url', '')
        self.username = config.settings.get('username', '')
        self.password = config.settings.get('password', '')
        self.remote_folder = config.settings.get('remote_folder', '/photovinc')
        self.auto_upload = config.settings.get('auto_upload', True)
        self.create_dated_folders = config.settings.get('create_dated_folders', True)
        
        # État
        self.connected = False
        self.upload_queue = []
        self.session = None
        self.credentials_file = Path.home() / ".photovinc_nextcloud.json"
    
    def initialize(self) -> bool:
        """Initialise la connexion NextCloud"""
        logger.info("Initialisation NextCloudPlugin")
        
        try:
            # Charger les credentials sauvegardés si disponibles
            if not self.server_url and self.credentials_file.exists():
                self._load_credentials()
            
            # Vérifier que la config est complète
            if not self.server_url or not self.username or not self.password:
                logger.warning("Configuration NextCloud incomplète")
                self._initialized = False
                return False
            
            # Créer une session requests
            self.session = requests.Session()
            self.session.auth = (self.username, self.password)
            self.session.headers.update({
                'OCS-APIRequest': 'true',
                'Content-Type': 'application/x-www-form-urlencoded'
            })
            
            # Tester la connexion
            if self._test_connection():
                self.connected = True
                self._initialized = True
                logger.info("Connexion NextCloud réussie")
                
                # Créer le dossier distant si nécessaire
                self._ensure_remote_folder()
                return True
            else:
                logger.error("Échec connexion NextCloud")
                return False
                
        except Exception as e:
            logger.error(f"Erreur initialisation NextCloud: {e}")
            return False
    
    def shutdown(self):
        """Arrête le plugin"""
        logger.info("Arrêt NextCloudPlugin")
        
        # Upload des fichiers en attente
        if self.upload_queue:
            logger.info(f"Upload de {len(self.upload_queue)} fichiers en attente")
            self._flush_queue()
        
        if self.session:
            self.session.close()
        
        self.connected = False
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du plugin"""
        return {
            "initialized": self._initialized,
            "connected": self.connected,
            "server_url": self.server_url,
            "username": self.username,
            "remote_folder": self.remote_folder,
            "queue_size": len(self.upload_queue),
            "auto_upload": self.auto_upload,
            "space_info": self._get_space_info()
        }
    
    def get_capabilities(self) -> List[str]:
        """Retourne les capacités du plugin"""
        return [
            "upload_file",
            "download_file", 
            "list_files",
            "create_folder",
            "delete_file",
            "get_share_link"
        ]
    
    def _load_credentials(self):
        """Charge les credentials sauvegardés"""
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                self.server_url = data.get('server_url', '')
                self.username = data.get('username', '')
                self.password = data.get('password', '')
                self.remote_folder = data.get('remote_folder', '/photovinc')
        except Exception as e:
            logger.error(f"Erreur chargement credentials: {e}")
    
    def _save_credentials(self):
        """Sauvegarde les credentials"""
        try:
            data = {
                'server_url': self.server_url,
                'username': self.username,
                'password': self.password,
                'remote_folder': self.remote_folder
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            # Permissions restrictives
            os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            logger.error(f"Erreur sauvegarde credentials: {e}")
    
    def _test_connection(self) -> bool:
        """Teste la connexion au serveur NextCloud"""
        try:
            # Utiliser l'API WebDAV pour tester
            url = f"{self.server_url}/remote.php/dav/files/{self.username}/"
            response = self.session.request('PROPFIND', url, timeout=10)
            return response.status_code in [200, 207]  # 207 = Multi-Status (succès WebDAV)
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return False
    
    def _ensure_remote_folder(self):
        """S'assure que le dossier distant existe"""
        try:
            # Créer le dossier principal si nécessaire
            self.create_folder(self.remote_folder)
        except Exception as e:
            logger.warning(f"Impossible de créer le dossier: {e}")
    
    def _get_space_info(self) -> Dict[str, Any]:
        """Obtient les informations d'espace disque"""
        if not self.connected:
            return {"used": "N/A", "available": "N/A", "total": "N/A"}
        
        try:
            url = f"{self.server_url}/ocs/v1.php/cloud/user"
            response = self.session.get(url, params={'format': 'json'}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                quota = data.get('ocs', {}).get('data', {}).get('quota', {})
                
                used = quota.get('used', 0)
                total = quota.get('total', 0)
                available = total - used if total > 0 else 0
                
                return {
                    "used": f"{used / (1024**3):.2f} GB",
                    "available": f"{available / (1024**3):.2f} GB",
                    "total": f"{total / (1024**3):.2f} GB"
                }
        except Exception as e:
            logger.error(f"Erreur récupération espace: {e}")
        
        return {"used": "N/A", "available": "N/A", "total": "N/A"}
    
    def _get_webdav_url(self, remote_path: str) -> str:
        """Construit l'URL WebDAV complète"""
        # Nettoyer le chemin
        remote_path = remote_path.lstrip('/')
        return f"{self.server_url}/remote.php/dav/files/{self.username}/{remote_path}"
    
    def create_folder(self, folder_path: str) -> bool:
        """Crée un dossier sur NextCloud"""
        if not self.connected:
            return False
        
        try:
            url = self._get_webdav_url(folder_path)
            response = self.session.request('MKCOL', url, timeout=10)
            
            # 201 = créé, 405 = existe déjà
            return response.status_code in [201, 405]
        except Exception as e:
            logger.error(f"Erreur création dossier: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: Optional[str] = None) -> bool:
        """Upload un fichier vers NextCloud"""
        if not self.connected:
            logger.error("NextCloud non connecté")
            return False
        
        try:
            local_file = Path(local_path)
            if not local_file.exists():
                logger.error(f"Fichier local introuvable: {local_path}")
                return False
            
            # Déterminer le chemin distant
            if remote_path is None:
                if self.create_dated_folders:
                    # Créer un sous-dossier par date
                    date_folder = datetime.now().strftime("%Y-%m-%d")
                    folder = f"{self.remote_folder}/{date_folder}"
                    self.create_folder(folder)
                    remote_path = f"{folder}/{local_file.name}"
                else:
                    remote_path = f"{self.remote_folder}/{local_file.name}"
            
            # Upload via WebDAV
            url = self._get_webdav_url(remote_path)
            
            with open(local_path, 'rb') as f:
                response = self.session.put(url, data=f, timeout=60)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Upload réussi: {local_file.name} -> {remote_path}")
                return True
            else:
                logger.error(f"Échec upload: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur upload: {e}")
            return False
    
    def upload_photo(self, photo_path: str, remote_name: Optional[str] = None) -> bool:
        """Upload une photo (alias pour upload_file)"""
        if self.auto_upload:
            return self.upload_file(photo_path, remote_name)
        else:
            # Ajouter à la file d'attente
            self.upload_queue.append((photo_path, remote_name))
            return True
    
    def _flush_queue(self):
        """Upload tous les fichiers en attente"""
        for photo_path, remote_name in self.upload_queue:
            self.upload_file(photo_path, remote_name)
        self.upload_queue.clear()
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Télécharge un fichier depuis NextCloud"""
        if not self.connected:
            return False
        
        try:
            url = self._get_webdav_url(remote_path)
            response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Download réussi: {remote_path}")
                return True
            else:
                logger.error(f"Échec download: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur download: {e}")
            return False
    
    def list_files(self, folder_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Liste les fichiers dans un dossier"""
        if not self.connected:
            return []
        
        if folder_path is None:
            folder_path = self.remote_folder
        
        try:
            url = self._get_webdav_url(folder_path)
            
            # Requête PROPFIND pour lister
            headers = {'Depth': '1'}
            response = self.session.request('PROPFIND', url, headers=headers, timeout=10)
            
            if response.status_code == 207:
                # Parser la réponse XML (simplifié)
                files = []
                # Note: Pour un parsing XML complet, utilisez xml.etree.ElementTree
                logger.info(f"Fichiers listés dans {folder_path}")
                return files
            else:
                logger.error(f"Échec listage: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur listage: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Supprime un fichier sur NextCloud"""
        if not self.connected:
            return False
        
        try:
            url = self._get_webdav_url(remote_path)
            response = self.session.delete(url, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"Fichier supprimé: {remote_path}")
                return True
            else:
                logger.error(f"Échec suppression: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur suppression: {e}")
            return False
    
    def get_share_link(self, remote_path: str, password: Optional[str] = None) -> Optional[str]:
        """Crée un lien de partage public pour un fichier"""
        if not self.connected:
            return None
        
        try:
            # API OCS pour créer un partage
            url = f"{self.server_url}/ocs/v2.php/apps/files_sharing/api/v1/shares"
            
            data = {
                'path': remote_path,
                'shareType': 3,  # 3 = lien public
                'permissions': 1  # 1 = lecture seule
            }
            
            if password:
                data['password'] = password
            
            response = self.session.post(
                url, 
                data=data,
                params={'format': 'json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                share_url = result.get('ocs', {}).get('data', {}).get('url')
                logger.info(f"Lien de partage créé: {share_url}")
                return share_url
            else:
                logger.error(f"Échec création lien: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur création lien: {e}")
            return None
    
    def configure(self, server_url: str, username: str, password: str, 
                  remote_folder: str = '/photovinc'):
        """Configure la connexion NextCloud"""
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.remote_folder = remote_folder
        
        # Sauvegarder
        self._save_credentials()
        
        # Mettre à jour la config du plugin
        self.config.settings['server_url'] = self.server_url
        self.config.settings['username'] = self.username
        self.config.settings['password'] = self.password
        self.config.settings['remote_folder'] = self.remote_folder


# Fonction d'enregistrement
def register_nextcloud_plugin(manager):
    """Enregistre le plugin NextCloud"""
    from plugin_manager import PluginConfig
    
    if "nextcloud" not in manager.plugin_configs:
        manager.plugin_configs["nextcloud"] = PluginConfig(
            name="nextcloud",
            enabled=False,
            priority=15,
            settings={
                "server_url": "",
                "username": "",
                "password": "",
                "remote_folder": "/photovinc",
                "auto_upload": True,
                "create_dated_folders": True
            }
        )
        manager.save_config()
    
    manager.register_plugin("nextcloud", NextCloudPlugin)
    logger.info("NextCloud plugin enregistré")


# Test du plugin
if __name__ == "__main__":
    from plugin_manager import PluginConfig
    
    # Configuration de test
    config = PluginConfig(
        name="nextcloud",
        enabled=True,
        priority=15,
        settings={
            "server_url": "https://votreserveur.com/nextcloud",
            "username": "votre_username",
            "password": "votre_password",
            "remote_folder": "/photovinc",
            "auto_upload": True,
            "create_dated_folders": True
        }
    )
    
    # Créer et tester le plugin
    plugin = NextCloudPlugin(config)
    
    if plugin.initialize():
        print("✓ Connexion NextCloud réussie")
        status = plugin.get_status()
        print(f"Statut: {status}")
        
        # Test upload (à adapter avec un vrai fichier)
        # plugin.upload_file("/path/to/test.jpg")
        
        plugin.shutdown()
    else:
        print("✗ Échec connexion NextCloud")
