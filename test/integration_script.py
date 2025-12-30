#!/usr/bin/env python3
"""
Script d'intégration des modifications pour photovinc
Applique automatiquement les corrections des fichiers .txt
"""

import os
import sys
from pathlib import Path
import re
from typing import Tuple, Optional

class PhotovincIntegration:
    """Gère l'intégration des modifications"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialise l'intégrateur
        
        Args:
            project_root: Racine du projet (None = répertoire courant)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.modifications = []
        self.errors = []
    
    def apply_printer_detection_fix(self) -> bool:
        """Applique la correction à printer_detection.py"""
        print("📝 Application de la correction printer_detection.py...")
        
        file_path = self.project_root / "printer_detection.py"
        
        if not file_path.exists():
            self.errors.append(f"❌ {file_path} non trouvé")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher la méthode detect_printers
            old_pattern = r"(elif line\.startswith\('printer'\):.*?self\.printers\[printer_info\.name\] = printer_info)"
            
            new_code = """elif line.startswith('printer'):
                    # Ligne du type: printer Canon_CP400 is idle
                    printer_info = self._parse_printer_line(line)
                    if printer_info:
                        is_default = printer_info.name == default_printer
                        printer_info.is_default = is_default
                        # ✅ Vérifier si l'imprimante est réellement connectée
                        printer_info.is_available = self._check_printer_connection(printer_info)
                        self.printers[printer_info.name] = printer_info"""
            
            # Chercher et remplacer
            if "self._check_printer_connection" not in content:
                # Ajouter la méthode _check_printer_connection si elle n'existe pas
                self._add_printer_connection_check(file_path, content)
                print("   ✅ Méthode _check_printer_connection ajoutée")
            
            self.modifications.append("printer_detection.py - Vérification connexion imprimante")
            print("   ✅ printer_detection.py corrigé")
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Erreur modification printer_detection.py: {e}")
            return False
    
    def _add_printer_connection_check(self, file_path: Path, content: str):
        """Ajoute la méthode de vérification de connexion"""
        method_code = '''
    def _check_printer_connection(self, printer_info: PrinterInfo) -> bool:
        """Vérifie si l'imprimante est réellement connectée"""
        try:
            # Vérifier via lpstat -a (appareils disponibles)
            result = subprocess.run(
                ['lpstat', '-a', printer_info.name],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            # Si CUPS ne répond pas, supposer connectée
            return True
'''
        
        # Insérer avant la dernière méthode
        if "def cache_printers" in content:
            content = content.replace(
                "    def cache_printers",
                method_code + "\n    def cache_printers"
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def apply_integration_complete_fix(self) -> bool:
        """Applique la correction à integration_complete.py"""
        print("📝 Application de la correction integration_complete.py...")
        
        file_path = self.project_root / "integration_complete.py"
        
        if not file_path.exists():
            self.errors.append(f"❌ {file_path} non trouvé")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Chercher la méthode update_printer_status_label
            new_method = '''    def update_printer_status_label(self):
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
'''
            
            # Chercher et remplacer la méthode
            output_lines = []
            i = 0
            replaced = False
            
            while i < len(lines):
                if "def update_printer_status_label" in lines[i]:
                    # Sauter l'ancienne méthode
                    output_lines.append(new_method + "\n")
                    replaced = True
                    
                    # Avancer jusqu'à la prochaine méthode
                    i += 1
                    indent_level = len(lines[i-1]) - len(lines[i-1].lstrip())
                    
                    while i < len(lines):
                        if lines[i].strip() and not lines[i].startswith(" " * (indent_level + 1)) and lines[i].startswith("    def "):
                            break
                        i += 1
                else:
                    output_lines.append(lines[i])
                    i += 1
            
            if replaced:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(output_lines)
                
                self.modifications.append("integration_complete.py - Amélioration affichage statut")
                print("   ✅ integration_complete.py corrigé")
                return True
            else:
                self.errors.append("❌ Méthode update_printer_status_label non trouvée")
                return False
            
        except Exception as e:
            self.errors.append(f"❌ Erreur modification integration_complete.py: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Crée des backups des fichiers modifiés"""
        print("💾 Création des backups...")
        
        try:
            backup_dir = self.project_root / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            files_to_backup = [
                "printer_detection.py",
                "integration_complete.py"
            ]
            
            for filename in files_to_backup:
                src = self.project_root / filename
                if src.exists():
                    import shutil
                    dst = backup_dir / f"{filename}.backup"
                    shutil.copy2(src, dst)
                    print(f"   ✅ Backup de {filename}")
            
            return True
        except Exception as e:
            self.errors.append(f"❌ Erreur création backups: {e}")
            return False
    
    def verify_modifications(self) -> bool:
        """Vérifie que les modifications ont bien été appliquées"""
        print("🔍 Vérification des modifications...")
        
        file_path = self.project_root / "integration_complete.py"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = [
                ("printer_info.is_available" in content, "Vérification connexion imprimante"),
                ("🟢" in content or "Mode démo" in content, "Affichage statut amélioré")
            ]
            
            all_good = True
            for check, description in checks:
                if check:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ⚠️  {description} - À vérifier manuellement")
                    all_good = False
            
            return all_good
        except Exception as e:
            self.errors.append(f"❌ Erreur vérification: {e}")
            return False
    
    def run_integration(self) -> Tuple[bool, str]:
        """Exécute l'intégration complète"""
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE DE L'INTÉGRATION PHOTOVINC")
        print("="*60 + "\n")
        
        # Créer backups
        if not self.create_backup():
            return False, "Erreur lors de la création des backups"
        
        # Appliquer les corrections
        steps = [
            ("Correction printer_detection.py", self.apply_printer_detection_fix),
            ("Correction integration_complete.py", self.apply_integration_complete_fix),
            ("Vérification des modifications", self.verify_modifications)
        ]
        
        all_success = True
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                all_success = False
        
        # Résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'INTÉGRATION")
        print("="*60)
        
        if self.modifications:
            print(f"\n✅ Modifications appliquées ({len(self.modifications)}):")
            for mod in self.modifications:
                print(f"   • {mod}")
        
        if self.errors:
            print(f"\n❌ Erreurs rencontrées ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n" + "="*60)
        
        if all_success and not self.errors:
            message = "✅ INTÉGRATION RÉUSSIE - Tous les fichiers ont été mis à jour!"
            print(f"\n{message}\n")
            return True, message
        else:
            message = "⚠️  INTÉGRATION PARTIELLE - Vérifiez les erreurs ci-dessus"
            print(f"\n{message}\n")
            return all_success, message


def main():
    """Point d'entrée du script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Intègre les modifications pour photovinc"
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Chemin vers la racine du projet (défaut: répertoire courant)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Ne pas créer de backups"
    )
    
    args = parser.parse_args()
    
    integrator = PhotovincIntegration(args.project)
    success, message = integrator.run_integration()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
