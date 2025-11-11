# z/OS MIPS Prediction - Machine Learning System

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Vue d'ensemble

Ce projet implémente un système d'apprentissage machine pour prédire la consommation CPU (MIPS) des applications z/OS basé sur des données historiques de performance sur 3 ans.

## 🚀 Quick Start sur Google Colab

**Exécutez le système complet en 5 minutes sur Google Colab (gratuit) !**

### Option 1: Avec Données d'Exemple (Pour tester)
1. Cliquez sur le badge "Open in Colab" ci-dessus
2. Exécutez toutes les cellules (`Runtime` → `Run all`)
3. Téléchargez vos modèles entraînés

### Option 2: Avec Vos Propres Données z/OS ⭐
1. Cliquez sur le badge "Open in Colab" ci-dessus
2. Allez à **Step 2: Prepare Data → Option B**
3. Changez `USE_UPLOADED_DATA = True`
4. Uploadez votre fichier CSV (format dans [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md))
5. Exécutez le reste du notebook

### Option 3: Script Automatisé

```bash
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!bash run_colab.sh
```

📖 **Guides:**
- [COLAB_GUIDE.md](COLAB_GUIDE.md) - Guide complet Colab
- [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md) - Comment uploader vos données ⭐
- [TRANSFORM_QUICKSTART.md](TRANSFORM_QUICKSTART.md) - Transform rapide (5 min) 🔄
- [TRANSFORM_GUIDE.md](TRANSFORM_GUIDE.md) - Transform guide complet 🔄

### 🔄 Vos Données sont en Format Pivot?

Si vos données z/OS ont **des dates en colonnes** et **des indicateurs en lignes** (format pivot):

```
code_application | code_indicateur | 2022-04-01 | 2022-05-01 | ...
DEV-CICS         | MDIU           | 0,2717     | 0,196      | ...
```

**Transformez-les d'abord:**
1. Ouvrez le [notebook de transformation](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/05_transform_pivot_data.ipynb)
2. Uploadez votre fichier pivot
3. Téléchargez le fichier transformé
4. Utilisez-le dans le notebook principal

📖 Guide complet: [TRANSFORM_GUIDE.md](TRANSFORM_GUIDE.md)

## Problème

**Type:** Apprentissage supervisé (Régression et Classification)

**Objectif:** Prédire la consommation MIPS de chaque application z/OS en fonction de:
- Type d'application
- Codes indicateurs de performance temporels

## Codes Indicateurs

| Code | Description |
|------|-------------|
| M24H | MIPS sur 24 heures |
| MDIU | MIPS Diurne (pendant la journée) |
| MPTE | MIPS Pointe (période de pointe) |
| TXDIU | Taux DIU (x1000) |
| EFF | Efficacité |
| TVDIU | Temps Valeur DIU |

## Variables

- **Entrées (Features):**
  - Nom de l'application (encodé)
  - Codes indicateurs (M24H, MDIU, MPTE, TXDIU, EFF, TVDIU)
  - Timestamp/période temporelle

- **Cible (Target):**
  - Consommation CPU en MIPS (valeur continue pour régression)
  - Catégorie de consommation (pour classification: LOW/MEDIUM/HIGH)

## Dataset

- **Période:** 3 ans d'historique
- **Format:** CSV avec colonnes pour chaque application et ses indicateurs

## Approches de Modélisation

### 1. Régression (Approche Principale)
Prédire la valeur exacte de consommation MIPS:
- Linear Regression
- Ridge Regression
- Lasso Regression
- ElasticNet
- Polynomial Regression

**Métriques d'évaluation:**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score
- MAPE (Mean Absolute Percentage Error)

### 2. Classification Multi-classe
Prédire la catégorie de consommation MIPS:
- Logistic Regression
- Ridge Classifier
- SGD Classifier

**Métriques d'évaluation:**
- Accuracy: (1/n) × Σ 𝟙[ŷᵢ = yᵢ]
- Precision, Recall, F1-Score
- Confusion Matrix

## Structure du Projet

```
Perf_Plan/
├── data/
│   ├── raw/                 # Données brutes CSV
│   ├── processed/           # Données preprocessées
│   └── sample/              # Échantillons de données pour tests
├── src/
│   ├── __init__.py
│   ├── data_loader.py       # Chargement des données
│   ├── preprocessing.py     # Nettoyage et transformation
│   ├── features.py          # Feature engineering
│   ├── models/
│   │   ├── __init__.py
│   │   ├── regression.py    # Modèles de régression
│   │   └── classification.py # Modèles de classification
│   ├── training.py          # Pipeline d'entraînement
│   ├── evaluation.py        # Métriques et évaluation
│   └── visualization.py     # Graphiques et rapports
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_results_analysis.ipynb
├── models/                  # Modèles entraînés sauvegardés
├── results/                 # Résultats et visualisations
├── tests/                   # Tests unitaires
├── requirements.txt
├── setup.py
└── main.py                  # Script principal
```

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### 1. Préparation des données

Placez vos fichiers CSV dans le dossier `data/raw/`. Format attendu:

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
APP1,2022-01-01,1000,800,1200,50,0.95,100,950
APP2,2022-01-01,1500,1200,1800,75,0.90,150,1350
...
```

### 2. Entraînement des modèles

```bash
# Régression (prédire valeur exacte MIPS)
python main.py --mode regression --model linear

# Classification (prédire catégorie MIPS)
python main.py --mode classification --model logistic

# Tous les modèles linéaires
python main.py --mode all --baseline
```

### 3. Évaluation et Prédictions

```bash
# Évaluer un modèle
python main.py --evaluate --model ridge --model-path models/ridge_model.pkl

# Faire des prédictions
python main.py --predict --input data/new_data.csv --output predictions.csv
```

## Résultats

Les résultats incluent:
- Métriques de performance comparées aux baselines
- Visualisations des prédictions vs valeurs réelles
- Importance des features
- Rapports de classification (si applicable)

## Baseline Performance

Les modèles linéaires servent de baseline pour comparaison:
- Mean predictor (toujours prédire la moyenne)
- Median predictor
- Linear Regression simple

**Objectif:** Surpasser ces baselines avec des modèles linéaires optimisés et régularisés.

## Technologies

- Python 3.8+
- scikit-learn
- pandas
- numpy
- matplotlib/seaborn
- joblib

## Licence

MIT License

## Auteurs

Projet de prédiction de performance z/OS
