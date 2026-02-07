# utils/auto_commit.py
import subprocess
import os
from datetime import datetime
import json

def auto_commit(training_metrics=None, message=None):
    """
    Commit automatique des résultats d'entraînement
    
    Args:
        training_metrics: dict avec les métriques (optionnel)
        message: message de commit personnalisé (optionnel)
    """
    if message is None:
        if training_metrics:
            epoch = training_metrics.get('epoch', 'N/A')
            map50 = training_metrics.get('mAP50', 'N/A')
            message = f"Training epoch {epoch} - mAP50: {map50} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            message = f"Auto-commit - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Vérifie qu'on est dans un repo git
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Erreur: pas dans un repo git")
        return False
    
    # Ajoute tous les fichiers
    subprocess.run(['git', 'add', '.'], check=True)
    
    # Vérifie s'il y a des changements
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    
    if result.stdout.strip():
        # Commit
        subprocess.run(['git', 'commit', '-m', message], check=True)
        
        # Push
        try:
            subprocess.run(['git', 'push'], check=True, timeout=30)
            print(f"✅ Committed et pushed: {message}")
            return True
        except subprocess.TimeoutExpired:
            print("⚠️ Push timeout - les changements sont commitées localement")
            return False
    else:
        print("ℹ️ Aucun changement à commiter")
        return False

if __name__ == "__main__":
    auto_commit()