#!/usr/bin/env python3
"""
Script de correction automatique pour photovinc
Corrige automatiquement les problèmes de fenêtres au premier plan
"""

import re
import sys
from pathlib import Path
import shutil
from datetime import datetime


class PhotovincAutoFix:
    """Correcteur automatique de code photovinc"""
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.backup_path = None
        self.corrections_made = []
        
    def backup_file(self):
        """Crée une sauvegarde du fichier original"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.file_path.with_suffix(f'.backup_{timestamp}.py')
        shutil.copy2(self.file_path, self.backup_path)
        print(f"✅ Sauvegarde créée: {self.backup_path}")
    
    def read_file(self):
        """Lit le contenu du fichier"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, content):
        """Écrit le contenu corrigé"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def fix_window_z_order(self, content):
        """Corrige les problèmes d'ordre Z des fenêtres Toplevel"""
        patterns = [
            # Pattern 1: show_zip_download_options
            {
                'name': 'show_zip_download_options - Z-order',
                'search': r"(def show_zip_download_options\(self, zip_path, stats\):.*?options_win\.configure\(bg='#2c3e50'\))\s*options_win\.transient\(self\.root\)\s*(.*?# Centrer.*?options_win\.geometry\(f\"600x500\+\{x\}\+\{y\}\"\))\s*.*?options_win\.grab_set\(\)",
                'replace': r"\1\n        \n        \2\n        \n        # Forcer au premier plan\n        options_win.lift()\n        options_win.focus_force()\n        options_win.grab_set()",
                'flags': re.DOTALL
            },
            
            # Pattern 2: Autres fenêtres Toplevel avec transient
            {
                'name': 'Fenêtres Toplevel génériques',
                'search': r"(\w+_win = tk\.Toplevel\(.*?\).*?\.configure\(bg='[^']+'\))\s*\1\.transient\(.*?\)\s*(\1\.grab_set\(\))",
                'replace': r"\1\n        \1.lift()\n        \1.focus_force()\n        \2",
                'flags': re.MULTILINE
            }
        ]
        
        modified = content
        for pattern in patterns:
            if re.search(pattern['search'], modified, pattern['flags']):
                modified = re.sub(
                    pattern['search'], 
                    pattern['replace'], 
                    modified, 
                    flags=pattern['flags']
                )
                self.corrections_made.append(pattern['name'])
        
        return modified
    
    def fix_show_gallery_download_button(self, content):
        """Corrige le bouton de téléchargement dans show_gallery"""
        pattern = r"(tk\.Button\(\s*title_frame,\s*text=\"Fermer\".*?\.pack\(side=tk\.RIGHT.*?\))"
        
        if re.search(pattern, content, re.DOTALL):
            # Chercher si le bouton télécharger existe déjà
            if "Télécharger ZIP" not in content:
                replacement = r'''tk.Button(
            title_frame,
            text="📦 Télécharger ZIP",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            width=16,
            command=self.download_gallery
        ).pack(side=tk.RIGHT, padx=10, pady=10)
        
        \1'''
                
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                self.corrections_made.append("Ajout bouton Télécharger ZIP dans galerie")
        
        return content
    
    def fix_import_gallery_download(self, content):
        """Vérifie et ajoute l'import de gallery_download si manquant"""
        if "from gallery_download import GalleryDownloader" not in content:
            # Trouver la zone des imports
            import_section = re.search(
                r"(from photo_web_server import.*?\n)", 
                content
            )
            
            if import_section:
                insertion_point = import_section.end()
                content = (
                    content[:insertion_point] +
                    "from gallery_download import GalleryDownloader\n" +
                    content[insertion_point:]
                )
                self.corrections_made.append("Ajout import GalleryDownloader")
        
        return content
    
    def fix_gallery_downloader_init(self, content):
        """Vérifie l'initialisation de GalleryDownloader dans __init__"""
        if "self.gallery_downloader = GalleryDownloader" not in content:
            # Chercher après web_server
            pattern = r"(self\.web_server = PhotoWebServer\(port=8000\))"
            
            if re.search(pattern, content):
                replacement = r'''\1
        
        # Gestionnaire de téléchargement de galerie
        self.gallery_downloader = GalleryDownloader(self.photo_dir, self.web_server)'''
                
                content = re.sub(pattern, replacement, content)
                self.corrections_made.append("Ajout initialisation gallery_downloader")
        
        return content
    
    def fix_all(self):
        """Applique toutes les corrections"""
        print("\n" + "="*60)
        print("  PHOTOVINC AUTO-FIX")
        print("="*60 + "\n")
        
        if not self.file_path.exists():
            print(f"❌ Fichier introuvable: {self.file_path}")
            return False
        
        print(f"📄 Fichier: {self.file_path}")
        
        # Sauvegarde
        self.backup_file()
        
        # Lecture
        print("📖 Lecture du fichier...")
        content = self.read_file()
        
        # Corrections
        print("\n🔧 Application des corrections...\n")
        
        content = self.fix_import_gallery_download(content)
        content = self.fix_gallery_downloader_init(content)
        content = self.fix_window_z_order(content)
        content = self.fix_show_gallery_download_button(content)
        
        # Écriture
        if self.corrections_made:
            print("💾 Écriture des corrections...")
            self.write_file(content)
            
            print("\n✅ Corrections appliquées:\n")
            for i, correction in enumerate(self.corrections_made, 1):
                print(f"   {i}. {correction}")
            
            print(f"\n📦 Backup: {self.backup_path}")
            print(f"✨ Fichier corrigé: {self.file_path}")
            return True
        else:
            print("ℹ️  Aucune correction nécessaire")
            # Supprimer le backup si aucune modification
            self.backup_path.unlink()
            return True


def main():
    print("\n🔧 Script de correction automatique photovinc\n")
    
    # Fichier par défaut
    default_file = Path("integration_complete.py")
    
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        file_path = default_file
    
    print(f"Fichier cible: {file_path}\n")
    
    # Demander confirmation
    response = input("Continuer avec ce fichier? [O/n]: ").strip().lower()
    if response and response not in ['o', 'oui', 'y', 'yes']:
        print("❌ Annulé par l'utilisateur")
        return
    
    # Correction
    fixer = PhotovincAutoFix(file_path)
    success = fixer.fix_all()
    
    if success:
        print("\n" + "="*60)
        print("  ✅ CORRECTIONS TERMINÉES AVEC SUCCÈS")
        print("="*60)
        print("\n💡 Pour tester:")
        print(f"   python3 {file_path}")
    else:
        print("\n❌ Échec des corrections")
        sys.exit(1)


if __name__ == "__main__":
    main()
