#!/usr/bin/env python3
"""
Interface graphique de gestion des plugins photovinc
Permet d'activer/désactiver et configurer chaque plugin
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
from typing import Dict, Any


class PluginManagerUI:
    """Interface de gestion des plugins"""
    
    def __init__(self, root, plugin_manager):
        self.root = root
        self.manager = plugin_manager
        self.plugin_frames = {}
        
        self.root.title("Gestion des Plugins - photovinc")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        self.setup_ui()
        self.refresh_all()
    
    def setup_ui(self):
        """Configure l'interface"""
        # En-tête
        header = tk.Frame(self.root, bg='#34495e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="GESTIONNAIRE DE PLUGINS",
            font=('Arial', 18, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Button(
            header,
            text="Actualiser",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            command=self.refresh_all
        ).pack(side=tk.RIGHT, padx=10, pady=15)
        
        tk.Button(
            header,
            text="Sauvegarder",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            command=self.save_all
        ).pack(side=tk.RIGHT, padx=5, pady=15)
        
        # Zone principale avec scroll
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_container, bg='#2c3e50', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg='#2c3e50')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Créer les sections de plugins
        self.create_plugin_sections()
        
        # Barre de statut
        status_frame = tk.Frame(self.root, bg='#34495e', height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Prêt",
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
    
    def create_plugin_sections(self):
        """Crée les sections pour chaque plugin"""
        plugins_info = {
            "camera": {
                "title": "📷 Appareil Photo",
                "description": "Gestion de l'appareil photo Canon",
                "color": "#e74c3c"
            },
            "printer": {
                "title": "🖨️ Imprimante",
                "description": "Gestion de l'imprimante Canon CP-400",
                "color": "#3498db"
            },
            "decorator": {
                "title": "🎨 Décorateur",
                "description": "Effets et styles pour les photos",
                "color": "#9b59b6"
            },
            "wifi": {
                "title": "📡 WiFi",
                "description": "Configuration réseau sans fil",
                "color": "#16a085"
            },
            "keyboard": {
                "title": "⌨️ Clavier Virtuel",
                "description": "Clavier tactile à l'écran",
                "color": "#f39c12"
            }
        }
        
        for plugin_id, info in plugins_info.items():
            frame = self.create_plugin_frame(plugin_id, info)
            self.plugin_frames[plugin_id] = frame
    
    def create_plugin_frame(self, plugin_id: str, info: Dict[str, str]):
        """Crée le cadre pour un plugin"""
        # Cadre principal
        main_frame = tk.Frame(
            self.scrollable_frame,
            bg='#34495e',
            relief=tk.RAISED,
            bd=2
        )
        main_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # En-tête du plugin
        header = tk.Frame(main_frame, bg=info['color'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Titre et description
        left_frame = tk.Frame(header, bg=info['color'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            left_frame,
            text=info['title'],
            font=('Arial', 14, 'bold'),
            bg=info['color'],
            fg='white'
        ).pack(anchor=tk.W, padx=15, pady=2)
        
        tk.Label(
            left_frame,
            text=info['description'],
            font=('Arial', 9),
            bg=info['color'],
            fg='white'
        ).pack(anchor=tk.W, padx=15)
        
        # Boutons de contrôle
        controls = tk.Frame(header, bg=info['color'])
        controls.pack(side=tk.RIGHT, padx=10)
        
        # Switch activé/désactivé
        enabled_var = tk.BooleanVar(value=True)
        enabled_check = tk.Checkbutton(
            controls,
            text="Activé",
            variable=enabled_var,
            font=('Arial', 10, 'bold'),
            bg=info['color'],
            fg='white',
            selectcolor='#2c3e50',
            activebackground=info['color'],
            activeforeground='white',
            command=lambda: self.toggle_plugin(plugin_id, enabled_var.get())
        )
        enabled_check.pack(side=tk.LEFT, padx=5)
        
        # Boutons d'action
        tk.Button(
            controls,
            text="Config",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='white',
            width=8,
            command=lambda: self.show_config(plugin_id)
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            controls,
            text="Statut",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='white',
            width=8,
            command=lambda: self.show_status(plugin_id)
        ).pack(side=tk.LEFT, padx=2)
        
        # Zone de contenu
        content = tk.Frame(main_frame, bg='#2c3e50')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Informations du plugin
        info_frame = tk.Frame(content, bg='#2c3e50')
        info_frame.pack(fill=tk.X, pady=5)
        
        # Statut actuel
        status_label = tk.Label(
            info_frame,
            text="Statut: Vérification...",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Capacités
        caps_label = tk.Label(
            info_frame,
            text="Capacités: -",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#95a5a6',
            anchor=tk.W
        )
        caps_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Priorité
        priority_frame = tk.Frame(info_frame, bg='#2c3e50')
        priority_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            priority_frame,
            text="Priorité d'initialisation:",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(side=tk.LEFT)
        
        priority_spin = tk.Spinbox(
            priority_frame,
            from_=0,
            to=10,
            width=5,
            font=('Arial', 9)
        )
        priority_spin.pack(side=tk.LEFT, padx=5)
        
        return {
            'main_frame': main_frame,
            'enabled_var': enabled_var,
            'status_label': status_label,
            'caps_label': caps_label,
            'priority_spin': priority_spin,
            'enabled_check': enabled_check
        }
    
    def toggle_plugin(self, plugin_id: str, enabled: bool):
        """Active ou désactive un plugin"""
        if enabled:
            self.manager.enable_plugin(plugin_id)
            self.status_label.config(
                text=f"Plugin {plugin_id} activé",
                fg='#2ecc71'
            )
        else:
            self.manager.disable_plugin(plugin_id)
            self.status_label.config(
                text=f"Plugin {plugin_id} désactivé",
                fg='#e74c3c'
            )
        
        self.refresh_plugin_status(plugin_id)
    
    def show_config(self, plugin_id: str):
        """Affiche la configuration d'un plugin"""
        config_win = tk.Toplevel(self.root)
        config_win.title(f"Configuration - {plugin_id}")
        config_win.geometry("500x400")
        config_win.configure(bg='#2c3e50')
        config_win.transient(self.root)
        
        tk.Label(
            config_win,
            text=f"Configuration du plugin {plugin_id.upper()}",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=15)
        
        # Zone de configuration
        config_frame = tk.Frame(config_win, bg='#34495e')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Obtenir la config actuelle
        if plugin_id in self.manager.plugin_configs:
            config = self.manager.plugin_configs[plugin_id]
            
            # Afficher les paramètres
            settings_text = scrolledtext.ScrolledText(
                config_frame,
                font=('Courier', 10),
                bg='#2c3e50',
                fg='#ecf0f1',
                height=15
            )
            settings_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Formater en JSON
            settings_json = json.dumps(config.settings, indent=2)
            settings_text.insert(tk.END, settings_json)
        
        # Boutons
        btn_frame = tk.Frame(config_win, bg='#2c3e50')
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Appliquer",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            command=lambda: self.apply_config(plugin_id, settings_text.get(1.0, tk.END), config_win)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Annuler",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=12,
            command=config_win.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def apply_config(self, plugin_id: str, settings_json: str, window):
        """Applique une nouvelle configuration"""
        try:
            settings = json.loads(settings_json)
            self.manager.update_plugin_settings(plugin_id, settings)
            messagebox.showinfo("Succès", "Configuration mise à jour", parent=window)
            window.destroy()
            self.refresh_plugin_status(plugin_id)
        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur", f"JSON invalide:\n{e}", parent=window)
    
    def show_status(self, plugin_id: str):
        """Affiche le statut détaillé d'un plugin"""
        status_win = tk.Toplevel(self.root)
        status_win.title(f"Statut - {plugin_id}")
        status_win.geometry("450x350")
        status_win.configure(bg='#2c3e50')
        status_win.transient(self.root)
        
        tk.Label(
            status_win,
            text=f"Statut du plugin {plugin_id.upper()}",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=15)
        
        # Zone de statut
        status_frame = tk.Frame(status_win, bg='#34495e')
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        status_text = scrolledtext.ScrolledText(
            status_frame,
            font=('Courier', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            height=12
        )
        status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Obtenir le statut
        plugin = self.manager.get_plugin(plugin_id)
        if plugin:
            status = plugin.get_status()
            status_json = json.dumps(status, indent=2)
            status_text.insert(tk.END, status_json)
        else:
            status_text.insert(tk.END, "Plugin non chargé ou désactivé")
        
        tk.Button(
            status_win,
            text="Fermer",
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            width=12,
            command=status_win.destroy
        ).pack(pady=10)
    
    def refresh_plugin_status(self, plugin_id: str):
        """Actualise le statut d'un plugin"""
        if plugin_id not in self.plugin_frames:
            return
        
        frame = self.plugin_frames[plugin_id]
        plugin = self.manager.get_plugin(plugin_id)
        
        if plugin and plugin.is_initialized():
            status = plugin.get_status()
            status_text = f"Statut: ✓ Initialisé"
            status_color = '#2ecc71'
            
            # Capacités
            caps = plugin.get_capabilities()
            caps_text = f"Capacités: {', '.join(caps)}"
            
            frame['enabled_var'].set(True)
        else:
            status_text = "Statut: ✗ Non initialisé"
            status_color = '#e74c3c'
            caps_text = "Capacités: -"
            frame['enabled_var'].set(False)
        
        frame['status_label'].config(text=status_text, fg=status_color)
        frame['caps_label'].config(text=caps_text)
        
        # Priorité
        if plugin_id in self.manager.plugin_configs:
            priority = self.manager.plugin_configs[plugin_id].priority
            frame['priority_spin'].delete(0, tk.END)
            frame['priority_spin'].insert(0, str(priority))
    
    def refresh_all(self):
        """Actualise tous les plugins"""
        self.status_label.config(text="Actualisation...", fg='#f39c12')
        self.root.update()
        
        for plugin_id in self.plugin_frames.keys():
            self.refresh_plugin_status(plugin_id)
        
        self.status_label.config(text="Actualisation terminée", fg='#2ecc71')
        self.root.after(2000, lambda: self.status_label.config(text="Prêt", fg='#ecf0f1'))
    
    def save_all(self):
        """Sauvegarde toutes les configurations"""
        # Récupérer les priorités
        for plugin_id, frame in self.plugin_frames.items():
            try:
                priority = int(frame['priority_spin'].get())
                if plugin_id in self.manager.plugin_configs:
                    self.manager.plugin_configs[plugin_id].priority = priority
            except ValueError:
                pass
        
        self.manager.save_config()
        self.status_label.config(text="Configuration sauvegardée", fg='#2ecc71')
        messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")


class PluginControlPanel:
    """Panneau de contrôle simplifié pour l'application principale"""
    
    def __init__(self, parent, plugin_manager):
        self.parent = parent
        self.manager = plugin_manager
        
        self.panel = tk.Frame(parent, bg='#2c3e50')
        self.status_labels = {}
        
        self.create_compact_panel()
    
    def create_compact_panel(self):
        """Crée un panneau compact pour l'interface principale"""
        tk.Label(
            self.panel,
            text="Plugins",
            font=('Arial', 10, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        plugins = {
            "camera": "📷",
            "printer": "🖨️",
            "decorator": "🎨",
            "wifi": "📡",
            "keyboard": "⌨️"
        }
        
        for plugin_id, icon in plugins.items():
            frame = tk.Frame(self.panel, bg='#34495e')
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(
                frame,
                text=icon,
                font=('Arial', 12),
                bg='#34495e',
                fg='white',
                width=3
            ).pack(side=tk.LEFT)
            
            status_label = tk.Label(
                frame,
                text="●",
                font=('Arial', 16),
                bg='#34495e',
                fg='#95a5a6'
            )
            status_label.pack(side=tk.LEFT, padx=5)
            
            tk.Label(
                frame,
                text=plugin_id.capitalize(),
                font=('Arial', 9),
                bg='#34495e',
                fg='#ecf0f1',
                anchor=tk.W
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.status_labels[plugin_id] = status_label
        
        tk.Button(
            self.panel,
            text="Gérer",
            font=('Arial', 9, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            command=self.open_manager
        ).pack(pady=10)
        
        # Mise à jour automatique
        self.update_status()
    
    def update_status(self):
        """Met à jour les indicateurs de statut"""
        for plugin_id, label in self.status_labels.items():
            plugin = self.manager.get_plugin(plugin_id)
            if plugin and plugin.is_initialized():
                label.config(fg='#2ecc71')  # Vert
            else:
                label.config(fg='#e74c3c')  # Rouge
        
        # Répéter toutes les 5 secondes
        self.panel.after(5000, self.update_status)
    
    def open_manager(self):
        """Ouvre le gestionnaire complet"""
        manager_win = tk.Toplevel(self.parent)
        PluginManagerUI(manager_win, self.manager)
    
    def pack(self, **kwargs):
        """Permet d'utiliser pack sur le panneau"""
        self.panel.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Permet d'utiliser grid sur le panneau"""
        self.panel.grid(**kwargs)


# Exemple d'utilisation
if __name__ == "__main__":
    # Importer le gestionnaire (à adapter selon votre structure)
    from plugin_manager import PluginManager, CameraPlugin, PrinterPlugin
    from plugin_manager import DecoratorPlugin, WiFiPlugin, KeyboardPlugin
    
    root = tk.Tk()
    
    # Créer et initialiser le gestionnaire
    manager = PluginManager()
    manager.load_config()
    
    # Enregistrer les plugins
    manager.register_plugin("camera", CameraPlugin)
    manager.register_plugin("printer", PrinterPlugin)
    manager.register_plugin("decorator", DecoratorPlugin)
    manager.register_plugin("wifi", WiFiPlugin)
    manager.register_plugin("keyboard", KeyboardPlugin)
    
    # Initialiser
    manager.initialize_all()
    
    # Créer l'interface de gestion
    app = PluginManagerUI(root, manager)
    
    root.mainloop()
    
    # Arrêter proprement
    manager.shutdown_all()
