#!/usr/bin/env python3
"""
Interface de configuration WiFi complète - Correction clavier virtuel
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
from pathlib import Path


class WiFiConfigDialog:
    """Dialogue de configuration WiFi"""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_file = Path.home() / ".photovinc_wifi_configured"
        self.connected = False
        
    def check_wifi_connection(self):
        """Vérifie si le WiFi est déjà connecté"""
        try:
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                return True, result.stdout.strip()
            return False, None
        except:
            return False, None
    
    def scan_networks(self):
        """Scanner les réseaux WiFi disponibles"""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3 and parts[0]:
                            ssid = parts[0]
                            signal = parts[1]
                            security = parts[2]
                            networks.append({
                                'ssid': ssid,
                                'signal': signal,
                                'security': security
                            })
                return sorted(networks, key=lambda x: int(x['signal']) if x['signal'].isdigit() else 0, reverse=True)
            return []
        except Exception as e:
            print(f"Erreur scan: {e}")
            return []
    
    def connect_to_network(self, ssid, password=""):
        """Se connecter à un réseau WiFi"""
        try:
            if password:
                result = subprocess.run(
                    ['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                result = subprocess.run(
                    ['nmcli', 'device', 'wifi', 'connect', ssid],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                return True, "Connexion reussie !"
            else:
                return False, result.stderr or "Echec de connexion"
        except subprocess.TimeoutExpired:
            return False, "Timeout - connexion trop longue"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def show_config_dialog(self):
        """Affiche le dialogue de configuration WiFi"""
        is_connected, current_ssid = self.check_wifi_connection()
        
        if is_connected:
            response = messagebox.askyesno(
                "WiFi Deja Connecte",
                f"Vous etes deja connecte a : {current_ssid}\n\nVoulez-vous changer de reseau ?",
                parent=self.parent
            )
            if not response:
                self.config_file.touch()
                return True
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Configuration WiFi")
        dialog.geometry("600x550")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f"600x550+{x}+{y}")
        
        tk.Label(
            dialog,
            text="CONFIGURATION WIFI",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        tk.Label(
            dialog,
            text="Selectionnez votre reseau WiFi :",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=5)
        
        list_frame = tk.Frame(dialog, bg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        networks_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=12
        )
        networks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=networks_listbox.yview)
        
        status_label = tk.Label(
            dialog,
            text="Recherche des reseaux...",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#f39c12'
        )
        status_label.pack(pady=5)
        
        networks_data = []
        selected_network = [None]
        
        def refresh_networks():
            networks_listbox.delete(0, tk.END)
            status_label.config(text="Recherche des reseaux...", fg='#f39c12')
            dialog.update()
            
            networks = self.scan_networks()
            networks_data.clear()
            networks_data.extend(networks)
            
            if networks:
                for net in networks:
                    security_icon = "[*]" if net['security'] else "[ ]"
                    signal_percent = net['signal'] if net['signal'].isdigit() else "?"
                    display_text = f"{security_icon} {net['ssid']}  ({signal_percent}%)"
                    networks_listbox.insert(tk.END, display_text)
                status_label.config(text=f"{len(networks)} reseaux trouves", fg='#2ecc71')
            else:
                status_label.config(text="Aucun reseau trouve", fg='#e74c3c')
        
        def on_connect():
            selection = networks_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selection requise", "Veuillez selectionner un reseau", parent=dialog)
                return
            
            idx = selection[0]
            selected_network[0] = networks_data[idx]
            
            if selected_network[0]['security']:
                password_dialog = tk.Toplevel(dialog)
                password_dialog.title("Mot de passe WiFi")
                password_dialog.geometry("400x250")
                password_dialog.configure(bg='#2c3e50')
                password_dialog.transient(dialog)
                password_dialog.grab_set()
                # CORRECTION: Forcer la fenêtre au-dessus
                password_dialog.attributes('-topmost', True)
                
                password_dialog.update_idletasks()
                x = (password_dialog.winfo_screenwidth() // 2) - 200
                y = (password_dialog.winfo_screenheight() // 2) - 125
                password_dialog.geometry(f"400x250+{x}+{y}")
                
                tk.Label(
                    password_dialog,
                    text=f"Reseau : {selected_network[0]['ssid']}",
                    font=('Arial', 12, 'bold'),
                    bg='#2c3e50',
                    fg='#ecf0f1'
                ).pack(pady=15)
                
                tk.Label(
                    password_dialog,
                    text="Mot de passe :",
                    font=('Arial', 11),
                    bg='#2c3e50',
                    fg='#ecf0f1'
                ).pack(pady=5)
                
                password_entry = tk.Entry(
                    password_dialog,
                    font=('Arial', 12),
                    show='*',
                    width=30
                )
                password_entry.pack(pady=10)
                password_entry.focus()
                
                # Ajouter bouton clavier virtuel si disponible
                try:
                    from plugin_manager import KeyboardPlugin
                    
                    def show_keyboard():
                        # CORRECTION: Passer password_dialog comme parent
                        keyboard_win = tk.Toplevel(password_dialog)
                        keyboard_win.title("Clavier")
                        keyboard_win.geometry("800x300")
                        keyboard_win.configure(bg='#2c3e50')
                        keyboard_win.transient(password_dialog)
                        # CRITIQUE: Toujours au-dessus
                        keyboard_win.attributes('-topmost', True)
                        
                        # Centrer
                        keyboard_win.update_idletasks()
                        x = (keyboard_win.winfo_screenwidth() // 2) - 400
                        y = password_dialog.winfo_y() + password_dialog.winfo_height() + 10
                        keyboard_win.geometry(f"800x300+{x}+{y}")
                        
                        current_entry = [password_entry]
                        
                        def insert_char(char):
                            if current_entry[0]:
                                current_entry[0].insert(tk.END, char)
                        
                        def backspace():
                            if current_entry[0]:
                                text = current_entry[0].get()
                                current_entry[0].delete(0, tk.END)
                                current_entry[0].insert(0, text[:-1])
                        
                        def clear_all():
                            if current_entry[0]:
                                current_entry[0].delete(0, tk.END)
                        
                        # Layout du clavier
                        keys_layout = [
                            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                            ['a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                            ['q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm'],
                            ['w', 'x', 'c', 'v', 'b', 'n', '@', '.', '-', '_']
                        ]
                        
                        keys_frame = tk.Frame(keyboard_win, bg='#2c3e50')
                        keys_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
                        
                        for row_idx, row in enumerate(keys_layout):
                            row_frame = tk.Frame(keys_frame, bg='#2c3e50')
                            row_frame.pack(pady=2)
                            for key in row:
                                tk.Button(
                                    row_frame,
                                    text=key,
                                    font=('Arial', 14, 'bold'),
                                    width=5,
                                    height=2,
                                    bg='#34495e',
                                    fg='white',
                                    command=lambda k=key: insert_char(k)
                                ).pack(side=tk.LEFT, padx=2)
                        
                        # Boutons spéciaux
                        special_frame = tk.Frame(keyboard_win, bg='#2c3e50')
                        special_frame.pack(pady=5)
                        
                        tk.Button(
                            special_frame,
                            text="ESPACE",
                            font=('Arial', 12, 'bold'),
                            width=20,
                            height=2,
                            bg='#34495e',
                            fg='white',
                            command=lambda: insert_char(' ')
                        ).pack(side=tk.LEFT, padx=5)
                        
                        tk.Button(
                            special_frame,
                            text="⌫",
                            font=('Arial', 14, 'bold'),
                            width=8,
                            height=2,
                            bg='#e67e22',
                            fg='white',
                            command=backspace
                        ).pack(side=tk.LEFT, padx=5)
                        
                        tk.Button(
                            special_frame,
                            text="EFFACER",
                            font=('Arial', 12, 'bold'),
                            width=12,
                            height=2,
                            bg='#e74c3c',
                            fg='white',
                            command=clear_all
                        ).pack(side=tk.LEFT, padx=5)
                        
                        tk.Button(
                            special_frame,
                            text="FERMER",
                            font=('Arial', 12, 'bold'),
                            width=12,
                            height=2,
                            bg='#95a5a6',
                            fg='white',
                            command=keyboard_win.destroy
                        ).pack(side=tk.LEFT, padx=5)
                    
                    tk.Button(
                        password_dialog,
                        text="⌨️ Clavier",
                        font=('Arial', 10),
                        bg='#3498db',
                        fg='white',
                        width=12,
                        command=show_keyboard
                    ).pack(pady=5)
                except:
                    pass
                
                def do_connect():
                    password = password_entry.get()
                    if not password:
                        messagebox.showwarning("Mot de passe requis", "Veuillez entrer le mot de passe", parent=password_dialog)
                        return
                    
                    password_dialog.destroy()
                    attempt_connection(password)
                
                password_entry.bind('<Return>', lambda e: do_connect())
                
                btn_frame = tk.Frame(password_dialog, bg='#2c3e50')
                btn_frame.pack(pady=15)
                
                tk.Button(
                    btn_frame,
                    text="Connexion",
                    font=('Arial', 12, 'bold'),
                    bg='#27ae60',
                    fg='white',
                    width=12,
                    height=2,
                    command=do_connect
                ).pack(side=tk.LEFT, padx=5)
                
                tk.Button(
                    btn_frame,
                    text="Annuler",
                    font=('Arial', 12),
                    bg='#95a5a6',
                    fg='white',
                    width=12,
                    height=2,
                    command=password_dialog.destroy
                ).pack(side=tk.LEFT, padx=5)
                
            else:
                attempt_connection("")
        
        def attempt_connection(password):
            status_label.config(text=f"Connexion a {selected_network[0]['ssid']}...", fg='#f39c12')
            dialog.update()
            
            success, message = self.connect_to_network(selected_network[0]['ssid'], password)
            
            if success:
                status_label.config(text=message, fg='#2ecc71')
                self.config_file.touch()
                self.connected = True
                messagebox.showinfo("Succes", f"Connecte a {selected_network[0]['ssid']} !", parent=dialog)
                dialog.destroy()
            else:
                status_label.config(text="Echec de connexion", fg='#e74c3c')
                messagebox.showerror("Erreur", f"Impossible de se connecter :\n{message}", parent=dialog)
        
        def on_skip():
            if messagebox.askyesno("Ignorer", "Voulez-vous vraiment ignorer la configuration WiFi ?", parent=dialog):
                self.config_file.touch()
                dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg='#2c3e50')
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Actualiser",
            font=('Arial', 11, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            height=2,
            command=refresh_networks
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Se connecter",
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            height=2,
            command=on_connect
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Ignorer",
            font=('Arial', 11, 'bold'),
            bg='#95a5a6',
            fg='white',
            width=12,
            height=2,
            command=on_skip
        ).pack(side=tk.LEFT, padx=5)
        
        dialog.after(500, refresh_networks)
        dialog.wait_window()
        
        return self.connected
