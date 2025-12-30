#!/usr/bin/env python3
"""
Interface graphique pour PrintCounterAdvanced
CORRECTION TAILLE FENÊTRE - Adaptée à écran 1024x600
AVEC CLAVIER VIRTUEL pour saisie mot de passe
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path


class PasswordDialogWithKeyboard:
    """Dialogue de saisie de mot de passe avec clavier virtuel"""
    
    def __init__(self, parent, title="Mot de passe"):
        self.parent = parent
        self.title = title
        self.password = None
        
    def show_keyboard(self, password_entry, keyboard_parent):
        """Affiche le clavier virtuel"""
        keyboard_win = tk.Toplevel(keyboard_parent)
        keyboard_win.title("Clavier")
        keyboard_win.geometry("800x300")
        keyboard_win.configure(bg='#2c3e50')
        keyboard_win.transient(keyboard_parent)
        keyboard_win.attributes('-topmost', True)
        
        # Centrer
        keyboard_win.update_idletasks()
        x = (keyboard_win.winfo_screenwidth() // 2) - 400
        y = keyboard_parent.winfo_y() + keyboard_parent.winfo_height() + 10
        keyboard_win.geometry(f"800x300+{x}+{y}")
        
        def insert_char(char):
            password_entry.insert(tk.END, char)
        
        def backspace():
            text = password_entry.get()
            password_entry.delete(0, tk.END)
            password_entry.insert(0, text[:-1])
        
        def clear_all():
            password_entry.delete(0, tk.END)
        
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
    
    def ask_password(self):
        """Affiche la boîte de dialogue de saisie"""
        password_dialog = tk.Toplevel(self.parent)
        password_dialog.title(self.title)
        password_dialog.geometry("400x280")
        password_dialog.configure(bg='#2c3e50')
        password_dialog.transient(self.parent)
        password_dialog.grab_set()
        password_dialog.attributes('-topmost', True)
        
        # Centrer
        password_dialog.update_idletasks()
        x = (password_dialog.winfo_screenwidth() // 2) - 200
        y = (password_dialog.winfo_screenheight() // 2) - 140
        password_dialog.geometry(f"400x280+{x}+{y}")
        
        tk.Label(
            password_dialog,
            text=self.title,
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=20)
        
        tk.Label(
            password_dialog,
            text="Entrez le mot de passe admin :",
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
        
        # Bouton clavier virtuel
        tk.Button(
            password_dialog,
            text="⌨️ Clavier",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            width=12,
            command=lambda: self.show_keyboard(password_entry, password_dialog)
        ).pack(pady=5)
        
        def on_ok():
            self.password = password_entry.get()
            password_dialog.destroy()
        
        def on_cancel():
            self.password = None
            password_dialog.destroy()
        
        password_entry.bind('<Return>', lambda e: on_ok())
        
        btn_frame = tk.Frame(password_dialog, bg='#2c3e50')
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="Valider",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=12,
            height=2,
            command=on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Annuler",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=12,
            height=2,
            command=on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        password_dialog.wait_window()
        return self.password


class PrintCounterDialog:
    """Dialogue du compteur - OPTIMISÉ POUR PETIT ÉCRAN"""
    
    def __init__(self, parent, print_counter):
        self.parent = parent
        self.counter = print_counter
        
        # Créer la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Compteur d'Impressions")
        self.dialog.configure(bg='#2c3e50')
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        
        # CORRECTION: Taille adaptée à 1024x600 avec marge
        # Hauteur maximale : 580px pour laisser de la place
        self.create_ui()
    
    def create_ui(self):
        """Crée l'interface COMPACTE"""
        
        # Forcer le style Tkinter classique
        self.dialog.tk.call('tk', 'scaling', 1.0)    
        # Forcer dimensions
        self.dialog.update_idletasks()
        self.dialog.geometry("650x550")  # RÉDUIT de 750 à 550
        
        # Centrer
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - 325
        y = (screen_height // 2) - 275
        self.dialog.geometry(f"650x550+{x}+{y}")
        
        # Attendre que la fenêtre soit visible
        self.dialog.update()
        
        # Grab focus
        try:
            self.dialog.grab_set()
        except:
            pass
        
        # En-tête RÉDUIT
        header = tk.Frame(self.dialog, bg='#34495e', height=60)  # RÉDUIT de 80 à 60
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 COMPTEUR",
            font=('Arial', 18, 'bold'),  # RÉDUIT de 20 à 18
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=18)
        
        # Zone principale avec scroll
        main_container = tk.Frame(self.dialog, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # RÉDUIT padding
        
        canvas = tk.Canvas(main_container, bg='#2c3e50', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview, width=20)
        content_frame = tk.Frame(canvas, bg='#2c3e50')
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === SECTION 1 : IMPRESSIONS (COMPACT) ===
        prints_frame = tk.Frame(content_frame, bg='#e74c3c', relief=tk.RIDGE, bd=2)
        prints_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            prints_frame,
            text="🖨️ Impressions",
            font=('Arial', 12, 'bold'),  # RÉDUIT
            bg='#e74c3c',
            fg='white'
        ).pack(pady=5)
        
        tk.Label(
            prints_frame,
            text=str(self.counter.total_prints),
            font=('Arial', 36, 'bold'),  # RÉDUIT de 48 à 36
            bg='#e74c3c',
            fg='white'
        ).pack(pady=5)
        
        # === SECTION 2 : PHOTOS TOTALES (COMPACT) ===
        photos_frame = tk.Frame(content_frame, bg='#3498db', relief=tk.RIDGE, bd=2)
        photos_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            photos_frame,
            text="📷 Photos Prises",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white'
        ).pack(pady=5)
        
        tk.Label(
            photos_frame,
            text=str(self.counter.total_photos),
            font=('Arial', 36, 'bold'),
            bg='#3498db',
            fg='white'
        ).pack(pady=5)
        
        # === SECTION 3 : PHOTOS PAR STYLE (COMPACT) ===
        styles_frame = tk.Frame(content_frame, bg='#34495e', relief=tk.RIDGE, bd=2)
        styles_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            styles_frame,
            text="🎨 Par Style",
            font=('Arial', 13, 'bold'),  # RÉDUIT
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=8)
        
        # Icônes et couleurs par style
        style_icons = {
            'polaroid': ('📸', '#9b59b6'),
            'vintage': ('🎞️', '#e67e22'),
            'stamp': ('✉️', '#e74c3c'),
            'fete': ('🎉', '#f39c12'),
            'normal': ('📷', '#3498db')
        }
        
        for style, count in self.counter.photos_by_style.items():
            icon, color = style_icons.get(style, ('📷', '#95a5a6'))
            
            style_row = tk.Frame(styles_frame, bg='#2c3e50', relief=tk.RAISED, bd=1)
            style_row.pack(fill=tk.X, padx=10, pady=3)  # RÉDUIT padding
            
            # Icône
            tk.Label(
                style_row,
                text=icon,
                font=('Arial', 16),  # RÉDUIT de 20 à 16
                bg='#2c3e50',
                fg='white',
                width=3
            ).pack(side=tk.LEFT, padx=8, pady=5)
            
            # Nom du style
            tk.Label(
                style_row,
                text=style.capitalize(),
                font=('Arial', 12, 'bold'),  # RÉDUIT
                bg='#2c3e50',
                fg='#ecf0f1',
                anchor=tk.W,
                width=10
            ).pack(side=tk.LEFT, padx=5)
            
            # Compteur
            tk.Label(
                style_row,
                text=str(count),
                font=('Arial', 16, 'bold'),  # RÉDUIT
                bg='#2c3e50',
                fg=color,
                width=6
            ).pack(side=tk.RIGHT, padx=10)
        
        # === SECTION 4 : INFOS GALERIE (COMPACT) ===
        gallery_info = self.counter.get_gallery_info()
        
        gallery_frame = tk.Frame(content_frame, bg='#16a085', relief=tk.RIDGE, bd=2)
        gallery_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            gallery_frame,
            text="🗂️ Galerie",
            font=('Arial', 12, 'bold'),
            bg='#16a085',
            fg='white'
        ).pack(pady=6)
        
        info_items = [
            ("Fichiers", str(gallery_info['total_files'])),
            ("Taille", gallery_info.get('total_size_mb', 'N/A'))
        ]
        
        for label, value in info_items:
            row = tk.Frame(gallery_frame, bg='#16a085')
            row.pack(fill=tk.X, padx=15, pady=2)
            
            tk.Label(
                row,
                text=f"{label}:",
                font=('Arial', 10),  # RÉDUIT
                bg='#16a085',
                fg='white',
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=('Arial', 10, 'bold'),
                bg='#16a085',
                fg='white'
            ).pack(side=tk.RIGHT)
        
        # === BOUTONS D'ACTION (TOUJOURS VISIBLES) ===
        action_frame = tk.Frame(self.dialog, bg='#34495e', height=85)  # RÉDUIT
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        action_frame.pack_propagate(False)
        
        btn_container = tk.Frame(action_frame, bg='#34495e')
        btn_container.pack(expand=True, pady=10)
        
        btn_reset = tk.Button(
            btn_container,
            text="🔄 Reset",
            font=('Arial', 10, 'bold'),
            bg='#e67e22',
            fg='white',
            activebackground='#d35400',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            width=15,
            height=2,
            command=self.reset_counter_only
        )
        btn_reset.pack(side=tk.LEFT, padx=4)
        
        btn_reset_all = tk.Button(
            btn_container,
            text="🗑️ Reset + Galerie",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            width=16,
            height=2,
            command=self.reset_all
        )
        btn_reset_all.pack(side=tk.LEFT, padx=4)
        
        btn_close = tk.Button(
            btn_container,
            text="Fermer",
            font=('Arial', 10, 'bold'),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            width=10,
            height=2,
            command=self.dialog.destroy
        )
        btn_close.pack(side=tk.LEFT, padx=4)
    
    def reset_counter_only(self):
        """Réinitialise uniquement le compteur"""
        # Utiliser le dialogue personnalisé avec clavier
        pwd_dialog = PasswordDialogWithKeyboard(self.dialog, "Reset Compteur")
        password = pwd_dialog.ask_password()
        
        if not password:
            return
        
        success, message = self.counter.reset(password, clear_photos=False)
        
        if success:
            messagebox.showinfo("Succès", message, parent=self.dialog)
            self.dialog.destroy()
        else:
            messagebox.showerror("Erreur", message, parent=self.dialog)
    
    def reset_all(self):
        """Réinitialise compteur ET vide la galerie"""
        # Confirmation
        confirm = messagebox.askyesno(
            "Confirmation",
            "⚠️ ATTENTION ⚠️\n\n"
            "Cette action va :\n"
            "• Réinitialiser les compteurs\n"
            "• Supprimer TOUTES les photos\n"
            "• Créer un backup\n\n"
            "Continuer ?",
            parent=self.dialog,
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Utiliser le dialogue personnalisé avec clavier
        pwd_dialog = PasswordDialogWithKeyboard(self.dialog, "Reset Complet")
        password = pwd_dialog.ask_password()
        
        if not password:
            return
        
        # Réinitialisation
        success, message = self.counter.reset(
            password, 
            clear_photos=True, 
            create_backup=True
        )
        
        if success:
            messagebox.showinfo(
                "Succès",
                f"✅ {message}\n\nCompteurs remis à zéro.\nGalerie vidée.",
                parent=self.dialog
            )
            self.dialog.destroy()
        else:
            messagebox.showerror("Erreur", message, parent=self.dialog)


# Fonction d'intégration
def show_print_counter_dialog(parent, print_counter):
    """Affiche le dialogue du compteur"""
    try:
        dialog = PrintCounterDialog(parent, print_counter)
        parent.wait_window(dialog.dialog)
    except Exception as e:
        print(f"Erreur dialogue compteur: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le compteur:\n{e}")


# Test
if __name__ == "__main__":
    from print_counter_advanced import PrintCounterAdvanced
    
    root = tk.Tk()
    root.title("Test Interface")
    root.geometry("400x300")
    root.configure(bg='#2c3e50')
    
    counter = PrintCounterAdvanced()
    counter.increment_session(4, 'polaroid')
    counter.increment_session(3, 'vintage')
    counter.increment_print()
    counter.increment_print()
    
    tk.Button(
        root,
        text="Ouvrir Compteur",
        font=('Arial', 14, 'bold'),
        bg='#3498db',
        fg='white',
        width=20,
        height=3,
        command=lambda: show_print_counter_dialog(root, counter)
    ).pack(expand=True)
    
    root.mainloop()
