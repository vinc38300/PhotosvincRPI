 
#!/usr/bin/env python3
"""
Script pour changer le mot de passe admin du photovinc
Modifie à la fois le compteur d'impressions et les statistiques
"""

import json
from pathlib import Path
import getpass
import sys

def load_config(filepath):
    """Charge un fichier de configuration JSON"""
    if filepath.exists():
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lecture {filepath}: {e}")
            return None
    return None

def save_config(filepath, data):
    """Sauvegarde un fichier de configuration JSON"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur écriture {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Changement du mot de passe admin - photovinc")
    print("=" * 60)
    print()
    
    # Fichiers de configuration
    counter_file = Path.home() / ".photovinc_print_counter.json"
    
    # Charger la configuration actuelle
    counter_data = load_config(counter_file)
    
    if not counter_data:
        print("Aucune configuration trouvée.")
        print("Création d'une nouvelle configuration...")
        counter_data = {
            'counter': 0,
            'password': 'admin123'
        }
    
    current_password = counter_data.get('password', 'admin123')
    
    print(f"Fichier de configuration: {counter_file}")
    print()
    
    # Vérifier l'ancien mot de passe
    print("Étape 1/3 - Vérification")
    old_password = getpass.getpass("Ancien mot de passe: ")
    
    if old_password != current_password:
        print()
        print("Erreur: Mot de passe incorrect")
        sys.exit(1)
    
    print("Mot de passe vérifié")
    print()
    
    # Demander le nouveau mot de passe
    print("Étape 2/3 - Nouveau mot de passe")
    while True:
        new_password = getpass.getpass("Nouveau mot de passe: ")
        
        if len(new_password) < 4:
            print("Erreur: Le mot de passe doit contenir au moins 4 caractères")
            continue
        
        confirm_password = getpass.getpass("Confirmer le mot de passe: ")
        
        if new_password != confirm_password:
            print("Erreur: Les mots de passe ne correspondent pas")
            continue
        
        break
    
    print()
    print("Étape 3/3 - Sauvegarde")
    
    # Mettre à jour la configuration
    counter_data['password'] = new_password
    
    # Sauvegarder
    if save_config(counter_file, counter_data):
        print(f"Configuration mise à jour: {counter_file}")
    else:
        print("Erreur lors de la sauvegarde")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Mot de passe changé avec succès !")
    print("=" * 60)
    print()
    print("Le nouveau mot de passe est actif pour :")
    print("  - Compteur d'impressions")
    print("  - Statistiques (Analytics)")
    print()
    print("Conservez ce mot de passe en lieu sûr.")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOpération annulée")
        sys.exit(0)
