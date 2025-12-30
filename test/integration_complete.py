#!/usr/bin/env python3
"""
Interface photovinc COMPLÈTE - Version Finale Améliorée
- Sélection photos intégrée et compacte
- Actions Imprimer/QR Code comme dans la galerie
- Compteur avancé avec statistiques par style
- Réinitialisation avec vidage galerie
- Interface corrigée (plus de fenêtre noire)
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
from datetime import datetime
from pathlib import Path
import time
import json

from camera_printer_real import register_real_plugins
from decorator_real import register_real_decorator
from plugin_manager import PluginManager, WiFiPlugin, KeyboardPlugin
from wifi_config_ui import WiFiConfigDialog
from photo_web_server import PhotoWebServer
from qr_code_plugin import QRCodePlugin, register_qr_plugin
from nextcloud_plugin import NextCloudPlugin, register_nextcloud_plugin
from nextcloud_ui import NextCloudConfigUI, integrate_nextcloud_features

# Nouveaux imports pour le compteur avancé
from print_counter_advanced import PrintCounterAdvanced

# Imports pour détection d'imprimante automatique
from printer_detection import (
    PrinterIntegration, 
    PrinterDetector,
    setup_printer_detection
)
from print_counter_ui import show_print_counter_dialog


class PrinterDiagnostic:
    """Diagnostic détaillé de l'imprimante"""
    
    @staticmethod
    def get_detailed_status(printer_plugin):
        """Retourne un diagnostic complet"""
        if not printer_plugin or not printer_plugin.is_initialized():
            return {
                'status': 'non_disponible',
                'message': 'Imprimante non détectée',
                'color': '#e74c3c',
                'solutions': [
                    'Vérifier le branchement USB',
                    'Allumer l\'imprimante',
                    'Redémarrer l\'application'
                ]
            }
        
        status_ok, status_msg = printer_plugin.check_printer_status()
        jobs_count = printer_plugin._get_jobs_count()
        
        if status_msg == "Prête" and jobs_count == 0:
            return {'status': 'prete', 'message': 'Imprimante prête', 'color': '#2ecc71', 'solutions': []}
        elif status_msg == "Impression...":
            return {'status': 'impression', 'message': f'Impression en cours ({jobs_count} job(s))', 'color': '#3498db', 'solutions': ['Attendre la fin de l\'impression']}
        elif status_msg == "Job bloqué":
            return {'status': 'bloque', 'message': 'Job d\'impression bloqué', 'color': '#e67e22', 'solutions': ['1. Cliquer sur "Annuler jobs"', '2. Si ça persiste, cliquer "Reset"', '3. Vérifier le papier']}
        elif status_msg == "Mauvais papier":
            return {'status': 'papier', 'message': 'Format de papier incorrect', 'color': '#e74c3c', 'solutions': ['Charger du papier Postcard (10x15cm)', 'Vérifier le bac papier', 'Cliquer sur "Reset"']}
        elif status_msg == "Non connectée":
            return {'status': 'deconnecte', 'message': 'Imprimante déconnectée', 'color': '#e74c3c', 'solutions': ['Vérifier le câble USB', 'Rallumer l\'imprimante', 'Cliquer sur "Reset"']}
        elif status_msg == "Désactivée":
            return {'status': 'desactive', 'message': 'Imprimante désactivée', 'color': '#e67e22', 'solutions': ['Cliquer sur "Reset"', 'Vérifier CUPS']}
        elif status_msg == "En pause":
            return {'status': 'pause', 'message': 'Imprimante en pause', 'color': '#f39c12', 'solutions': ['Cliquer sur "Reset"']}
        else:
            return {'status': 'erreur', 'message': f'Erreur: {status_msg}', 'color': '#e74c3c', 'solutions': ['Cliquer sur "Reset"', 'Vérifier /var/log/cups/error_log', 'Redémarrer l\'application']}


