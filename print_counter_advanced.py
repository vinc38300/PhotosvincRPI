#!/usr/bin/env python3
"""
Gestionnaire de compteur d'impressions avancé avec :
- Comptage par style de photo
- Réinitialisation complète (compteur + galerie)
- Interface fixée (problème fenêtre noire)
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PrintCounterAdvanced:
    """Gestionnaire avancé du compteur d'impressions"""
    
    def __init__(self, photo_dir=None):
        self.counter_file = Path.home() / ".photovinc_print_counter.json"
        self.password = "admin123"
        self.photo_dir = photo_dir or Path.home() / "Photos_photovinc"
        
        # Compteurs
        self.total_prints = 0
        self.total_photos = 0
        self.photos_by_style = {}
        
        self.load_counter()
    
    def load_counter(self):
        """Charge le compteur depuis le fichier"""
        try:
            if self.counter_file.exists():
                with open(self.counter_file, 'r') as f:
                    data = json.load(f)
                    self.total_prints = data.get('total_prints', 0)
                    self.total_photos = data.get('total_photos', 0)
                    self.photos_by_style = data.get('photos_by_style', {})
                    self.password = data.get('password', 'admin123')
                    
                    # Initialiser les styles par défaut s'ils n'existent pas
                    default_styles = ['polaroid', 'vintage', 'stamp', 'fete', 'normal']
                    for style in default_styles:
                        if style not in self.photos_by_style:
                            self.photos_by_style[style] = 0
            else:
                self._initialize_default()
                
        except Exception as e:
            logger.error(f"Erreur chargement compteur: {e}")
            self._initialize_default()
    
    def _initialize_default(self):
        """Initialise les valeurs par défaut"""
        self.total_prints = 0
        self.total_photos = 0
        self.photos_by_style = {
            'polaroid': 0,
            'vintage': 0,
            'stamp': 0,
            'fete': 0,
            'normal': 0
        }
        self.save_counter()
    
    def save_counter(self):
        """Sauvegarde le compteur dans le fichier"""
        try:
            data = {
                'total_prints': self.total_prints,
                'total_photos': self.total_photos,
                'photos_by_style': self.photos_by_style,
                'password': self.password,
                'last_update': datetime.now().isoformat()
            }
            with open(self.counter_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde compteur: {e}")
    
    def increment_print(self):
        """Incrémente le compteur d'impressions"""
        self.total_prints += 1
        self.save_counter()
        logger.info(f"Impression #{self.total_prints}")
    
    def increment_photo(self, style='normal'):
        """Incrémente le compteur de photos par style"""
        self.total_photos += 1
        
        if style not in self.photos_by_style:
            self.photos_by_style[style] = 0
        
        self.photos_by_style[style] += 1
        self.save_counter()
        logger.info(f"Photo {style} #{self.photos_by_style[style]}")
    
    def increment_session(self, num_photos, style='normal'):
        """Incrémente une session complète"""
        for _ in range(num_photos):
            self.increment_photo(style)
    
    def get_stats(self):
        """Retourne les statistiques complètes"""
        return {
            'total_prints': self.total_prints,
            'total_photos': self.total_photos,
            'photos_by_style': self.photos_by_style.copy(),
            'most_used_style': self._get_most_used_style(),
            'least_used_style': self._get_least_used_style()
        }
    
    def _get_most_used_style(self):
        """Retourne le style le plus utilisé"""
        if not self.photos_by_style:
            return "N/A"
        return max(self.photos_by_style.items(), key=lambda x: x[1])[0]
    
    def _get_least_used_style(self):
        """Retourne le style le moins utilisé"""
        if not self.photos_by_style:
            return "N/A"
        return min(self.photos_by_style.items(), key=lambda x: x[1])[0]
    
    def clear_gallery(self):
        """Vide le dossier galerie"""
        try:
            if not self.photo_dir.exists():
                logger.warning(f"Dossier galerie inexistant: {self.photo_dir}")
                return True
            
            # Compter les fichiers avant suppression
            photo_files = list(self.photo_dir.glob("*.jpg"))
            count = len(photo_files)
            
            # Supprimer tous les fichiers .jpg
            for photo in photo_files:
                try:
                    photo.unlink()
                except Exception as e:
                    logger.error(f"Erreur suppression {photo.name}: {e}")
            
            logger.info(f"Galerie vidée : {count} photos supprimées")
            return True
            
        except Exception as e:
            logger.error(f"Erreur vidage galerie: {e}")
            return False
    
    def backup_gallery(self, backup_dir=None):
        """Sauvegarde la galerie avant réinitialisation"""
        try:
            if backup_dir is None:
                backup_dir = Path.home() / "Photos_photovinc_Backup"
            
            # Créer un dossier de backup avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copier tous les fichiers
            if self.photo_dir.exists():
                for photo in self.photo_dir.glob("*.jpg"):
                    shutil.copy2(photo, backup_path / photo.name)
            
            logger.info(f"Backup créé : {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Erreur backup galerie: {e}")
            return None
    
    def reset(self, password, clear_photos=False, create_backup=True):
        """Réinitialise le compteur (et optionnellement la galerie)"""
        if password != self.password:
            logger.warning("Tentative de réinitialisation avec mauvais mot de passe")
            return False, "Mot de passe incorrect"
        
        try:
            # Backup avant suppression si demandé
            backup_path = None
            if clear_photos and create_backup:
                backup_path = self.backup_gallery()
                if backup_path is None:
                    return False, "Erreur lors du backup"
            
            # Réinitialiser les compteurs
            self.total_prints = 0
            self.total_photos = 0
            for style in self.photos_by_style:
                self.photos_by_style[style] = 0
            
            self.save_counter()
            
            # Vider la galerie si demandé
            if clear_photos:
                if not self.clear_gallery():
                    return False, "Erreur lors du vidage de la galerie"
            
            message = "Compteur réinitialisé"
            if clear_photos:
                if backup_path:
                    message += f"\nGalerie vidée (backup : {backup_path})"
                else:
                    message += "\nGalerie vidée"
            
            logger.info(f"Réinitialisation complète effectuée")
            return True, message
            
        except Exception as e:
            logger.error(f"Erreur réinitialisation: {e}")
            return False, f"Erreur : {str(e)}"
    
    def change_password(self, old_password, new_password):
        """Change le mot de passe"""
        if old_password != self.password:
            return False
        
        if len(new_password) < 4:
            return False
        
        self.password = new_password
        self.save_counter()
        logger.info("Mot de passe modifié")
        return True
    
    def get_gallery_info(self):
        """Retourne des infos sur la galerie"""
        try:
            if not self.photo_dir.exists():
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'oldest': None,
                    'newest': None
                }
            
            photo_files = list(self.photo_dir.glob("*.jpg"))
            
            if not photo_files:
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'oldest': None,
                    'newest': None
                }
            
            # Calculer la taille totale
            total_size = sum(f.stat().st_size for f in photo_files)
            
            # Dates
            oldest = min(photo_files, key=lambda f: f.stat().st_mtime)
            newest = max(photo_files, key=lambda f: f.stat().st_mtime)
            
            return {
                'total_files': len(photo_files),
                'total_size': total_size,
                'total_size_mb': f"{total_size / (1024*1024):.2f} MB",
                'oldest': datetime.fromtimestamp(oldest.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
                'newest': datetime.fromtimestamp(newest.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            }
            
        except Exception as e:
            logger.error(f"Erreur info galerie: {e}")
            return {'total_files': 0, 'total_size': 0, 'oldest': None, 'newest': None}


# Test du module
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    counter = PrintCounterAdvanced()
    
    print("\n=== Test PrintCounterAdvanced ===\n")
    
    # Simuler quelques photos
    counter.increment_session(4, 'polaroid')
    counter.increment_session(4, 'vintage')
    counter.increment_photo('fete')
    
    # Simuler des impressions
    counter.increment_print()
    counter.increment_print()
    
    # Afficher les stats
    stats = counter.get_stats()
    print(f"Total impressions : {stats['total_prints']}")
    print(f"Total photos : {stats['total_photos']}")
    print(f"Style le plus utilisé : {stats['most_used_style']}")
    print("\nPhotos par style :")
    for style, count in stats['photos_by_style'].items():
        print(f"  {style}: {count}")
    
    # Info galerie
    gallery_info = counter.get_gallery_info()
    print(f"\nGalerie : {gallery_info['total_files']} fichiers")
    print(f"Taille : {gallery_info['total_size_mb']}")
