#!/usr/bin/env python3
"""
Lance PhotoVinc en mode DEMO (sans matériel)
"""

import sys
import os

# Ajouter le dossier courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et modifier le plugin manager pour utiliser le mode démo
from plugin_manager import PluginManager
from demo_mode_plugin import register_demo_plugins

# Créer le gestionnaire
manager = PluginManager()
manager.load_config()

# IMPORTANT: Enregistrer les plugins DEMO au lieu des vrais
register_demo_plugins(manager)

# Initialiser les plugins
results = manager.initialize_all()

print("\n=== Mode DEMO activé ===")
for name, success in results.items():
    print(f"{'✓' if success else '✗'} {name}")

# Maintenant lancer l'interface graphique avec les plugins démo
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

import tkinter as tk
from integration_complete import photovincAppComplete

root = tk.Tk()

# Passer le manager avec les plugins démo à l'application
app = photovincAppComplete(root)
app.plugin_manager = manager  # Remplacer par le manager démo

root.mainloop()
