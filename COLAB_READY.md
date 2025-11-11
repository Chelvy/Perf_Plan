# 🚀 Ready to Use - Google Colab Commands

Tous les liens sont maintenant configurés avec votre username **chelvy** !

---

## ✨ Option 1: Notebook All-in-One (Recommandé) ⭐

**NOUVEAU: Un seul notebook pour tout!**

### Lien Direct:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/01_complete_pipeline.ipynb)

**URL complète:**
```
https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/01_complete_pipeline.ipynb
```

**Inclut:**
- 🔄 Transformation pivot → ML
- 📤 Upload données
- 🎲 Données d'exemple
- 🚀 Entraînement complet
- 📊 Évaluation
- 💾 Téléchargement

**Étapes:**
1. Cliquez sur le badge ci-dessus
2. Section 2: Configurez votre source de données (pivot/upload/sample)
3. `Runtime` → `Run all` (ou Ctrl+F9)
4. Attendez ~8-15 minutes
5. Téléchargez `zos_mips_models_results.zip`

### Notebooks Spécialisés:

Si vous préférez des notebooks séparés:
- [Transformation pivot seule](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/05_transform_pivot_data.ipynb)
- [Upload et validation](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb)
- [Pipeline original](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)

---

## ⚡ Option 2: Script Python Automatique (Recommandé)

Créez une nouvelle cellule dans Google Colab et exécutez:

```python
# Clone et exécute le système complet
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!python run_colab.py
```

### Avec Options:

```python
# Plus de données (5000 records, 200 apps)
!python run_colab.py --n-samples 5000 --n-apps 200

# Seulement régression (plus rapide)
!python run_colab.py --mode regression

# Seulement classification
!python run_colab.py --mode classification

# Skip download automatique
!python run_colab.py --no-download
```

---

## 🔧 Option 3: Script Shell

```bash
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!bash run_colab.sh
```

---

## 📤 Avec Vos Propres Données

### Upload CSV:

```python
# Clone le repo
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan

# Install dependencies
!pip install -q -r requirements.txt

# Upload votre fichier
from google.colab import files
uploaded = files.upload()
data_file = list(uploaded.keys())[0]

# Train avec vos données
!python main.py train --data-path {data_file} --mode both --feature-engineering
```

### Depuis Google Drive:

```python
# Clone le repo
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!pip install -q -r requirements.txt

# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Train
!python main.py train \
    --data-path /content/drive/MyDrive/zos_data/mips_data.csv \
    --mode both \
    --feature-engineering \
    --output-dir /content/drive/MyDrive/zos_models
```

---

## 📊 Commandes Rapides Post-Entraînement

### Visualiser les Résultats:

```python
import json
from pathlib import Path

# Charger les résultats
results_files = list(Path('results').glob('training_summary_*.json'))
latest = max(results_files, key=lambda x: x.stat().st_mtime)

with open(latest) as f:
    results = json.load(f)

# Afficher le meilleur modèle
print("🏆 MEILLEUR MODÈLE DE RÉGRESSION:")
best_reg = min(results['regression'].items(),
               key=lambda x: x[1]['test']['rmse'] if 'test' in x[1] else float('inf'))
print(f"   Nom: {best_reg[0]}")
print(f"   RMSE: {best_reg[1]['test']['rmse']:.2f}")
print(f"   R²: {best_reg[1]['test']['r2']:.4f}")

print("\n🏆 MEILLEUR MODÈLE DE CLASSIFICATION:")
best_clf = max(results['classification'].items(),
               key=lambda x: x[1]['test']['accuracy'] if 'test' in x[1] else 0)
print(f"   Nom: {best_clf[0]}")
print(f"   Accuracy: {best_clf[1]['test']['accuracy']:.4f}")
print(f"   F1-Score: {best_clf[1]['test']['f1_macro']:.4f}")
```

### Télécharger les Modèles:

```python
from google.colab import files
import zipfile
from pathlib import Path

# Create ZIP
with zipfile.ZipFile('models_results.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in Path('models').rglob('*'):
        if file.is_file():
            zipf.write(file, f'models/{file.name}')
    for file in Path('results').rglob('*'):
        if file.is_file():
            zipf.write(file, f'results/{file.name}')

# Download
files.download('models_results.zip')
print("✅ Téléchargement lancé!")
```

### Faire des Prédictions:

```python
import sys
sys.path.insert(0, 'src')
import pandas as pd
from src.models.regression import MIPSRegressionModel
from src.preprocessing import MIPSPreprocessor
from src.features import MIPSFeatureEngineering

# Charger le meilleur modèle
model_files = list(Path('models').glob('best_regression_*.pkl'))
if model_files:
    model = MIPSRegressionModel.load(str(model_files[0]))

    # Charger le preprocessor
    preproc_files = list(Path('models').glob('preprocessor_*.pkl'))
    if preproc_files:
        preprocessor = MIPSPreprocessor.load(str(preproc_files[0]))

        # Nouvelles données
        new_data = pd.DataFrame({
            'application': ['APP_001', 'APP_002'],
            'timestamp': ['2025-01-01', '2025-01-02'],
            'M24H': [1200, 1500],
            'MDIU': [1000, 1300],
            'MPTE': [1400, 1700],
            'TXDIU': [60, 75],
            'EFF': [0.92, 0.88],
            'TVDIU': [120, 140]
        })

        # Feature engineering
        feature_eng = MIPSFeatureEngineering()
        new_data_fe = feature_eng.create_all_features(new_data)

        # Preprocess
        X_new = new_data_fe.drop(columns=['timestamp'], errors='ignore')
        X_new_scaled = preprocessor.transform(X_new)

        # Predict
        predictions = model.predict(X_new_scaled)

        # Afficher
        new_data['MIPS_Prediction'] = predictions.round(2)
        print("\n🔮 PRÉDICTIONS:")
        print(new_data[['application', 'M24H', 'MDIU', 'MIPS_Prediction']])
```

