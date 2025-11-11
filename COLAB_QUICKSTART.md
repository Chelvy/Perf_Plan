# ⚡ Colab Quick Start (Copy & Paste)

Ultra-rapide : copiez-collez ces commandes dans Google Colab !

---

## 🚀 Option 1: Notebook Complet (Recommandé)

### Ouvrez le notebook:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)

**Puis:**
- `Runtime` → `Run all` (ou `Ctrl+F9`)
- Attendez 5-10 minutes
- Téléchargez vos modèles

**C'est tout ! ✨**

---

## 🎯 Option 2: Script Automatique

Copiez-collez dans une cellule Colab:

```python
# Clone et exécute le système complet
!git clone https://github.com/YOUR_USERNAME/Perf_Plan.git
%cd Perf_Plan
!python run_colab.py
```

**Temps: ~5-10 minutes**

---

## 🛠️ Option 3: Script Shell

```bash
# Clone et setup
!git clone https://github.com/YOUR_USERNAME/Perf_Plan.git
%cd Perf_Plan

# Exécute tout
!bash run_colab.sh
```

---

## 📊 Option 4: Commandes Détaillées

Si vous voulez plus de contrôle:

### 1. Setup
```python
# Clone repository
!git clone https://github.com/YOUR_USERNAME/Perf_Plan.git
%cd Perf_Plan

# Install dependencies
!pip install -q -r requirements.txt

# Setup Python path
import sys
sys.path.insert(0, 'src')
```

### 2. Créer des données d'exemple
```python
from src.data_loader import create_sample_data

df = create_sample_data(
    'data/sample/sample_mips_data.csv',
    n_samples=2000,
    n_apps=100
)
print(f"Created {len(df)} records")
```

### 3. Entraîner les modèles
```python
from src.training import MIPSTrainingPipeline

config = {
    'data_path': 'data/sample/sample_mips_data.csv',
    'test_size': 0.2,
    'feature_engineering': True,
    'save_models': True
}

pipeline = MIPSTrainingPipeline(config)
results = pipeline.run_full_pipeline(mode='both')

print(f"\nBest model: {pipeline.best_model_name}")
```

### 4. Télécharger les résultats
```python
from google.colab import files
import zipfile
from pathlib import Path

# Create ZIP
with zipfile.ZipFile('models_results.zip', 'w') as zipf:
    for file in Path('models').rglob('*'):
        if file.is_file():
            zipf.write(file, f'models/{file.name}')
    for file in Path('results').rglob('*'):
        if file.is_file():
            zipf.write(file, f'results/{file.name}')

# Download
files.download('models_results.zip')
```

---

## 📤 Option 5: Avec Vos Données

### Uploader votre CSV:
```python
from google.colab import files

# Upload
print("Upload your MIPS data CSV...")
uploaded = files.upload()

# Get filename
DATA_PATH = list(uploaded.keys())[0]
print(f"Uploaded: {DATA_PATH}")
```

### Ou depuis Google Drive:
```python
from google.colab import drive

# Mount Drive
drive.mount('/content/drive')

# Set path
DATA_PATH = '/content/drive/MyDrive/your_folder/mips_data.csv'
```

### Puis entraîner:
```python
from src.training import MIPSTrainingPipeline

config = {
    'data_path': DATA_PATH,  # Votre fichier
    'test_size': 0.2,
    'feature_engineering': True,
}

pipeline = MIPSTrainingPipeline(config)
results = pipeline.run_full_pipeline(mode='both')
```

---

## 🎨 Visualisations Rapides

```python
from src.visualization import MIPSVisualizer
from src.evaluation import ModelEvaluator
import matplotlib.pyplot as plt

# Get best model results
best_name = pipeline.best_model_name
best_result = results['regression'][best_name]

# Visualize
viz = MIPSVisualizer('results')

# Reload test data for plotting
from src.data_loader import MIPSDataLoader
loader = MIPSDataLoader(DATA_PATH)
data = loader.load_csv()
train, test = loader.split_train_test(test_size=0.2, random_state=42)
_, y_test = loader.get_feature_target_split(test)

# Plot predictions
y_pred = best_result['predictions']['test']
viz.plot_predictions_vs_actual(y_test, y_pred, title=f"{best_name}")
viz.plot_residuals(y_test, y_pred, title=f"{best_name} - Residuals")
```

---

## 🔮 Faire des Prédictions