class photovincAppComplete:
    """Application photovinc complète"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("photovinc")
        self.root.geometry("1024x600")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        
        # ✅ NOUVEAU : Compteur avancé avec statistiques
        self.photo_dir = Path.home() / "Photos_photovinc"
        self.photo_dir.mkdir(exist_ok=True)
        self.print_counter = PrintCounterAdvanced(photo_dir=self.photo_dir)
        # ✅ Initialisation printer_integration
        self.printer_integration = None
        
        # Initialiser le gestionnaire de plugins
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_config()
        self.register_all_plugins()
        # Serveur web pour QR codes
        self.web_server = PhotoWebServer(port=8000)
        
        # Variables de l'application
        self.current_style = "Normal"
        self.is_capturing = False
        self.last_session_photos = []
        
        # Styles disponibles
        self.styles_list = [
            ("normal", "Normal", "#3498db"),
            ("polaroid", "Polaroid", "#9b59b6"),
            ("vintage", "Vintage", "#e67e22"),
            ("stamp", "Timbre", "#e74c3c"),
            ("fete", "Fête", "#f39c12"),
            
        ]
        
        self.setup_ui()
        
        # Mettre à jour le statut imprimante après setup_ui
        self.root.after(1000, self.update_printer_status_label)
        
        self.initialize_plugins()
        self.show_welcome_screen()
    
    def register_all_plugins(self):
        """Enregistre tous les plugins"""
        register_real_plugins(self.plugin_manager)
        register_real_decorator(self.plugin_manager)
        register_qr_plugin(self.plugin_manager)
        register_nextcloud_plugin(self.plugin_manager)
        
        from plugin_manager import PluginConfig
        
        if "wifi" not in self.plugin_manager.plugin_configs:
            self.plugin_manager.plugin_configs["wifi"] = PluginConfig(
                name="wifi", enabled=True, priority=4, settings={}
            )
        
        if "keyboard" not in self.plugin_manager.plugin_configs:
            self.plugin_manager.plugin_configs["keyboard"] = PluginConfig(
                name="keyboard", enabled=True, priority=5, settings={}
            )
        
        self.plugin_manager.register_plugin("wifi", WiFiPlugin)
        self.plugin_manager.register_plugin("keyboard", KeyboardPlugin)
    
    def initialize_plugins(self):
        """Initialise tous les plugins"""
        self.show_message("Initialisation...", '#f39c12', 14)
        self.root.update()
        
        # ✅ CORRECTION: Détection d'imprimante AVANT initialisation des plugins
        self.printer_integration = PrinterIntegration(self.plugin_manager)
        printer_success, printer_msg = self.printer_integration.initialize()
        
        # Afficher les détails de détection
        if printer_success and self.printer_integration.selected_printer:
            printer_info = self.printer_integration.get_printer_info()
            print(f"\n✓ Imprimante sélectionnée: {printer_info['name']}")
            print(f"  Modèle: {printer_info['model']}")
            print(f"  Statut: {printer_info['status']}")
            print(f"  Connexion: {'🟢 Physique' if printer_info['is_physically_connected'] else '🔴 Déconnectée'}")
        else:
            print(f"\n⚠ {printer_msg} - Mode démo activé")
        
        # Maintenant initialiser tous les plugins (avec la bonne config imprimante)
        results = self.plugin_manager.initialize_all()
        failed = [name for name, success in results.items() if not success]
        if failed:
            print(f"Plugins non initialisés: {', '.join(failed)}")
        
        # Vérifier que le plugin printer utilise la bonne imprimante
        printer_plugin = self.plugin_manager.get_plugin("printer")
        if printer_plugin and printer_plugin.is_initialized():
            print(f"✓ Plugin printer configuré: {printer_plugin.printer_name}")
        else:
            print("⚠ Plugin printer non disponible")
        
        # Démarrer le serveur web
        if self.web_server.start():
            print(f"Serveur web démarré: {self.web_server.get_server_url()}")
        
        self.show_message("Prêt !", '#2ecc71', 14)
        time.sleep(1)
    
    def show_welcome_screen(self):
        """Affiche le logo de bienvenue"""
        try:
            decorator = self.plugin_manager.get_plugin("decorator")
            if decorator and decorator.is_initialized():
                logo = decorator.create_logo()
                logo.thumbnail((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(logo)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
        except Exception as e:
            print(f"Erreur logo: {e}")
            self.show_message("Prêt !", '#ecf0f1', 14)
    
    def setup_ui(self):
        """Configure l'interface"""
        # Barre de titre
        title_frame = tk.Frame(self.root, bg='#34495e', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="PHOTOVINC",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=20, pady=8)
        
        # Statut imprimante
        self.printer_status_label = tk.Label(
            title_frame,
            text="Vérification...",
            font=('Arial', 11),
            bg='#34495e',
            fg='#95a5a6',
            cursor="hand2"
        )
        self.printer_status_label.pack(side=tk.LEFT, padx=20)
        self.printer_status_label.bind('<Button-1>', self.show_printer_diagnostic)
        
        # Statut serveur
        self.server_status_label = tk.Label(
            title_frame,
            text="Serveur: OK",
            font=('Arial', 11),
            bg='#34495e',
            fg='#2ecc71',
            cursor="hand2"
        )
        self.server_status_label.pack(side=tk.LEFT, padx=10)
        self.server_status_label.bind('<Button-1>', self.show_server_info)
        
        # ✅ NOUVEAU : Affichage compteur avancé
        counter_frame = tk.Frame(title_frame, bg='#34495e')
        counter_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            counter_frame,
            text="🖨️",
            font=('Arial', 16),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        self.counter_label = tk.Label(
            counter_frame,
            text=str(self.print_counter.total_prints),
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='#e74c3c',
            cursor="hand2"
        )
        self.counter_label.pack(side=tk.LEFT)
        self.counter_label.bind('<Button-1>', self.show_counter_dialog)
        
        tk.Label(
            counter_frame,
            text="📷",
            font=('Arial', 16),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=(15, 5))
        
        self.photos_label = tk.Label(
            counter_frame,
            text=str(self.print_counter.total_photos),
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='#3498db',
            cursor="hand2"
        )
        self.photos_label.pack(side=tk.LEFT)
        self.photos_label.bind('<Button-1>', self.show_counter_dialog)
        
        # Conteneur principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de prévisualisation
        preview_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.RIDGE, bd=2)
        preview_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.preview_label = tk.Label(
            preview_frame,
            text="Prêt !",
            font=('Arial', 18, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panneau de contrôle
        control_frame = tk.Frame(main_frame, bg='#2c3e50', width=340)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        control_frame.pack_propagate(False)
        
        # BOUTON CHOIX STYLE
        self.style_display = tk.StringVar(value="Normal")
        
        tk.Button(
            control_frame,
            textvariable=self.style_display,
            font=('Arial', 14, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=26,
            height=2,
            command=self.open_style_selector
        ).pack(pady=8, padx=10)
        
        # Séparateur
        tk.Frame(control_frame, bg='#95a5a6', height=2).pack(fill=tk.X, pady=8)
        
        # BOUTONS PRINCIPAUX
        tk.Button(
            control_frame,
            text="TEST PHOTO",
            font=('Arial', 13, 'bold'),
            bg='#3498db',
            fg='white',
            width=26,
            height=2,
            command=self.test_photo
        ).pack(pady=6, padx=10)
        
        self.start_btn = tk.Button(
            control_frame,
            text="PRENDRE 4 PHOTOS",
            font=('Arial', 15, 'bold'),
            bg='#27ae60',
            fg='white',
            width=26,
            height=3,
            command=self.take_four_photos
        )
        self.start_btn.pack(pady=6, padx=10)
        
        tk.Button(
            control_frame,
            text="GALERIE",
            font=('Arial', 13, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=26,
            height=2,
            command=self.show_gallery
        ).pack(pady=6, padx=10)
        
        # Séparateur
        tk.Frame(control_frame, bg='#95a5a6', height=2).pack(fill=tk.X, pady=8)
        
        # BOUTONS MAINTENANCE
        maint_frame = tk.Frame(control_frame, bg='#2c3e50')
        maint_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Button(
            maint_frame,
            text="Diagnostic",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            height=2,
            command=self.show_printer_diagnostic
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            maint_frame,
            text="Annuler Jobs",
            font=('Arial', 10, 'bold'),
            bg='#e67e22',
            fg='white',
            width=12,
            height=2,
            command=self.cancel_print_jobs
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            maint_frame,
            text="Reset",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            height=2,
            command=self.reset_printer
        ).pack(side=tk.LEFT, padx=2)
        
        # BOUTONS WiFi, QR et NextCloud
        net_frame = tk.Frame(control_frame, bg='#2c3e50')
        net_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Button(
            net_frame,
            text="WiFi",
            font=('Arial', 10, 'bold'),
            bg='#16a085',
            fg='white',
            width=12,
            height=2,
            command=self.show_wifi_config
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            net_frame,
            text="QR Code",
            font=('Arial', 10, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=12,
            height=2,
            command=self.show_qr_selection
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            net_frame,
            text="NextCloud",
            font=('Arial', 10, 'bold'),
            bg='#e67e22',
            fg='white',
            width=12,
            height=2,
            command=self.show_nextcloud_menu
        ).pack(side=tk.LEFT, padx=2)
        
        # Bouton quitter
        tk.Button(
            control_frame,
            text="Quitter",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#7f8c8d',
            relief=tk.FLAT,
            command=self.quit_app
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Mise à jour périodique du statut
        self.update_printer_status()
    
    def open_style_selector(self):
        """Ouvre la fenêtre de sélection de style"""
        selector_win = tk.Toplevel(self.root)
        selector_win.title("Choisir un style")
        selector_win.geometry("500x600")
        selector_win.configure(bg='#2c3e50')
        selector_win.transient(self.root)
        selector_win.grab_set()
        
        # Centrer
        selector_win.update_idletasks()
        x = (selector_win.winfo_screenwidth() // 2) - 250
        y = (selector_win.winfo_screenheight() // 2) - 300
        selector_win.geometry(f"500x600+{x}+{y}")
        
        tk.Label(
            selector_win,
            text="CHOISISSEZ UN STYLE",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        # Boutons des styles
        for style_id, style_name, color in self.styles_list:
            is_selected = (style_id == self.current_style)
            
            btn = tk.Button(
                selector_win,
                text=style_name,
                font=('Arial', 14, 'bold'),
                bg=color if is_selected else '#34495e',
                fg='white',
                width=32,
                height=3,
                relief=tk.RAISED if is_selected else tk.FLAT,
                command=lambda sid=style_id, sname=style_name: self.select_style(sid, sname, selector_win)
            )
            btn.pack(pady=6, padx=20)
        
        tk.Button(
            selector_win,
            text="Fermer",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=20,
            command=selector_win.destroy
        ).pack(pady=20)
    
    def select_style(self, style_id, style_name, window):
        """Sélectionne un style"""
        self.current_style = style_id
        self.style_display.set(style_name)
        self.show_message(f"Style: {style_name}", '#2ecc71', 16, timeout=2)
        window.destroy()
    
    def show_gallery(self):
        """Affiche la galerie de photos"""
        photos = sorted(self.photo_dir.glob("*.jpg"), reverse=True)[:20]
        
        if not photos:
            messagebox.showinfo("Galerie", "Aucune photo dans la galerie")
            return
        
        gallery_win = tk.Toplevel(self.root)
        gallery_win.title("Galerie Photos")
        gallery_win.geometry("900x550")
        gallery_win.configure(bg='#2c3e50')
        gallery_win.transient(self.root)
        
        # Centrer
        gallery_win.update_idletasks()
        x = (gallery_win.winfo_screenwidth() // 2) - 450
        y = (gallery_win.winfo_screenheight() // 2) - 275
        gallery_win.geometry(f"900x550+{x}+{y}")
        
        # Titre
        title_frame = tk.Frame(gallery_win, bg='#34495e')
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text=f"GALERIE ({len(photos)} photos)",
            font=('Arial', 18, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Button(
            title_frame,
            text="Fermer",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            command=gallery_win.destroy
        ).pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Frame avec scroll
        canvas = tk.Canvas(gallery_win, bg='#2c3e50', highlightthickness=0)
        scrollbar = tk.Scrollbar(gallery_win, orient="vertical", command=canvas.yview, width=25)
        scrollable_frame = tk.Frame(canvas, bg='#2c3e50')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Afficher les miniatures (4 par ligne)
        for idx, photo_path in enumerate(photos):
            row = idx // 4
            col = idx % 4
            
            frame = tk.Frame(scrollable_frame, bg='#34495e', relief=tk.RAISED, bd=2)
            frame.grid(row=row, column=col, padx=8, pady=8)
            
            try:
                img = Image.open(photo_path)
                img.thumbnail((180, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                btn = tk.Button(
                    frame,
                    image=photo,
                    command=lambda p=photo_path: self.show_photo_actions(p, gallery_win),
                    cursor="hand2",
                    bg='#34495e'
                )
                btn.image = photo
                btn.pack(padx=3, pady=3)
                
                # Nom du fichier
                filename = photo_path.name[:30] + "..." if len(photo_path.name) > 30 else photo_path.name
                tk.Label(
                    frame,
                    text=filename,
                    font=('Arial', 8),
                    bg='#34495e',
                    fg='#ecf0f1'
                ).pack(pady=3)
            except:
                pass
    
    def show_photo_actions(self, photo_path, parent_win):
        """Affiche les actions possibles pour une photo"""
        actions_win = tk.Toplevel(parent_win)
        actions_win.title("Actions")
        actions_win.geometry("400x350")
        actions_win.configure(bg='#2c3e50')
        actions_win.transient(parent_win)
        actions_win.grab_set()
        
        # Centrer
        actions_win.update_idletasks()
        x = (actions_win.winfo_screenwidth() // 2) - 200
        y = (actions_win.winfo_screenheight() // 2) - 175
        actions_win.geometry(f"400x350+{x}+{y}")
        
        # Afficher la photo
        try:
            img = Image.open(photo_path)
            img.thumbnail((350, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = tk.Label(actions_win, image=photo, bg='#2c3e50')
            label.image = photo
            label.pack(pady=10)
        except:
            pass
        
        # Boutons d'actions
        btn_frame = tk.Frame(actions_win, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Imprimer",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=15,
            command=lambda: [self.print_photo_from_gallery(photo_path), actions_win.destroy()]
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="QR Code",
            font=('Arial', 11, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=15,
            command=lambda: [actions_win.destroy(), self.generate_qr_for_photo(photo_path)]
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Supprimer",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=15,
            command=lambda: self.delete_photo(photo_path, actions_win, parent_win)
        ).pack(pady=5)
        
        tk.Button(
            btn_frame,
            text="Fermer",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=actions_win.destroy
        ).pack(pady=5)
    
    def print_photo_from_gallery(self, photo_path):
        """Imprime une photo depuis la galerie - ✅ SUPPORT IPP + USB"""
        printer = self.plugin_manager.get_plugin("printer")
        if printer and printer.is_initialized():
            success = False
            
            # ✅ SMART: Utiliser IPP si réseau, sinon USB classique
            if hasattr(self, 'printer_integration') and self.printer_integration.selected_printer:
                ipp_printer = self.printer_integration.selected_printer.ipp_printer
                
                if ipp_printer:
                    # Imprimante réseau IPP/IPPS
                    print(f"🌐 Impression IPP (réseau): {photo_path}")
                    success = ipp_printer.print_image(str(photo_path))
                else:
                    # Imprimante USB ou autre (méthode classique)
                    print(f"🖨️  Impression USB/classique: {photo_path}")
                    success = printer.print_image(str(photo_path))
            else:
                # Pas d'intégration, méthode classique
                success = printer.print_image(str(photo_path))
            
            if success:
                # ✅ INCRÉMENTER LE COMPTEUR D'IMPRESSIONS
                self.print_counter.increment_print()
                
                # ✅ METTRE À JOUR L'AFFICHAGE
                self.counter_label.config(text=str(self.print_counter.total_prints))
                
                messagebox.showinfo("Succès", "Photo envoyée à l'imprimante")
            else:
                messagebox.showerror("Erreur", "Échec d'impression")
        else:
            messagebox.showerror("Erreur", "Imprimante non disponible")
    
    def delete_photo(self, photo_path, actions_win, gallery_win):
        """Supprime une photo"""
        if messagebox.askyesno("Confirmer", "Supprimer cette photo ?", parent=actions_win):
            try:
                os.remove(photo_path)
                messagebox.showinfo("Succès", "Photo supprimée", parent=actions_win)
                actions_win.destroy()
                gallery_win.destroy()
                self.show_gallery()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer:\n{e}", parent=actions_win)
    
    def show_qr_selection(self):
        """Affiche l'interface de sélection pour QR Code"""
        if not self.last_session_photos:
            messagebox.showinfo("Info", "Prenez d'abord des photos\nou allez dans la Galerie")
            return
        
        qr_select_win = tk.Toplevel(self.root)
        qr_select_win.title("QR Code - Sélection")
        qr_select_win.geometry("650x450")
        qr_select_win.configure(bg='#2c3e50')
        qr_select_win.transient(self.root)
        qr_select_win.grab_set()
        
        # Centrer
        qr_select_win.update_idletasks()
        x = (qr_select_win.winfo_screenwidth() // 2) - 325
        y = (qr_select_win.winfo_screenheight() // 2) - 225
        qr_select_win.geometry(f"650x450+{x}+{y}")
        
        tk.Label(
            qr_select_win,
            text="CHOISIR UNE PHOTO À PARTAGER",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=15)
        
        thumbs_frame = tk.Frame(qr_select_win, bg='#2c3e50')
        thumbs_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        for idx, photo_path in enumerate(self.last_session_photos[:4]):
            col = idx % 2
            row = idx // 2
            
            frame = tk.Frame(thumbs_frame, bg='#34495e', relief=tk.RAISED, bd=3)
            frame.grid(row=row, column=col, padx=10, pady=10)
            
            try:
                img = Image.open(photo_path)
                img.thumbnail((280, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                btn = tk.Button(
                    frame,
                    image=photo,
                    command=lambda p=photo_path: [qr_select_win.destroy(), self.generate_qr_for_photo(p)],
                    cursor="hand2"
                )
                btn.image = photo
                btn.pack(padx=5, pady=5)
            except:
                pass
        
        tk.Button(
            qr_select_win,
            text="Annuler",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=qr_select_win.destroy
        ).pack(pady=10)
    
    def generate_qr_for_photo(self, photo_path):
        """Génère et affiche un QR code pour une photo"""
        qr_plugin = self.plugin_manager.get_plugin("qrcode")
        
        if not qr_plugin or not qr_plugin.is_initialized():
            messagebox.showerror("Erreur", "Plugin QR Code non disponible\nInstallez: pip install qrcode[pil]")
            return
        
        # Mettre à jour l'URL du serveur
        qr_plugin.server_url = self.web_server.get_server_url()
        
        # Générer le QR code
        qr_output = str(Path(photo_path).parent / "temp_qr.png")
        qr_path = qr_plugin.generate_qr_for_photo(str(photo_path), qr_output)
        
        if not qr_path or not os.path.exists(qr_path):
            messagebox.showerror("Erreur", "Impossible de générer le QR code")
            return
        
        # Afficher le QR code en plein écran
        qr_win = tk.Toplevel(self.root)
        qr_win.title("QR Code")
        qr_win.configure(bg='white')
        qr_win.attributes('-fullscreen', True)
        
        # Bouton FERMER très visible
        close_btn = tk.Button(
            qr_win,
            text="✕ FERMER",
            font=('Arial', 18, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            height=2,
            command=lambda: [os.remove(qr_path), qr_win.destroy()]
        )
        close_btn.place(x=850, y=20)
        
        # Titre
        tk.Label(
            qr_win,
            text="SCANNEZ CE QR CODE",
            font=('Arial', 28, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=30)
        
        # Afficher le QR code
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
                text=f"Erreur affichage QR: {e}",
                font=('Arial', 14),
                bg='white',
                fg='#e74c3c'
            ).pack(pady=20)
        
        # URL à afficher
        url = qr_plugin.get_photo_url(photo_path)
        tk.Label(
            qr_win,
            text=f"URL: {url}",
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d'
        ).pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            qr_win,
            text="Ouvrez l'appareil photo de votre smartphone\net pointez-le vers ce QR code",
            font=('Arial', 14),
            bg='white',
            fg='#34495e',
            justify=tk.CENTER
        )
        instructions.pack(pady=20)
    
    def show_server_info(self, event=None):
        """Affiche les informations du serveur web"""
        status = self.web_server.get_status()
        
        info_win = tk.Toplevel(self.root)
        info_win.title("Serveur Web")
        info_win.geometry("500x350")
        info_win.configure(bg='#2c3e50')
        info_win.transient(self.root)
        info_win.grab_set()
        
        # Centrer
        info_win.update_idletasks()
        x = (info_win.winfo_screenwidth() // 2) - 250
        y = (info_win.winfo_screenheight() // 2) - 175
        info_win.geometry(f"500x350+{x}+{y}")
        
        tk.Label(
            info_win,
            text="SERVEUR WEB",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        info_frame = tk.Frame(info_win, bg='#34495e', relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        status_color = '#2ecc71' if status['running'] else '#e74c3c'
        status_text = "En ligne" if status['running'] else "Arrêté"
        
        tk.Label(
            info_frame,
            text=f"Statut: {status_text}",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg=status_color
        ).pack(pady=15)
        
        if status['running']:
            tk.Label(
                info_frame,
                text=f"URL: {status['url']}",
                font=('Arial', 12),
                bg='#34495e',
                fg='#ecf0f1'
            ).pack(pady=5)
            
            tk.Label(
                info_frame,
                text=f"IP locale: {status['local_ip']}",
                font=('Arial', 12),
                bg='#34495e',
                fg='#ecf0f1'
            ).pack(pady=5)
            
            tk.Label(
                info_frame,
                text=f"Port: {status['port']}",
                font=('Arial', 12),
                bg='#34495e',
                fg='#ecf0f1'
            ).pack(pady=5)
            
            tk.Label(
                info_frame,
                text=f"Dossier: {status['photo_dir']}",
                font=('Arial', 10),
                bg='#34495e',
                fg='#95a5a6'
            ).pack(pady=10)
        
        tk.Button(
            info_win,
            text="Fermer",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=info_win.destroy
        ).pack(pady=15)
    
    def show_wifi_config(self):
        """Affiche la configuration WiFi"""
        wifi_dialog = WiFiConfigDialog(self.root)
        wifi_dialog.show_config_dialog()
    
    def show_nextcloud_menu(self):
        """Affiche le menu NextCloud"""
        nextcloud = self.plugin_manager.get_plugin("nextcloud")
        
        if not nextcloud:
            messagebox.showerror("Erreur", "Plugin NextCloud non disponible\nInstallez: pip install requests")
            return
        
        if not nextcloud.is_initialized():
            response = messagebox.askyesno(
                "Configuration requise",
                "NextCloud n'est pas encore configuré.\nVoulez-vous le configurer maintenant ?"
            )
            if response:
                self.show_nextcloud_config()
            return
        
        menu_win = tk.Toplevel(self.root)
        menu_win.title("NextCloud")
        menu_win.geometry("500x400")
        menu_win.configure(bg='#2c3e50')
        menu_win.transient(self.root)
        menu_win.grab_set()
        
        # Centrer
        menu_win.update_idletasks()
        x = (menu_win.winfo_screenwidth() // 2) - 250
        y = (menu_win.winfo_screenheight() // 2) - 200
        menu_win.geometry(f"500x400+{x}+{y}")
        
        # Titre
        tk.Label(
            menu_win,
            text="☁️ NEXTCLOUD",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        # Statut
        status = nextcloud.get_status()
        status_frame = tk.Frame(menu_win, bg='#34495e', relief=tk.RIDGE, bd=2)
        status_frame.pack(fill=tk.X, padx=30, pady=10)
        
        status_color = '#2ecc71' if status['connected'] else '#e74c3c'
        status_text = "Connecté ✓" if status['connected'] else "Non connecté ✗"
        
        tk.Label(
            status_frame,
            text=f"Statut: {status_text}",
            font=('Arial', 13, 'bold'),
            bg='#34495e',
            fg=status_color
        ).pack(pady=10)
        
        if status['connected']:
            space = status.get('space_info', {})
            tk.Label(
                status_frame,
                text=f"Espace: {space.get('used', 'N/A')} / {space.get('total', 'N/A')}",
                font=('Arial', 10),
                bg='#34495e',
                fg='#ecf0f1'
            ).pack(pady=5)
        
        # Boutons
        btn_frame = tk.Frame(menu_win, bg='#2c3e50')
        btn_frame.pack(expand=True, pady=20)
        
        tk.Button(
            btn_frame,
            text="Configuration",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            width=20,
            height=2,
            command=lambda: [menu_win.destroy(), self.show_nextcloud_config()]
        ).pack(pady=8)
        
        if status['connected'] and self.last_session_photos:
            tk.Button(
                btn_frame,
                text="Upload dernières photos",
                font=('Arial', 12, 'bold'),
                bg='#27ae60',
                fg='white',
                width=20,
                height=2,
                command=lambda: [menu_win.destroy(), self.upload_to_nextcloud()]
            ).pack(pady=8)
        
        tk.Button(
            btn_frame,
            text="Fermer",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=20,
            command=menu_win.destroy
        ).pack(pady=8)

    def show_nextcloud_config(self):
        """Affiche la configuration NextCloud"""
        nextcloud = self.plugin_manager.get_plugin("nextcloud")
        if nextcloud:
            NextCloudConfigUI(self.root, nextcloud)
        else:
            messagebox.showerror("Erreur", "Plugin NextCloud non disponible")
    
    def upload_to_nextcloud(self):
        """Upload les photos vers NextCloud"""
        nextcloud = self.plugin_manager.get_plugin("nextcloud")
        
        if not nextcloud or not nextcloud.connected:
            messagebox.showwarning("Non connecté", "NextCloud n'est pas connecté")
            return
        
        if not self.last_session_photos:
            messagebox.showinfo("Info", "Aucune photo à uploader")
            return
        
        # Créer une fenêtre de progression
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Upload NextCloud")
        progress_win.geometry("400x200")
        progress_win.configure(bg='#2c3e50')
        progress_win.transient(self.root)
        progress_win.grab_set()
        
        # Centrer
        progress_win.update_idletasks()
        x = (progress_win.winfo_screenwidth() // 2) - 200
        y = (progress_win.winfo_screenheight() // 2) - 100
        progress_win.geometry(f"400x200+{x}+{y}")
        
        tk.Label(
            progress_win,
            text="Upload en cours...",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        progress_label = tk.Label(
            progress_win,
            text="0 / 0",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#3498db'
        )
        progress_label.pack(pady=10)
        
        progress_win.update()
        
        # Upload des photos
        success_count = 0
        total = len(self.last_session_photos)
        
        for idx, photo in enumerate(self.last_session_photos, 1):
            progress_label.config(text=f"{idx} / {total}")
            progress_win.update()
            
            if nextcloud.upload_file(photo):
                success_count += 1
        
        progress_win.destroy()
        
        # Résultat
        if success_count == total:
            messagebox.showinfo(
                "Succès",
                f"Toutes les photos ont été uploadées !\n{success_count}/{total}"
            )
        elif success_count > 0:
            messagebox.showwarning(
                "Partiel",
                f"{success_count}/{total} photos uploadées"
            )
        else:
            messagebox.showerror(
                "Échec",
                "Aucune photo n'a pu être uploadée"
            )
    

    
    def update_printer_status_label(self):
        """✅ CORRECTION: Met à jour le label de statut imprimante APRÈS initialisation"""
        if self.printer_integration and self.printer_integration.selected_printer:
            info = self.printer_integration.get_printer_info()
            printer_info = self.printer_integration.selected_printer
            
            # Vérifier si l'imprimante est réellement connectée
            if printer_info.is_available:
                self.printer_status_label.config(
                    text=f"🟢 {info['name']}",
                    fg='#2ecc71'
                )
            else:
                self.printer_status_label.config(
                    text=f"🟠 {info['name']} (déco)",
                    fg='#f39c12'
                )
        else:
            self.printer_status_label.config(
                text="✗ Mode démo",
                fg='#e74c3c'
            )

    def update_printer_status(self):
        """Met à jour le statut de l'imprimante"""
        printer = self.plugin_manager.get_plugin("printer")
        diagnostic = PrinterDiagnostic.get_detailed_status(printer)
        

        # Ne pas écraser le label si imprimante détectée
        if hasattr(self, 'printer_integration') and self.printer_integration:
            # Garder le label avec le modèle
            pass
        else:
            self.printer_status_label.config(
            text=diagnostic['message'],
            fg=diagnostic['color']
        )
        
        self.root.after(5000, self.update_printer_status)
    
    def show_printer_diagnostic(self, event=None):
        """Affiche le diagnostic détaillé"""
        printer = self.plugin_manager.get_plugin("printer")
        diagnostic = PrinterDiagnostic.get_detailed_status(printer)
        
        diag_win = tk.Toplevel(self.root)
        diag_win.title("Diagnostic Imprimante")
        diag_win.geometry("600x500")
        diag_win.configure(bg='#2c3e50')
        diag_win.transient(self.root)
        
        diag_win.update_idletasks()
        x = (diag_win.winfo_screenwidth() // 2) - 300
        y = (diag_win.winfo_screenheight() // 2) - 250
        diag_win.geometry(f"600x500+{x}+{y}")
        
        tk.Label(
            diag_win,
            text="DIAGNOSTIC IMPRIMANTE",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        status_frame = tk.Frame(diag_win, bg='#34495e', relief=tk.RIDGE, bd=3)
        status_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            status_frame,
            text=diagnostic['message'],
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg=diagnostic['color']
        ).pack(pady=20)
        
        if diagnostic['solutions']:
            tk.Label(
                diag_win,
                text="Solutions:",
                font=('Arial', 14, 'bold'),
                bg='#2c3e50',
                fg='#ecf0f1'
            ).pack(pady=10)
            
            solutions_frame = tk.Frame(diag_win, bg='#34495e', relief=tk.RIDGE, bd=2)
            solutions_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
            
            for solution in diagnostic['solutions']:
                tk.Label(
                    solutions_frame,
                    text=f"• {solution}",
                    font=('Arial', 12),
                    bg='#34495e',
                    fg='#ecf0f1',
                    anchor=tk.W,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, padx=20, pady=5)
        
        btn_frame = tk.Frame(diag_win, bg='#2c3e50')
        btn_frame.pack(pady=20)
        
        if diagnostic['status'] in ['bloque', 'erreur']:
            tk.Button(
                btn_frame,
                text="Annuler jobs",
                font=('Arial', 12, 'bold'),
                bg='#e67e22',
                fg='white',
                width=15,
                command=self.cancel_print_jobs
            ).pack(side=tk.LEFT, padx=5)
        
        if diagnostic['status'] != 'prete':
            tk.Button(
                btn_frame,
                text="Reset",
                font=('Arial', 12, 'bold'),
                bg='#e74c3c',
                fg='white',
                width=15,
                command=lambda: [self.reset_printer(), diag_win.destroy()]
            ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Fermer",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=diag_win.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    
    
    def show_printer_info(self, event=None):
        """Affiche les détails de l'imprimante détectée"""
        if not hasattr(self, 'printer_integration') or not self.printer_integration.selected_printer:
            messagebox.showinfo(
                "Imprimante",
                "Aucune imprimante détectée\nMode démo activé"
            )
            return
        
        info = self.printer_integration.get_printer_info()
        profile = info.get('profile', {})
        
        details = f"""
IMPRIMANTE DÉTECTÉE
═══════════════════════════

Nom: {info['name']}
Modèle: {info['model']}
Statut: {info['status']}
URI: {info['device_uri']}

PROFIL COMPATIBILITÉ
═══════════════════════════

Format papier: {profile.get('paper_size', 'N/A')}
Résolution: {profile.get('dpi', 'N/A')} DPI
Mode couleur: {profile.get('color_mode', 'N/A')}
Max: {profile.get('max_width', 'N/A')}x{profile.get('max_height', 'N/A')}mm
        """.strip()
        
        messagebox.showinfo("Info Imprimante", details)
    def cancel_print_jobs(self):
        """Annule les jobs d'impression"""
        if messagebox.askyesno("Confirmation", "Annuler tous les jobs d'impression ?"):
            printer = self.plugin_manager.get_plugin("printer")
            if printer and printer.is_initialized():
                printer.cancel_all_jobs()
                messagebox.showinfo("Succès", "Jobs annulés")
                self.update_printer_status()
    
    def show_counter_dialog(self, event=None):
        """✅ NOUVEAU : Dialogue compteur avancé avec interface corrigée"""
        show_print_counter_dialog(self.root, self.print_counter)
        
        # Mettre à jour les affichages après fermeture
        self.root.after(500, self.update_counter_display)
    
    def update_counter_display(self):
        """Met à jour l'affichage des compteurs"""
        self.counter_label.config(text=str(self.print_counter.total_prints))
        self.photos_label.config(text=str(self.print_counter.total_photos))
    
    def reset_printer(self):
        """Reset imprimante"""
        printer = self.plugin_manager.get_plugin("printer")
        if printer and printer.is_initialized():
            if messagebox.askyesno("Reset", "Réinitialiser l'imprimante ?"):
                self.show_message("Reset...", '#e67e22', 16)
                self.root.update()
                if printer.reset_printer():
                    messagebox.showinfo("Succès", "Imprimante réinitialisée")
                    self.update_printer_status()
                else:
                    messagebox.showerror("Erreur", "Échec reset")
                self.show_message("Prêt !", '#ecf0f1', 14)
    
    def show_message(self, text, color='#ecf0f1', size=14, timeout=None):
        """Affiche un message"""
        self.preview_label.config(
            text=text,
            fg=color,
            font=('Arial', size, 'bold'),
            image=''
        )
        self.preview_label.image = None
        
        if timeout:
            self.root.after(timeout * 1000, 
                          lambda: self.show_message("Prêt !", '#ecf0f1', 14))
    
    def test_photo(self):
        """Test photo avec compte à rebours de 3 secondes"""
        if self.is_capturing:
            return
    
        camera = self.plugin_manager.get_plugin("camera")
        if not camera or not camera.is_initialized():
            messagebox.showerror("Erreur", "Caméra non disponible")
            return
    
        # Compte à rebours de 3 secondes
        for i in range(3, 0, -1):
            self.show_message(f"Test photo\n\n{i}...", '#f39c12', 32)
            self.root.update()
            time.sleep(1)
    
        self.show_message("Test photo\n\nCLIC!", '#2ecc71', 28)
        self.root.update()
    
        temp_path = "/tmp/test_photo.jpg"
        success = camera.capture_image(temp_path)
    
        if success and os.path.exists(temp_path):
            try:
                img = Image.open(temp_path)
                img.thumbnail((750, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo, text="")
                self.preview_label.image = photo
                os.remove(temp_path)
            except Exception as e:
                self.show_message("Erreur affichage", '#e74c3c', 14)
        
    def take_four_photos(self):
        """Prend 4 photos"""
        if self.is_capturing:
            return
        
        camera = self.plugin_manager.get_plugin("camera")
        decorator = self.plugin_manager.get_plugin("decorator")
        
        if not camera or not camera.is_initialized():
            messagebox.showerror("Erreur", "Caméra non disponible")
            return
        
        self.is_capturing = True
        self.start_btn.config(state=tk.DISABLED, bg='#95a5a6')
        
        captured_photos = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for photo_num in range(1, 5):
            for i in range(3, 0, -1):
                self.show_message(f"Photo {photo_num}/4\n\n{i}...", '#f39c12', 32)
                self.root.update()
                time.sleep(1)
            
            self.show_message(f"Photo {photo_num}/4\n\nCLIC!", '#2ecc71', 28)
            self.root.update()
            
            temp_file = f"/tmp/photo_{timestamp}_{photo_num}.jpg"
            success = camera.capture_image(temp_file)
            
            if success and os.path.exists(temp_file):
                captured_photos.append(temp_file)
            
            if photo_num < 4:
                time.sleep(1)
        
        if len(captured_photos) >= 4:
            self.show_message("Traitement...", '#3498db', 16)
            self.root.update()
            
            self.last_session_photos = []
            
            # ✅ ENREGISTRER LA SESSION DANS LE COMPTEUR
            self.print_counter.increment_session(4, self.current_style)
            self.update_counter_display()
            
            if decorator and decorator.is_initialized():
                montage_path = str(self.photo_dir / f"montage_{self.current_style}_{timestamp}.jpg")
                if decorator.create_film_strip(captured_photos, self.current_style, montage_path):
                    self.last_session_photos.append(montage_path)
            
            for i, photo_path in enumerate(captured_photos):
                output_path = str(self.photo_dir / f"photo_{self.current_style}_{timestamp}_{i+1}.jpg")
                if decorator and decorator.is_initialized():
                    if decorator.apply_style(photo_path, self.current_style, output_path):
                        self.last_session_photos.append(output_path)
            
            for temp_file in captured_photos:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            # Upload auto vers NextCloud si configuré
            self.auto_upload_to_nextcloud()
            
            self.show_print_selection()
        else:
            self.show_message("Session incomplète", '#e74c3c', 14)
            self.reset_session()
    
    def show_print_selection(self):
        """Affiche sélection photos avec images complètes"""
        selection_win = tk.Toplevel(self.root)
        selection_win.title("Vos Photos")
        selection_win.attributes("-fullscreen", True)
        selection_win.configure(bg='#2c3e50')
        selection_win.transient(self.root)
        selection_win.grab_set()
        
        selected_photo = tk.StringVar(value=self.last_session_photos[0] if self.last_session_photos else "")
        
        # En-tête avec bouton fermer
        header = tk.Frame(selection_win, bg='#34495e', height=80)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="VOS PHOTOS SONT PRÊTES !",
            font=('Arial', 24, 'bold'),
            bg='#34495e',
            fg='#2ecc71'
        ).pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Button(
            header,
            text="✕ FERMER",
            font=('Arial', 16, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            height=2,
            command=lambda: self.close_selection(selection_win)
        ).pack(side=tk.RIGHT, padx=30, pady=15)
        
        tk.Label(
            header,
            text="👆 Touchez une photo",
            font=('Arial', 14),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=20)
        
        # Zone photos avec Canvas + Scrollbar
        photos_outer = tk.Frame(selection_win, bg='#2c3e50')
        photos_outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        canvas = tk.Canvas(photos_outer, bg='#2c3e50', highlightthickness=0)
        scrollbar = tk.Scrollbar(photos_outer, orient="vertical", command=canvas.yview, width=25)
        photos_container = tk.Frame(canvas, bg='#2c3e50')
        
        photos_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=photos_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        photo_frames = {}
        
        def select_photo(photo_path):
            selected_photo.set(photo_path)
            for path, frame in photo_frames.items():
                if path == photo_path:
                    frame.config(bg='#27ae60', relief=tk.SOLID, bd=6)
                else:
                    frame.config(bg='#34495e', relief=tk.RAISED, bd=2)
        
        # Grille adaptative
        num_photos = len(self.last_session_photos)
        cols = 3 if num_photos > 4 else 2
        
        for idx, photo_path in enumerate(self.last_session_photos[:6]):
            row, col = idx // cols, idx % cols
            
            frame = tk.Frame(photos_container, bg='#34495e', relief=tk.RAISED, bd=2, cursor="hand2")
            frame.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
            photo_frames[photo_path] = frame
            
            photos_container.grid_rowconfigure(row, weight=1)
            photos_container.grid_columnconfigure(col, weight=1)
            
            try:
                img = Image.open(photo_path)
                
                # Calcul taille adaptative
                if cols == 3:
                    max_w, max_h = 280, 200
                else:
                    max_w, max_h = 450, 280
                
                # Conserver proportions
                ratio = img.width / img.height
                target_ratio = max_w / max_h
                
                if ratio > target_ratio:
                    new_w, new_h = max_w, int(max_w / ratio)
                else:
                    new_h, new_w = max_h, int(max_h * ratio)
                
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Container pour centrer
                img_container = tk.Frame(frame, bg='#34495e', width=max_w, height=max_h)
                img_container.pack(padx=8, pady=8)
                img_container.pack_propagate(False)
                
                img_label = tk.Label(img_container, image=photo, bg='#34495e', cursor="hand2")
                img_label.image = photo
                img_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                img_label.bind('<Button-1>', lambda e, p=photo_path: select_photo(p))
                
                frame.bind('<Button-1>', lambda e, p=photo_path: select_photo(p))
                
                is_montage = "montage" in photo_path
                label_text = "🎞️ MONTAGE" if is_montage else f"📷 PHOTO {idx + 1 if not is_montage else ''}"
                name_label = tk.Label(frame, text=label_text, font=('Arial', 12, 'bold'), bg='#34495e', fg='#ecf0f1', cursor="hand2")
                name_label.pack(pady=5)
                name_label.bind('<Button-1>', lambda e, p=photo_path: select_photo(p))
            except Exception as e:
                print(f"Erreur photo {idx}: {e}")
        
        if self.last_session_photos:
            select_photo(self.last_session_photos[0])
        
        # Boutons d'action
        action_frame = tk.Frame(selection_win, bg='#34495e', height=110)
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        action_frame.pack_propagate(False)
        
        btn_container = tk.Frame(action_frame, bg='#34495e')
        btn_container.pack(expand=True, pady=15)
        
        def print_selected():
            photo = selected_photo.get()
            if photo:
                selection_win.destroy()
                self.print_photo_from_gallery(photo)
                self.reset_session()
        
        def qr_selected():
            photo = selected_photo.get()
            if photo:
                selection_win.destroy()
                self.generate_qr_for_photo(photo)
                self.reset_session()
        
        def print_all():
            if messagebox.askyesno("Confirmer", f"Imprimer toutes les {len(self.last_session_photos)} photos ?", parent=selection_win):
                selection_win.destroy()
                printer = self.plugin_manager.get_plugin("printer")
                if printer and printer.is_initialized():
                    success_count = 0
                    
                    # ✅ SMART: Détecter le type d'imprimante
                    use_ipp = False
                    ipp_printer = None
                    print_method = "classique"
                    
                    if hasattr(self, 'printer_integration') and self.printer_integration.selected_printer:
                        ipp_printer = self.printer_integration.selected_printer.ipp_printer
                        use_ipp = ipp_printer is not None
                        
                        if use_ipp:
                            print_method = "IPP (réseau)"
                            print(f"🌐 Impression IPP batch de {len(self.last_session_photos)} photos")
                        else:
                            print_method = "USB/classique"
                            print(f"🖨️  Impression USB batch de {len(self.last_session_photos)} photos")
                    
                    for photo in self.last_session_photos:
                        if use_ipp:
                            # Imprimante réseau IPP
                            success = ipp_printer.print_image(str(photo))
                        else:
                            # Imprimante USB ou autre (méthode classique)
                            success = printer.print_image(str(photo))
                        
                        if success:
                            self.print_counter.increment_print()
                            success_count += 1
                        time.sleep(2)
                    
                    self.update_counter_display()
                    messagebox.showinfo("Succès", f"{success_count} photos imprimées !\nMéthode: {print_method}")
                    
                else:
                    messagebox.showerror("Erreur", "Imprimante non disponible")
                self.reset_session()
        
        tk.Button(btn_container, text="🖨️ IMPRIMER", font=('Arial', 18, 'bold'), bg='#27ae60', fg='white', width=18, height=2, command=print_selected).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_container, text="📱 QR CODE", font=('Arial', 18, 'bold'), bg='#9b59b6', fg='white', width=18, height=2, command=qr_selected).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_container, text="Tout Imprimer", font=('Arial', 14, 'bold'), bg='#3498db', fg='white', width=15, height=2, command=print_all).pack(side=tk.LEFT, padx=10)

    def close_selection(self, window):
        """Ferme la sélection"""
        window.destroy()
        self.reset_session()
    
    def reset_session(self):
        """Reset session"""
        self.is_capturing = False
        self.start_btn.config(state=tk.NORMAL, bg='#27ae60')
        self.show_message("Prêt !", '#ecf0f1', 14)
    
    def auto_upload_to_nextcloud(self):
        """Upload automatique vers NextCloud si activé"""
        try:
            nextcloud = self.plugin_manager.get_plugin("nextcloud")
            if nextcloud and nextcloud.connected and nextcloud.auto_upload:
                if self.last_session_photos:
                    for photo in self.last_session_photos:
                        nextcloud.upload_file(photo)
                    print(f"Auto-upload NextCloud: {len(self.last_session_photos)} photos")
        except Exception as e:
            print(f"Erreur auto-upload NextCloud: {e}")
    
    def quit_app(self):
        """Quitte"""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ?"):
            self.web_server.stop()
            self.plugin_manager.shutdown_all()
            self.root.quit()


def main():
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    root = tk.Tk()
    app = photovincAppComplete(root)
    root.mainloop()


if __name__ == "__main__":
    main()
