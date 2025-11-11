# 📇 Quick Reference Card - z/OS MIPS Prediction

## 🔗 URLs Importants

| Ressource | URL |
|-----------|-----|
| **Colab Notebook** | https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb |
| **GitHub Repo** | https://github.com/chelvy/Perf_Plan |
| **Clone URL** | https://github.com/chelvy/Perf_Plan.git |

---

## ⚡ Commandes Essentielles

### Sur Google Colab (Copy-Paste)

```python
# Installation complète automatique
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!python run_colab.py
```

### Transformation Données Pivot (Si nécessaire)

```python
# Si vos données ont dates en colonnes et indicateurs en lignes
from google.colab import files
uploaded = files.upload()
pivot_file = list(uploaded.keys())[0]
!python src/transform_pivot.py {pivot_file}
# Fichier transformé créé: {pivot_file}_transformed.csv
```

### Localement

```bash
# Clone
git clone https://github.com/chelvy/Perf_Plan.git
cd Perf_Plan

# Install
pip install -r requirements.txt

# Transformer données pivot (si nécessaire)
python src/transform_pivot.py votre_fichier_pivot.csv

# Créer données d'exemple
python main.py create-sample

# Entraîner
python main.py train --data-path data/sample/sample_mips_data.csv --mode both

# Prédire
python main.py predict \
    --model-path models/best_model.pkl \
    --preprocessor-path models/preprocessor.pkl \
    --input new_data.csv \
    --output predictions.csv
```

---

## 📊 Structure des Données

**Colonnes Requises:**
```
application, timestamp, M24H, MDIU, MPTE, TXDIU, EFF, TVDIU, MIPS_consumption
```

**Exemple CSV:**
```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
APP_001,2022-01-01,1000,800,1200,50,0.95,100,950
APP_002,2022-01-01,1500,1200,1800,75,0.90,150,1350
```

---

## 🎯 Modèles Disponibles

### Régression
- `linear` - Linear Regression
- `ridge_1.0` - Ridge (α=1.0)
- `lasso_1.0` - Lasso (α=1.0)
- `elasticnet` - ElasticNet
- `sgd` - SGD Regressor
- `bayesian_ridge` - Bayesian Ridge

### Classification
- `logistic_l2_C1.0` - Logistic Regression
- `ridge_1.0` - Ridge Classifier
- `sgd_log` - SGD Classifier

### Baselines
- `baseline_mean` - Mean predictor
- `baseline_median` - Median predictor
- `baseline_majority` - Majority class

---

## 📈 Métriques Principales

### Régression
- **RMSE** - Root Mean Squared Error (plus bas = mieux)
- **R²** - Coefficient de détermination (plus haut = mieux, max 1.0)
- **MAE** - Mean Absolute Error
- **MAPE** - Mean Absolute Percentage Error (%)

### Classification
- **Accuracy** - (1/n) × Σ 𝟙[ŷᵢ = yᵢ] (plus haut = mieux)
- **F1-Score** - Harmonic mean de precision/recall
- **Precision** - TP / (TP + FP)
- **Recall** - TP / (TP + FN)

---

## 🔧 Configuration Rapide

```python
config = {
    'data_path': 'data/sample/sample_mips_data.csv',
    'test_size': 0.2,           # 20% pour test
    'scaler_type': 'standard',  # standard/minmax/robust
    'feature_engineering': True,
    'n_categories': 3,          # LOW/MEDIUM/HIGH
}
```

---

## 📁 Structure du Projet

```
Perf_Plan/
├── src/                    # Code source
│   ├── data_loader.py     # Chargement données
│   ├── preprocessing.py   # Preprocessing
│   ├── features.py        # Feature engineering
│   ├── training.py        # Pipeline entraînement
│   ├── evaluation.py      # Évaluation
│   ├── visualization.py   # Visualisations
│   └── models/
│       ├── regression.py  # Modèles régression
│       └── classification.py
├── notebooks/             # Notebooks Jupyter
├── data/                  # Données
├── models/               # Modèles entraînés
├── results/              # Résultats
├── main.py              # CLI principal
└── run_colab.py         # Script Colab
```

---

## 💡 Tips Rapides

- **Premier test**: Utilisez le notebook Colab complet
- **Production**: Utilisez `run_colab.py` ou CLI `main.py`
- **Debugging**: Activez `MIPS_LOG_LEVEL=DEBUG`
- **Performance**: Activez `feature_engineering=True`
- **Données bruitées**: Utilisez `scaler_type='robust'`
- **Plus de stabilité**: Augmentez `test_size=0.3`

---

## ⏱️ Temps Estimés (Colab gratuit)

- Setup: 2-3 min
- 2000 records: ~8-12 min total
- 5000 records: ~15-20 min total
- 10000 records: ~30-40 min total

---

## 🆘 Dépannage Express

| Problème | Solution |
|----------|----------|
| Module not found | `sys.path.insert(0, 'src')` |
| Permission denied | `chmod +x script.sh` |
| GPU out of memory | Utilisez CPU (pas de GPU nécessaire) |
| Session timeout | Sauvegardez dans Google Drive |
| Mauvaise performance | Activez feature engineering |

---

## 📚 Documentation

| Document | Usage |
|----------|-------|
| **COLAB_READY.md** | ⭐ Commandes prêtes à l'emploi |
| **COLAB_QUICKSTART.md** | Copy-paste rapide |
| **COLAB_GUIDE.md** | Guide complet détaillé |
| **TRANSFORM_GUIDE.md** | 🔄 Transformer données pivot |
| **UPLOAD_GUIDE.md** | 📤 Uploader vos données |
| **UPLOAD_QUICKSTART.md** | 📤 Upload rapide (3 min) |
| **README.md** | Documentation générale |

---

## 🎓 Workflow Typique

1. **Clone** le repo sur Colab
2. **Transformez** vos données pivot (si nécessaire)
3. **Créez** ou uploadez vos données
4. **Entraînez** avec `run_colab.py`
5. **Comparez** les modèles
6. **Téléchargez** le meilleur
7. **Déployez** en production

---

## 🔮 Exemple de Prédiction

```python
from src.models.regression import MIPSRegressionModel
from src.preprocessing import MIPSPreprocessor

# Charger
model = MIPSRegressionModel.load('models/best_model.pkl')
prep = MIPSPreprocessor.load('models/preprocessor.pkl')

# Préparer
X_scaled = prep.transform(new_data)

# Prédire
predictions = model.predict(X_scaled)
```

---

**Prêt à utiliser ! 🚀**

Toutes les URLs utilisent maintenant `chelvy` ✅