```python
import pandas as pd

# New data
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
from src.features import MIPSFeatureEngineering
feature_eng = MIPSFeatureEngineering()
new_data_fe = feature_eng.create_all_features(new_data)

# Preprocess
X_new = new_data_fe.drop(columns=['timestamp'], errors='ignore')
X_new_scaled = pipeline.preprocessor.transform(X_new)

# Predict
predictions = pipeline.best_model.predict(X_new_scaled)

# Display
new_data['Predicted_MIPS'] = predictions
print(new_data[['application', 'M24H', 'MDIU', 'Predicted_MIPS']])
```

---

## ⚙️ Configuration Personnalisée

```python
config = {
    # Data
    'data_path': 'your_data.csv',
    'test_size': 0.2,                    # 20% test
    'random_state': 42,
    'time_based_split': False,           # True for chronological split

    # Preprocessing
    'scaler_type': 'standard',           # standard/minmax/robust
    'handle_outliers': True,
    'outlier_method': 'clip',            # clip/remove/cap

    # Feature Engineering
    'feature_engineering': True,         # Highly recommended

    # Classification
    'n_categories': 3,                   # LOW/MEDIUM/HIGH
    'category_method': 'quantile',       # quantile/uniform

    # Output
    'save_models': True,
    'output_dir': 'models',
    'results_dir': 'results'
}

# Train
pipeline = MIPSTrainingPipeline(config)
results = pipeline.run_full_pipeline(mode='both')
```

---

## 📊 Comparer les Modèles

```python
from src.evaluation import ModelEvaluator
import pandas as pd

evaluator = ModelEvaluator()

# Regression comparison
if 'regression' in results:
    rmse_comp = evaluator.compare_models(results['regression'], 'rmse', 'regression')
    print("\n🔵 REGRESSION - Top 5 Models (RMSE):")
    print(rmse_comp.head().to_string(index=False))

    r2_comp = evaluator.compare_models(results['regression'], 'r2', 'regression')
    print("\n🔵 REGRESSION - Top 5 Models (R²):")
    print(r2_comp.head().to_string(index=False))

# Classification comparison
if 'classification' in results:
    acc_comp = evaluator.compare_models(results['classification'], 'accuracy', 'classification')
    print("\n🟢 CLASSIFICATION - Top 5 Models (Accuracy):")
    print(acc_comp.head().to_string(index=False))
```

---

## 💡 Trucs et Astuces

### Sauvegarder dans Drive au lieu de télécharger:
```python
from google.colab import drive
drive.mount('/content/drive')

# Copy to Drive
!cp -r models /content/drive/MyDrive/zos_mips_models
!cp -r results /content/drive/MyDrive/zos_mips_results
```

### Exécuter avec plus de données:
```python
!python run_colab.py --n-samples 5000 --n-apps 200
```

### Seulement régression (plus rapide):
```python
!python run_colab.py --mode regression
```

### Charger un modèle sauvegardé:
```python
from src.models.regression import MIPSRegressionModel
model = MIPSRegressionModel.load('models/best_model.pkl')
```

---

## ❓ Problèmes Fréquents

### "No module named 'src'"
```python
import sys
sys.path.insert(0, 'src')
```

### "File not found"
```python
# Vérifier le chemin
import os
print(f"Current dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")
```

### Session déconnectée
```python
# Sauvegarder dans Drive automatiquement
from google.colab import drive
drive.mount('/content/drive')
# Puis utiliser des chemins dans /content/drive/...
```

---

## 📚 Plus d'Info

- **Guide complet**: [COLAB_GUIDE.md](COLAB_GUIDE.md)
- **Documentation**: [README.md](README.md)
- **Notebooks**: `notebooks/`
- **Code source**: `src/`

---

## ⏱️ Temps Estimés

| Opération | Temps |
|-----------|-------|
| Setup | 2-3 min |
| Création données | <1 min |
| Entraînement | 3-5 min |
| Visualisations | 1-2 min |
| **TOTAL** | **~8-12 min** |

*Basé sur 2000 records, Colab gratuit*

---

## ✅ Checklist Rapide

Après exécution, vous devriez avoir:

- [ ] ✅ Dependencies installées
- [ ] ✅ Données chargées
- [ ] ✅ 15+ modèles entraînés
- [ ] ✅ Comparaisons affichées
- [ ] ✅ Meilleur modèle identifié
- [ ] ✅ Visualisations créées
- [ ] ✅ Modèles téléchargés/sauvegardés

**Si oui, vous êtes prêt ! 🎉**

---

**N'oubliez pas de remplacer `YOUR_USERNAME` par votre username GitHub !**