---

## 💾 Sauvegarder dans Google Drive

Pour ne pas perdre vos modèles si la session se déconnecte:

```python
from google.colab import drive
import shutil

# Mount Drive
drive.mount('/content/drive')

# Créer dossier dans Drive
!mkdir -p /content/drive/MyDrive/ZOS_MIPS_Models

# Copier modèles et résultats
!cp -r models /content/drive/MyDrive/ZOS_MIPS_Models/
!cp -r results /content/drive/MyDrive/ZOS_MIPS_Models/

print("✅ Modèles sauvegardés dans Google Drive!")
print("📁 Emplacement: MyDrive/ZOS_MIPS_Models/")
```

---

## 🔍 Vérifier l'État

```python
import os
from pathlib import Path

print("📊 ÉTAT DU PROJET\n" + "="*50)

# Working directory
print(f"📁 Répertoire: {os.getcwd()}")

# Models
if os.path.exists('models'):
    model_files = list(Path('models').glob('*.pkl'))
    print(f"\n🤖 Modèles: {len(model_files)} fichiers")
    for f in model_files[:5]:
        size = f.stat().st_size / 1024
        print(f"   - {f.name} ({size:.1f} KB)")
else:
    print("\n⚠️  Pas de modèles trouvés")

# Results
if os.path.exists('results'):
    result_files = list(Path('results').glob('*'))
    print(f"\n📈 Résultats: {len(result_files)} fichiers")
    for f in result_files[:5]:
        size = f.stat().st_size / 1024
        print(f"   - {f.name} ({size:.1f} KB)")
else:
    print("\n⚠️  Pas de résultats trouvés")

print("\n" + "="*50)
```

---

## ⏱️ Estimation des Temps

| Étape | Temps | Description |
|-------|-------|-------------|
| Clone repo | 10-20s | Clone depuis GitHub |
| Install deps | 1-2 min | Installation packages |
| Créer données | 5-10s | 2000 records |
| Train modèles | 3-5 min | 15+ modèles |
| Évaluation | 30s-1min | Métriques + viz |
| Download | 5-10s | ZIP file |
| **TOTAL** | **~8-12 min** | Pipeline complet |

---

## ✅ Checklist de Succès

Après exécution, vous devriez avoir:

- [x] Repository cloné dans `/content/Perf_Plan`
- [x] Dependencies installées (numpy, pandas, sklearn, etc.)
- [x] Données chargées (sample ou vos données)
- [x] 15+ modèles entraînés et évalués
- [x] Résultats sauvegardés dans `results/`
- [x] Modèles sauvegardés dans `models/`
- [x] ZIP file créé: `zos_mips_models_results.zip`
- [x] Meilleur modèle identifié avec métriques

---

## 🆘 Problèmes Courants

### "fatal: could not read Username"
```bash
# Utilisez HTTPS (déjà configuré)
!git clone https://github.com/chelvy/Perf_Plan.git
```

### "ModuleNotFoundError: No module named 'src'"
```python
import sys
sys.path.insert(0, 'src')
```

### "Permission denied"
```bash
chmod +x run_colab.py run_colab.sh
```

### Session déconnectée avant téléchargement
```python
# Utilisez Google Drive
from google.colab import drive
drive.mount('/content/drive')
!cp -r models results /content/drive/MyDrive/
```

---

## 📖 Documentation Complète

- **Guide Colab Détaillé**: [COLAB_GUIDE.md](COLAB_GUIDE.md)
- **Quick Start**: [COLAB_QUICKSTART.md](COLAB_QUICKSTART.md)
- **Documentation Générale**: [README.md](README.md)
- **Notebooks Interactifs**: `notebooks/`

---

## 🎯 Commande Ultra-Rapide (Copy-Paste)

**Tout en une commande:**

```python
# COPIEZ-COLLEZ CECI DANS COLAB 👇
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan && python run_colab.py && cd ..
```

Puis téléchargez le ZIP:
```python
from google.colab import files
files.download('Perf_Plan/zos_mips_models_results.zip')
```

**C'est tout ! 🎉**

---

## 📞 Support

- **Issues GitHub**: https://github.com/chelvy/Perf_Plan/issues
- **Documentation**: README.md dans le repo
- **Code source**: `src/` directory

---

**Dernière mise à jour:** Tous les liens utilisent maintenant `chelvy` ✅

**Prêt à utiliser !** 🚀
