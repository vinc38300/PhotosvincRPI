#!/usr/bin/env python3
"""
Interface de configuration et gestion NextCloud
Avec support du clavier virtuel pour écran tactile
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
import logging
import subprocess
import os

logger = logging.getLogger(__name__)


class VirtualKeyboard:
    """Gestionnaire de clavier virtuel"""
    
    @staticmethod
    def is_available():
        """Vérifie si onboard est installé"""
        try:
            subprocess.run(['which', 'onboard'], capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def toggle():
        """Active/désactive le clavier virtuel"""
        try:
            # Vérifier si onboard est déjà lancé
            result = subprocess.run(['pgrep', 'onboard'], capture_output=True)
            if result.returncode == 0:
                # Fermer onboard
                subprocess.run(['pkill', 'onboard'])
            else:
                # Lancer onboard
                subprocess.Popen(['onboard'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Erreur clavier virtuel: {e}")


class NextCloudConfigUI:
    """Interface de configuration NextCloud avec clavier virtuel"""
    
    def __init__(self, parent, nextcloud_plugin):
        self.parent = parent
        self.nextcloud = nextcloud_plugin
        self.keyboard_available = VirtualKeyboard.is_available()
        
        self.create_ui()
    
    def create_ui(self):
        """Crée l'interface de configuration"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Configuration NextCloud")
        self.window.geometry("700x700")
        self.window.configure(bg='#2c3e50')
        self.window.resizable(False, False)
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 350
        y = (self.window.winfo_screenheight() // 2) - 350
        self.window.geometry(f"700x700+{x}+{y}")
        
        # Barre de titre avec bouton clavier
        title_frame = tk.Frame(self.window, bg='#34495e')
        title_frame.pack(fill=tk.X)
        
        tk.Label(
            title_frame,
            text="☁️ NEXTCLOUD",
            font=('Arial', 22, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        # Bouton clavier virtuel
        if self.keyboard_available:
            keyboard_btn = tk.Button(
                title_frame,
                text="⌨️ Clavier",
                font=('Arial', 12, 'bold'),
                bg='#9b59b6',
                fg='white',
                width=12,
                height=2,
                command=VirtualKeyboard.toggle
            )
            keyboard_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Statut actuel
        status = self.nextcloud.get_status()
        
        status_frame = tk.Frame(self.window, bg='#34495e', relief=tk.RIDGE, bd=2)
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
            space_info = status['space_info']
            tk.Label(
                status_frame,
                text=f"Espace: {space_info['used']} utilisé / {space_info['total']}",
                font=('Arial', 10),
                bg='#34495e',
                fg='#ecf0f1'
            ).pack(pady=5)
        
        # Formulaire de configuration
        form_frame = tk.Frame(self.window, bg='#2c3e50')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # URL du serveur
        tk.Label(
            form_frame,
            text="URL du serveur NextCloud:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.server_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            width=50,
            bg='#ecf0f1'
        )
        self.server_entry.pack(fill=tk.X, pady=5)
        self.server_entry.insert(0, status.get('server_url', ''))
        
        # Ouvrir le clavier au focus
        if self.keyboard_available:
            self.server_entry.bind('<FocusIn>', lambda e: VirtualKeyboard.toggle())
        
        tk.Label(
            form_frame,
            text="Exemple: https://cloud.exemple.com ou https://exemple.com/nextcloud",
            font=('Arial', 9, 'italic'),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack(anchor=tk.W)
        
        # Nom d'utilisateur
        tk.Label(
            form_frame,
            text="Nom d'utilisateur:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(anchor=tk.W, pady=(15, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            width=50,
            bg='#ecf0f1'
        )
        self.username_entry.pack(fill=tk.X, pady=5)
        self.username_entry.insert(0, status.get('username', ''))
        
        if self.keyboard_available:
            self.username_entry.bind('<FocusIn>', lambda e: VirtualKeyboard.toggle())
        
        # Mot de passe
        tk.Label(
            form_frame,
            text="Mot de passe:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(anchor=tk.W, pady=(15, 5))
        
        password_frame = tk.Frame(form_frame, bg='#2c3e50')
        password_frame.pack(fill=tk.X, pady=5)
        
        self.password_entry = tk.Entry(
            password_frame,
            font=('Arial', 11),
            show='●',
            bg='#ecf0f1'
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if self.keyboard_available:
            self.password_entry.bind('<FocusIn>', lambda e: VirtualKeyboard.toggle())
        
        self.show_password_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            password_frame,
            text="Afficher",
            variable=self.show_password_var,
            command=self.toggle_password,
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            selectcolor='#34495e',
            activebackground='#2c3e50'
        ).pack(side=tk.LEFT, padx=10)
        
        # Dossier distant
        tk.Label(
            form_frame,
            text="Dossier de destination:",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(anchor=tk.W, pady=(15, 5))
        
        self.folder_entry = tk.Entry(
            form_frame,
            font=('Arial', 11),
            width=50,
            bg='#ecf0f1'
        )
        self.folder_entry.pack(fill=tk.X, pady=5)
        self.folder_entry.insert(0, status.get('remote_folder', '/photovinc'))
        
        if self.keyboard_available:
            self.folder_entry.bind('<FocusIn>', lambda e: VirtualKeyboard.toggle())
        
        # Options
        options_frame = tk.Frame(form_frame, bg='#2c3e50')
        options_frame.pack(fill=tk.X, pady=15)
        
        self.auto_upload_var = tk.BooleanVar(value=status.get('auto_upload', True))
        tk.Checkbutton(
            options_frame,
            text="Upload automatique après chaque session",
            variable=self.auto_upload_var,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            selectcolor='#34495e',
            activebackground='#2c3e50'
        ).pack(anchor=tk.W, pady=5)
        
        self.dated_folders_var = tk.BooleanVar(
            value=self.nextcloud.config.settings.get('create_dated_folders', True)
        )
        tk.Checkbutton(
            options_frame,
            text="Créer des sous-dossiers par date (2025-01-15)",
            variable=self.dated_folders_var,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            selectcolor='#34495e',
            activebackground='#2c3e50'
        ).pack(anchor=tk.W, pady=5)
        
        # Message d'aide si pas de clavier
        if not self.keyboard_available:
            help_frame = tk.Frame(self.window, bg='#e67e22', relief=tk.RIDGE, bd=2)
            help_frame.pack(fill=tk.X, padx=30, pady=10)
            
            tk.Label(
                help_frame,
                text="💡 Astuce: Installez 'onboard' pour un clavier virtuel\nsudo apt install onboard",
                font=('Arial', 9),
                bg='#e67e22',
                fg='white',
                justify=tk.LEFT
            ).pack(pady=8, padx=10)
        
        # Boutons d'action
        btn_frame = tk.Frame(self.window, bg='#2c3e50')
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Tester la connexion",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            width=18,
            height=2,
            command=self.test_connection
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Sauvegarder",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=18,
            height=2,
            command=self.save_config
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Annuler",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=18,
            height=2,
            command=self.close_window
        ).pack(side=tk.LEFT, padx=5)
    
    def toggle_password(self):
        """Affiche/masque le mot de passe"""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='●')
    
    def test_connection(self):
        """Teste la connexion NextCloud"""
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not server or not username or not password:
            messagebox.showwarning(
                "Champs manquants",
                "Veuillez remplir tous les champs",
                parent=self.window
            )
            return
        
        # Configuration temporaire pour test
        self.nextcloud.configure(server, username, password)
        
        # Tenter une réinitialisation
        self.nextcloud.shutdown()
        
        if self.nextcloud.initialize():
            messagebox.showinfo(
                "Succès",
                "Connexion NextCloud réussie !\n\n"
                f"Serveur: {server}\n"
                f"Utilisateur: {username}",
                parent=self.window
            )
        else:
            messagebox.showerror(
                "Échec",
                "Impossible de se connecter à NextCloud.\n\n"
                "Vérifiez:\n"
                "- L'URL du serveur\n"
                "- Le nom d'utilisateur\n"
                "- Le mot de passe\n"
                "- Votre connexion internet",
                parent=self.window
            )
    
    def save_config(self):
        """Sauvegarde la configuration"""
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        folder = self.folder_entry.get().strip()
        
        if not server or not username or not password:
            messagebox.showwarning(
                "Champs manquants",
                "Veuillez remplir tous les champs",
                parent=self.window
            )
            return
        
        # Sauvegarder
        self.nextcloud.configure(server, username, password, folder)
        self.nextcloud.auto_upload = self.auto_upload_var.get()
        self.nextcloud.create_dated_folders = self.dated_folders_var.get()
        
        # Mettre à jour les settings
        self.nextcloud.config.settings['auto_upload'] = self.auto_upload_var.get()
        self.nextcloud.config.settings['create_dated_folders'] = self.dated_folders_var.get()
        
        messagebox.showinfo(
            "Succès",
            "Configuration NextCloud sauvegardée !",
            parent=self.window
        )
        
        self.close_window()
    
    def close_window(self):
        """Ferme la fenêtre et le clavier si ouvert"""
        if self.keyboard_available:
            # Fermer le clavier virtuel si ouvert
            subprocess.run(['pkill', 'onboard'], stderr=subprocess.DEVNULL)
        self.window.destroy()


class NextCloudFileManagerUI:
    """Gestionnaire de fichiers NextCloud"""
    
    def __init__(self, parent, nextcloud_plugin):
        self.parent = parent
        self.nextcloud = nextcloud_plugin
        
        if not self.nextcloud.connected:
            messagebox.showerror(
                "Erreur",
                "NextCloud n'est pas connecté.\nConfigurez d'abord la connexion."
            )
            return
        
        self.create_ui()
    
    def create_ui(self):
        """Crée l'interface de gestion de fichiers"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestionnaire NextCloud")
        self.window.geometry("800x600")
        self.window.configure(bg='#2c3e50')
        
        # Titre
        tk.Label(
            self.window,
            text="FICHIERS NEXTCLOUD",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=15)
        
        # Barre d'outils
        toolbar = tk.Frame(self.window, bg='#34495e')
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Actualiser",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            command=self.refresh_list
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Upload photo",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            command=self.upload_photo
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Créer lien",
            font=('Arial', 10, 'bold'),
            bg='#9b59b6',
            fg='white',
            width=12,
            command=self.create_share_link
        ).pack(side=tk.LEFT, padx=5)
        
        # Chemin actuel
        path_frame = tk.Frame(self.window, bg='#2c3e50')
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            path_frame,
            text="Dossier:",
            font=('Arial', 10, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=5)
        
        self.current_path = self.nextcloud.remote_folder
        self.path_label = tk.Label(
            path_frame,
            text=self.current_path,
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1',
            anchor=tk.W
        )
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Liste des fichiers
        list_frame = tk.Frame(self.window, bg='#2c3e50')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview pour afficher les fichiers
        columns = ('name', 'size', 'date')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        self.tree.heading('#0', text='Type')
        self.tree.heading('name', text='Nom')
        self.tree.heading('size', text='Taille')
        self.tree.heading('date', text='Date')
        
        self.tree.column('#0', width=50)
        self.tree.column('name', width=300)
        self.tree.column('size', width=100)
        self.tree.column('date', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Charger la liste
        self.refresh_list()
        
        # Bouton fermer
        tk.Button(
            self.window,
            text="Fermer",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=self.window.destroy
        ).pack(pady=10)
    
    def refresh_list(self):
        """Actualise la liste des fichiers"""
        # Effacer la liste actuelle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Charger les fichiers
        files = self.nextcloud.list_files(self.current_path)
        
        # Pour l'instant, afficher un message
        self.tree.insert('', 'end', text='📁', values=('(Liste non disponible)', '', ''))
    
    def upload_photo(self):
        """Upload une photo"""
        from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            title="Sélectionner une photo",
            filetypes=[("Images", "*.jpg *.jpeg *.png"), ("Tous", "*.*")]
        )
        
        if filepath:
            if self.nextcloud.upload_file(filepath):
                messagebox.showinfo("Succès", f"Photo uploadée !\n{filepath}")
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", "Échec de l'upload")
    
    def create_share_link(self):
        """Crée un lien de partage"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionnez un fichier")
            return
        
        # Obtenir le nom du fichier
        item = self.tree.item(selection[0])
        filename = item['values'][0]
        remote_path = f"{self.current_path}/{filename}"
        
        # Créer le lien
        link = self.nextcloud.get_share_link(remote_path)
        
        if link:
            # Afficher le lien
            link_window = tk.Toplevel(self.window)
            link_window.title("Lien de partage")
            link_window.geometry("500x200")
            link_window.configure(bg='#2c3e50')
            
            tk.Label(
                link_window,
                text="Lien de partage créé !",
                font=('Arial', 14, 'bold'),
                bg='#2c3e50',
                fg='#2ecc71'
            ).pack(pady=20)
            
            link_entry = tk.Entry(
                link_window,
                font=('Arial', 11),
                width=50
            )
            link_entry.pack(pady=10)
            link_entry.insert(0, link)
            link_entry.config(state='readonly')
            
            tk.Button(
                link_window,
                text="Copier",
                font=('Arial', 11, 'bold'),
                bg='#3498db',
                fg='white',
                command=lambda: self.copy_to_clipboard(link, link_window)
            ).pack(pady=10)
        else:
            messagebox.showerror("Erreur", "Impossible de créer le lien")
    
    def copy_to_clipboard(self, text, window):
        """Copie le texte dans le presse-papier"""
        window.clipboard_clear()
        window.clipboard_append(text)
        messagebox.showinfo("Copié", "Lien copié dans le presse-papier !", parent=window)


# Fonction d'intégration dans l'application principale
def integrate_nextcloud_features(app, plugin_manager):
    """Intègre NextCloud dans l'application principale"""
    
    def show_nextcloud_config():
        """Affiche la configuration NextCloud"""
        nextcloud = plugin_manager.get_plugin("nextcloud")
        if nextcloud:
            NextCloudConfigUI(app.root, nextcloud)
        else:
            messagebox.showerror("Erreur", "Plugin NextCloud non disponible")
    
    def show_nextcloud_manager():
        """Affiche le gestionnaire de fichiers"""
        nextcloud = plugin_manager.get_plugin("nextcloud")
        if nextcloud and nextcloud.connected:
            NextCloudFileManagerUI(app.root, nextcloud)
        elif nextcloud:
            response = messagebox.askyesno(
                "Non connecté",
                "NextCloud n'est pas connecté.\nVoulez-vous configurer la connexion ?"
            )
            if response:
                show_nextcloud_config()
        else:
            messagebox.showerror("Erreur", "Plugin NextCloud non disponible")
    
    def upload_last_photos():
        """Upload les photos de la dernière session"""
        nextcloud = plugin_manager.get_plugin("nextcloud")
        if not nextcloud or not nextcloud.connected:
            messagebox.showwarning("Non connecté", "NextCloud n'est pas connecté")
            return
        
        if not hasattr(app, 'last_session_photos') or not app.last_session_photos:
            messagebox.showinfo("Info", "Aucune photo à uploader")
            return
        
        success_count = 0
        for photo in app.last_session_photos:
            if nextcloud.upload_file(photo):
                success_count += 1
        
        messagebox.showinfo(
            "Upload terminé",
            f"{success_count}/{len(app.last_session_photos)} photos uploadées"
        )
    
    return {
        'show_config': show_nextcloud_config,
        'show_manager': show_nextcloud_manager,
        'upload_photos': upload_last_photos
    }


# Exemple d'utilisation
if __name__ == "__main__":
    import tkinter as tk
    from plugin_manager import PluginManager, PluginConfig
    from nextcloud_plugin import NextCloudPlugin, register_nextcloud_plugin
    
    root = tk.Tk()
    root.withdraw()
    
    # Créer le gestionnaire
    manager = PluginManager()
    manager.load_config()
    
    # Enregistrer NextCloud
    register_nextcloud_plugin(manager)
    
    # Initialiser
    manager.initialize_all()
    
    # Obtenir le plugin
    nextcloud = manager.get_plugin("nextcloud")
    
    if nextcloud:
        # Afficher la config
        NextCloudConfigUI(root, nextcloud)
        root.mainloop()
    
    # Nettoyage
    manager.shutdown_all()
