#!/usr/bin/env python3
"""
Module de téléchargement de galerie pour photovinc
Permet de télécharger toutes les photos en ZIP
Avec QR code pour téléchargement mobile
"""

import zipfile
import tempfile
import os
from pathlib import Path
from datetime import datetime
import shutil
import tkinter as tk
from PIL import Image, ImageTk


class GalleryDownloader:
    """Gère le téléchargement de la galerie complète"""
    
    def __init__(self, photo_dir, web_server=None, zip_lifetime_minutes=60):
        self.photo_dir = Path(photo_dir)
        self.web_server = web_server
        self.temp_dir = Path(tempfile.gettempdir()) / "photovinc_exports"
        self.temp_dir.mkdir(exist_ok=True)
        self.last_zip_path = None
        self.zip_lifetime_minutes = zip_lifetime_minutes  # Durée de vie des ZIP
        
        # Nettoyer les vieux ZIP au démarrage
        self.cleanup_expired_zips()
    
    def create_zip_archive(self, output_path=None):
        """
        Crée une archive ZIP de toutes les photos
        
        Args:
            output_path: Chemin de sortie (optionnel)
        
        Returns:
            Path: Chemin du fichier ZIP créé
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.temp_dir / f"photovinc_photos_{timestamp}.zip"
        
        output_path = Path(output_path)
        
        # Récupérer toutes les photos
        photos = sorted(self.photo_dir.glob("*.jpg"))
        
        if not photos:
            return None
        
        # Créer l'archive ZIP
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for photo in photos:
                # Ajouter avec le nom de fichier seulement (pas le chemin complet)
                zipf.write(photo, arcname=photo.name)
        
        self.last_zip_path = output_path
        return output_path
    
    def generate_download_qr(self, qr_plugin):
        """
        Génère un QR code pour télécharger le ZIP
        
        Args:
            qr_plugin: Instance du plugin QR code
        
        Returns:
            Path: Chemin du QR code généré
        """
        if not self.last_zip_path or not self.last_zip_path.exists():
            return None
        
        if not self.web_server:
            return None
        
        # Copier le ZIP dans le dossier web pour qu'il soit accessible
        zip_filename = self.last_zip_path.name
        web_zip_path = self.photo_dir / zip_filename
        
        # Copier si pas déjà là
        if not web_zip_path.exists() or web_zip_path != self.last_zip_path:
            shutil.copy2(self.last_zip_path, web_zip_path)
        
        # Générer l'URL de téléchargement
        download_url = f"{self.web_server.get_server_url()}/{zip_filename}"
        
        # Générer le QR code
        qr_output = str(self.temp_dir / "gallery_download_qr.png")
        success = qr_plugin.generate_qr_code(download_url, qr_output)
        
        # generate_qr_code retourne True/False, pas le chemin
        if success:
            return qr_output, download_url
        else:
            return None, None
    
    def get_gallery_stats(self):
        """Retourne les statistiques de la galerie"""
        photos = list(self.photo_dir.glob("*.jpg"))
        
        if not photos:
            return {
                'count': 0,
                'total_size': 0,
                'total_size_mb': 0,
                'oldest': None,
                'newest': None
            }
        
        total_size = sum(p.stat().st_size for p in photos)
        timestamps = [p.stat().st_mtime for p in photos]
        
        return {
            'count': len(photos),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'oldest': datetime.fromtimestamp(min(timestamps)),
            'newest': datetime.fromtimestamp(max(timestamps))
        }
    
    def clean_old_exports(self, keep_last=3):
        """Nettoie les anciennes archives d'export"""
        exports = sorted(
            self.temp_dir.glob("photovinc_photos_*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Garder seulement les N dernières
        for old_export in exports[keep_last:]:
            try:
                old_export.unlink()
            except:
                pass
    
    def cleanup_expired_zips(self):
        """
        Nettoie les ZIP expirés (plus vieux que zip_lifetime_minutes)
        Appelé automatiquement au démarrage et peut être appelé périodiquement
        """
        import time
        
        now = time.time()
        lifetime_seconds = self.zip_lifetime_minutes * 60
        
        cleaned_count = 0
        
        # Nettoyer dans /tmp/photovinc_exports/
        for zip_file in self.temp_dir.glob("photovinc_photos_*.zip"):
            try:
                age_seconds = now - zip_file.stat().st_mtime
                if age_seconds > lifetime_seconds:
                    zip_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                print(f"Erreur nettoyage {zip_file}: {e}")
        
        # Nettoyer aussi dans le dossier photos (copies pour le serveur web)
        for zip_file in self.photo_dir.glob("photovinc_photos_*.zip"):
            try:
                age_seconds = now - zip_file.stat().st_mtime
                if age_seconds > lifetime_seconds:
                    zip_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                print(f"Erreur nettoyage {zip_file}: {e}")
        
        if cleaned_count > 0:
            print(f"🧹 {cleaned_count} archive(s) ZIP expirée(s) nettoyée(s)")
        
        return cleaned_count
    
    def get_zip_expiration_time(self, zip_path):
        """
        Retourne le temps restant avant expiration d'un ZIP
        
        Returns:
            dict: {'expired': bool, 'remaining_minutes': int, 'age_minutes': int}
        """
        import time
        
        if not zip_path or not Path(zip_path).exists():
            return {'expired': True, 'remaining_minutes': 0, 'age_minutes': 0}
        
        now = time.time()
        file_time = Path(zip_path).stat().st_mtime
        age_seconds = now - file_time
        age_minutes = int(age_seconds / 60)
        
        remaining_minutes = max(0, self.zip_lifetime_minutes - age_minutes)
        expired = age_minutes >= self.zip_lifetime_minutes
        
        return {
            'expired': expired,
            'remaining_minutes': remaining_minutes,
            'age_minutes': age_minutes
        }


def integrate_download_in_ui(app_instance):
    """
    Intègre le bouton de téléchargement dans integration_complete.py
    
    Usage: Ajouter dans la méthode show_gallery()
    """
    
    def download_all_photos():
        """Callback pour télécharger toutes les photos"""
        downloader = GalleryDownloader(app_instance.photo_dir, app_instance.web_server)
        
        # Vérifier qu'il y a des photos
        stats = downloader.get_gallery_stats()
        if stats['count'] == 0:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Aucune photo à télécharger")
            return
        
        # Créer la fenêtre de progression
        import tkinter as tk
        progress_win = tk.Toplevel(app_instance.root)
        progress_win.title("Téléchargement")
        progress_win.geometry("400x200")
        progress_win.configure(bg='#2c3e50')
        progress_win.transient(app_instance.root)
        progress_win.grab_set()
        
        # Centrer
        progress_win.update_idletasks()
        x = (progress_win.winfo_screenwidth() // 2) - 200
        y = (progress_win.winfo_screenheight() // 2) - 100
        progress_win.geometry(f"400x200+{x}+{y}")
        
        tk.Label(
            progress_win,
            text="Création de l'archive...",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=30)
        
        info_label = tk.Label(
            progress_win,
            text=f"{stats['count']} photos ({stats['total_size_mb']} MB)",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#3498db'
        )
        info_label.pack(pady=10)
        
        progress_win.update()
        
        # Créer l'archive
        zip_path = downloader.create_zip_archive()
        
        progress_win.destroy()
        
        if zip_path and zip_path.exists():
            # Proposer QR code ou ouvrir dossier
            show_download_options(app_instance, zip_path, downloader, stats)
        else:
            from tkinter import messagebox
            messagebox.showerror("Erreur", "Impossible de créer l'archive")
    
    return download_all_photos


def show_download_options(app_instance, zip_path, downloader, stats):
    """Affiche les options de téléchargement avec QR code"""
    from tkinter import messagebox
    import tkinter as tk
    
    options_win = tk.Toplevel(app_instance.root)
    options_win.title("Archive créée")
    options_win.geometry("600x450")
    options_win.configure(bg='#2c3e50')
    options_win.transient(app_instance.root)
    options_win.grab_set()
    
    # Centrer
    options_win.update_idletasks()
    x = (options_win.winfo_screenwidth() // 2) - 300
    y = (options_win.winfo_screenheight() // 2) - 225
    options_win.geometry(f"600x450+{x}+{y}")
    
    tk.Label(
        options_win,
        text="✅ Archive créée !",
        font=('Arial', 20, 'bold'),
        bg='#2c3e50',
        fg='#2ecc71'
    ).pack(pady=20)
    
    info_frame = tk.Frame(options_win, bg='#34495e', relief=tk.RIDGE, bd=2)
    info_frame.pack(fill=tk.X, padx=30, pady=10)
    
    tk.Label(
        info_frame,
        text=f"📦 {zip_path.name}",
        font=('Arial', 11),
        bg='#34495e',
        fg='#ecf0f1'
    ).pack(pady=5, padx=10)
    
    tk.Label(
        info_frame,
        text=f"📷 {stats['count']} photos • {zip_path.stat().st_size / (1024*1024):.1f} MB",
        font=('Arial', 11),
        bg='#34495e',
        fg='#3498db'
    ).pack(pady=5, padx=10)
    
    tk.Label(
        options_win,
        text="Choisissez une option :",
        font=('Arial', 14, 'bold'),
        bg='#2c3e50',
        fg='#ecf0f1'
    ).pack(pady=15)
    
    btn_frame = tk.Frame(options_win, bg='#2c3e50')
    btn_frame.pack(pady=10)
    
    def show_qr():
        """Affiche le QR code pour téléchargement mobile"""
        qr_plugin = app_instance.plugin_manager.get_plugin("qrcode")
        
        if not qr_plugin or not qr_plugin.is_initialized():
            messagebox.showerror("Erreur", "Plugin QR Code non disponible", parent=options_win)
            return
        
        # Générer le QR code
        result = downloader.generate_download_qr(qr_plugin)
        if not result:
            messagebox.showerror("Erreur", "Impossible de générer le QR code", parent=options_win)
            return
        
        qr_path, download_url = result
        
        if not qr_path or not Path(qr_path).exists():
            messagebox.showerror("Erreur", "QR code introuvable", parent=options_win)
            return
        
        options_win.destroy()
        
        # Afficher le QR code en plein écran
        qr_win = tk.Toplevel(app_instance.root)
        qr_win.title("QR Code - Télécharger ZIP")
        qr_win.configure(bg='white')
        qr_win.attributes('-fullscreen', True)
        
        # Bouton FERMER
        def cleanup_and_close():
            try:
                Path(qr_path).unlink()
            except:
                pass
            qr_win.destroy()
        
        close_btn = tk.Button(
            qr_win,
            text="✕ FERMER",
            font=('Arial', 18, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            height=2,
            command=cleanup_and_close
        )
        close_btn.place(x=850, y=20)
        
        # Titre
        tk.Label(
            qr_win,
            text="📱 SCANNEZ POUR TÉLÉCHARGER",
            font=('Arial', 28, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=30)
        
        # QR Code
        try:
            qr_img = Image.open(qr_path)
            qr_img = qr_img.resize((400, 400), Image.Resampling.LANCZOS)
            qr_photo = ImageTk.PhotoImage(qr_img)
            
            qr_label = tk.Label(qr_win, image=qr_photo, bg='white')
            qr_label.image = qr_photo
            qr_label.pack(pady=20)
        except Exception as e:
            tk.Label(
                qr_win,
                text=f"Erreur: {e}",
                font=('Arial', 14),
                bg='white',
                fg='#e74c3c'
            ).pack(pady=20)
        
        # URL
        tk.Label(
            qr_win,
            text=download_url,
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=10)
        
        # Instructions
        tk.Label(
            qr_win,
            text="Scannez ce QR code avec votre smartphone\npour télécharger toutes les photos en un seul fichier ZIP",
            font=('Arial', 14),
            bg='white',
            fg='#34495e',
            justify=tk.CENTER
        ).pack(pady=20)
        
        # Info taille
        tk.Label(
            qr_win,
            text=f"Taille du téléchargement : {zip_path.stat().st_size / (1024*1024):.1f} MB",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#e67e22'
        ).pack(pady=10)
        
        # Expiration
        expiration = downloader.get_zip_expiration_time(zip_path)
        if not expiration['expired']:
            tk.Label(
                qr_win,
                text=f"⏱️ Ce lien expire dans {expiration['remaining_minutes']} minutes",
                font=('Arial', 11),
                bg='white',
                fg='#e74c3c'
            ).pack(pady=5)
    
    def open_folder():
        """Ouvre le dossier contenant le ZIP"""
        import subprocess
        subprocess.Popen(['xdg-open', str(zip_path.parent)])
        options_win.destroy()
    
    tk.Button(
        btn_frame,
        text="📱 QR Code Mobile",
        font=('Arial', 14, 'bold'),
        bg='#9b59b6',
        fg='white',
        width=18,
        height=2,
        command=show_qr
    ).pack(pady=8)
    
    tk.Button(
        btn_frame,
        text="📁 Ouvrir le dossier",
        font=('Arial', 14, 'bold'),
        bg='#3498db',
        fg='white',
        width=18,
        height=2,
        command=open_folder
    ).pack(pady=8)
    
    tk.Button(
        btn_frame,
        text="Fermer",
        font=('Arial', 12),
        bg='#95a5a6',
        fg='white',
        width=18,
        height=2,
        command=options_win.destroy
    ).pack(pady=8)


# Test standalone
if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("  TEST MODULE TÉLÉCHARGEMENT GALERIE")
    print("="*70 + "\n")
    
    photo_dir = Path.home() / "Photos_photovinc"
    
    if not photo_dir.exists():
        print(f"❌ Dossier introuvable: {photo_dir}")
        sys.exit(1)
    
    downloader = GalleryDownloader(photo_dir)
    
    # Statistiques
    stats = downloader.get_gallery_stats()
    print("📊 Statistiques de la galerie:")
    print(f"   Photos: {stats['count']}")
    print(f"   Taille totale: {stats['total_size_mb']} MB")
    
    if stats['oldest']:
        print(f"   Plus ancienne: {stats['oldest'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Plus récente: {stats['newest'].strftime('%Y-%m-%d %H:%M')}")
    
    if stats['count'] == 0:
        print("\n⚠️  Aucune photo à archiver")
        sys.exit(0)
    
    # Créer l'archive
    print(f"\n📦 Création de l'archive ZIP...")
    zip_path = downloader.create_zip_archive()
    
    if zip_path:
        print(f"✅ Archive créée: {zip_path}")
        print(f"   Taille: {zip_path.stat().st_size / (1024*1024):.1f} MB")
        print(f"\n💡 Pour ouvrir le dossier:")
        print(f"   xdg-open {zip_path.parent}")
    else:
        print("❌ Échec création archive")
    
    # Nettoyage
    print(f"\n🧹 Nettoyage des anciennes archives...")
    downloader.clean_old_exports(keep_last=3)
    print("   ✓ Anciennes archives nettoyées")
    
    print("\n" + "="*70 + "\n")
