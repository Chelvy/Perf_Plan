# 🔄 Transform Pivot Data - Complete Guide

Guide pour transformer vos données z/OS du format pivot au format long requis pour l'entraînement ML.

---

## 🎯 Problème Résolu

**Votre format actuel (Pivot):**
```
code_application | code_indicateur | 2022-04-01 | 2022-05-01 | 2022-06-01 | ...
DEV-CICS         | M24H           | 1234,5     | 1456,8     | 1389,2     | ...
DEV-CICS         | MDIU           | 0,2717     | 0,196      | 0,2145     | ...
DEV-CICS         | MPTE           | 0,3014     | 0,3047     | 0,2876     | ...
PROD-DB2         | M24H           | 2345,6     | 2567,9     | 2456,3     | ...
```

**Format requis (Long):**
```
application | timestamp  | M24H   | MDIU  | MPTE  | TXDIU | EFF  | TVDIU | MIPS_consumption
DEV-CICS    | 2022-04-01 | 1234.5 | 0.27  | 0.30  | 50.0  | 0.95 | 100.0 | 1234.5
DEV-CICS    | 2022-05-01 | 1456.8 | 0.20  | 0.30  | 52.0  | 0.94 | 105.0 | 1456.8
PROD-DB2    | 2022-04-01 | 2345.6 | 0.35  | 0.42  | 75.0  | 0.92 | 150.0 | 2345.6
```

---

## ⚡ Méthode 1: Google Colab (Recommandé)

### Option A: Notebook Interactif

1. **Ouvrez le notebook de transformation:**
   ```
   https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/05_transform_pivot_data.ipynb
   ```

2. **Exécutez Step 1**: Setup automatique

3. **Exécutez Step 2**: Upload votre fichier pivot
   - Formats acceptés: CSV, TSV, Excel (.xlsx, .xls)
   - Séparateurs décimaux: virgule ou point (auto-détecté)
   - Taille recommandée: Minimum 500 records

4. **Exécutez Step 3**: Transformation automatique
   - Conversion décimales (virgule → point)
   - Dépivotage des dates
   - Pivotage des indicateurs
   - Création de MIPS_consumption

5. **Exécutez Step 4**: Validation
   - Vérification du format
   - Preview des données
   - Statistiques

6. **Exécutez Step 5**: Téléchargement
   - Fichier transformé prêt pour ML
   - Nom: `{original}_transformed.csv`

7. **Continuez avec l'entraînement:**
   - Ouvrez le notebook principal
   - Uploadez le fichier transformé
   - Lancez l'entraînement

**Temps total: ~5 minutes**

### Option B: Script Automatisé

```python
# Dans Colab
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan

# Upload votre fichier pivot
from google.colab import files
uploaded = files.upload()
input_file = list(uploaded.keys())[0]

# Transformer
!python src/transform_pivot.py {input_file}

# Le fichier transformé est créé automatiquement
# Utilisez-le pour l'entraînement
```

---

## 💻 Méthode 2: Localement (Python)

### Installation

```bash
git clone https://github.com/chelvy/Perf_Plan.git
cd Perf_Plan
pip install -r requirements.txt
```

### Usage CLI

```bash
# Transformer un fichier
python src/transform_pivot.py votre_fichier_pivot.csv

# Spécifier le fichier de sortie
python src/transform_pivot.py input.xlsx output_transformed.csv

# Le fichier transformé est créé dans le même dossier
```

### Usage Programmatique

```python
from src.transform_pivot import PivotTransformer

# Créer le transformer
transformer = PivotTransformer()

# Transformer un fichier
df_transformed, output_path = transformer.transform_file(
    input_path='zos_pivot_data.csv',
    output_path='zos_long_format.csv'  # Optionnel
)

print(f"Transformation complete: {output_path}")
print(f"Shape: {df_transformed.shape}")
```

---

## 📋 Format d'Entrée Détaillé

### Structure Attendue

**Colonnes:**
1. **Colonne 1**: Code application (ex: `code_application`, `application`, `app_id`)
2. **Colonne 2**: Code indicateur (ex: `code_indicateur`, `indicator`, `metric`)
3. **Colonnes 3+**: Dates (format: YYYY-MM-DD, DD/MM/YYYY, ou autre)

**Indicateurs Requis:**
- `M24H` - MIPS 24 heures
- `MDIU` - MIPS Diurne (jour)
- `MPTE` - MIPS Pointe (peak)
- `TXDIU` - Taux transactions DIU
- `EFF` - Efficacité
- `TVDIU` - Temps valeur DIU

**Indicateurs Optionnels:**
- Tout autre indicateur sera inclus comme colonne supplémentaire

### Formats Acceptés

**Fichiers:**
- CSV (`,` ou `;` ou `|` ou tab)
- TSV (tab-separated)
- Excel (`.xlsx`, `.xls`)

**Encodages:**
- UTF-8 (recommandé)
- Latin-1 / ISO-8859-1
- Windows-1252

**Décimales:**
- Virgule européenne: `1234,56` ✅ (auto-converti)
- Point anglo-saxon: `1234.56` ✅

### Exemple Complet

```csv
code_application,code_indicateur,2022-01-01,2022-02-01,2022-03-01
DEV-CICS,M24H,"1234,5","1456,8","1389,2"
DEV-CICS,MDIU,"0,2717","0,196","0,2145"
DEV-CICS,MPTE,"0,3014","0,3047","0,2876"
DEV-CICS,TXDIU,"50,2","52,1","48,9"
DEV-CICS,EFF,"95,5","94,2","96,1"
DEV-CICS,TVDIU,"100,0","105,0","98,0"
PROD-DB2,M24H,"2345,6","2567,9","2456,3"
PROD-DB2,MDIU,"0,35","0,38","0,36"
PROD-DB2,MPTE,"0,42","0,45","0,43"
PROD-DB2,TXDIU,"75,0","78,0","76,0"
PROD-DB2,EFF,"92,0","91,5","93,0"
PROD-DB2,TVDIU,"150,0","155,0","152,0"
```

---

## 🔄 Processus de Transformation

### Étapes Automatiques

1. **Chargement**
   - Détection automatique du format
   - Détection du séparateur
   - Détection de l'encodage

2. **Correction des Décimales**
   - Remplacement virgule → point
   - Conversion en float

3. **Dépivotage des Dates**
   - Dates en colonnes → Dates en lignes
   - Création colonne `timestamp`
   - Préservation app + indicateur

4. **Pivotage des Indicateurs**
   - Indicateurs en lignes → Indicateurs en colonnes
   - Une colonne par indicateur (M24H, MDIU, etc.)

5. **Création de la Cible**
   - Utilise M24H si disponible
   - Sinon moyenne(MDIU, MPTE)
   - Création colonne `MIPS_consumption`

6. **Colonnes Manquantes**
   - Ajout des indicateurs manquants (remplis à 0)

7. **Nettoyage**
   - Suppression lignes vides
   - Suppression lignes tout-à-zéro
   - Conversion timestamp en datetime

8. **Réorganisation**
   - Ordre standard des colonnes
   - Format prêt pour ML

---

## ✅ Validation du Résultat

### Checklist Post-Transformation

Après transformation, vérifiez:

- [ ] Fichier CSV créé avec suffixe `_transformed.csv`
- [ ] 9 colonnes présentes (ou plus si indicateurs extra)
- [ ] Colonnes: `application`, `timestamp`, `M24H`, `MDIU`, `MPTE`, `TXDIU`, `EFF`, `TVDIU`, `MIPS_consumption`
- [ ] Décimales au format point (`.`)
- [ ] Pas de valeurs manquantes dans `MIPS_consumption`
- [ ] Nombre de lignes = nb_applications × nb_dates
- [ ] Dates parsées correctement

### Commandes de Vérification

```python
import pandas as pd

# Charger le fichier transformé
df = pd.read_csv('votre_fichier_transformed.csv')

# Vérifications
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Applications: {df['application'].nunique()}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"MIPS range: {df['MIPS_consumption'].min():.2f} - {df['MIPS_consumption'].max():.2f}")
print(f"Missing values:\n{df.isnull().sum()}")
```

---

## 🛠️ Dépannage

### "Could not load file"

**Causes:**
- Format non reconnu
- Encodage incompatible
- Fichier corrompu

**Solutions:**
- Ouvrir dans Excel et "Save As" → CSV UTF-8
- Vérifier que le fichier n'est pas vide
- Essayer avec Excel (.xlsx) au lieu de CSV

### "Column not found: [indicateur]"

**Causes:**
- Nom d'indicateur non standard
- Faute de frappe
- Indicateurs manquants

**Solutions:**
- Vérifier les noms exacts dans votre fichier
- Les noms doivent être exactement: M24H, MDIU, MPTE, TXDIU, EFF, TVDIU
- Utiliser la casse correcte (majuscules)

### "Could not parse timestamp"

**Causes:**
- Format de date non reconnu
- Dates en format texte bizarre

**Solutions:**
- Utiliser format standard: YYYY-MM-DD ou DD/MM/YYYY
- Vérifier qu'il n'y a pas de texte dans les en-têtes de dates
- Ouvrir le CSV dans un éditeur de texte pour vérifier

### "Data type error in [column]"

**Causes:**
- Valeurs non numériques dans les colonnes d'indicateurs
- Caractères spéciaux

**Solutions:**
- Vérifier qu'il n'y a que des nombres dans les cellules
- Remplacer les virgules par des points si nécessaire
- Supprimer les espaces, symboles de devise, etc.

### "Too few records after transformation"

**Causes:**
- Beaucoup de lignes avec des valeurs manquantes
- Lignes tout-à-zéro supprimées

**Solutions:**
- Vérifier les données sources
- Remplir les valeurs manquantes avant transformation
- Ajuster les seuils de nettoyage si nécessaire

---

## 📊 Workflow Complet

### De A à Z

```
1. DONNÉES BRUTES (Pivot)
   ↓
2. TRANSFORMATION (notebooks/05_transform_pivot_data.ipynb)
   ↓
3. VALIDATION (vérifier format et statistiques)
   ↓
4. UPLOAD (notebooks/04_upload_your_data.ipynb)
   ↓
5. ENTRAÎNEMENT (notebooks/03_colab_full_pipeline.ipynb)
   ↓
6. MODÈLES ENTRAÎNÉS (télécharger et déployer)
```

### Commandes Complètes (Colab)

```python
# 1. Setup
!git clone https://github.com/chelvy/Perf_Plan.git
%cd Perf_Plan
!pip install -q -r requirements.txt

# 2. Upload données pivot
from google.colab import files
uploaded = files.upload()
pivot_file = list(uploaded.keys())[0]

# 3. Transformer
!python src/transform_pivot.py {pivot_file}
transformed_file = pivot_file.replace('.csv', '_transformed.csv')

# 4. Valider
import pandas as pd
df = pd.read_csv(transformed_file)
print(f"✅ Transformed: {df.shape}")
display(df.head())

# 5. Entraîner immédiatement
!python main.py train --data-path {transformed_file} --mode both --feature-engineering

# 6. Télécharger les modèles
files.download('models/best_model.pkl')
files.download('models/preprocessor.pkl')
```

---

## 💡 Bonnes Pratiques

### Avant Transformation

1. **Vérifier les données sources**
   - Ouvrir dans Excel/Sheets
   - Vérifier qu'il n'y a pas de lignes vides
   - Vérifier les en-têtes de colonnes

2. **Sauvegarder une copie**
   - Garder le fichier original
   - La transformation ne modifie pas l'original

3. **Préparer les métadonnées**
   - Noter le nombre d'applications
   - Noter la période couverte
   - Noter les unités des indicateurs

### Pendant Transformation

1. **Examiner les logs**
   - Vérifier les messages d'information
   - Noter les warnings
   - Résoudre les erreurs

2. **Valider les résultats intermédiaires**
   - Vérifier après dépivotage
   - Vérifier après conversion décimales
   - Vérifier la création du target

### Après Transformation

1. **Valider le résultat**
   - Utiliser le script de validation
   - Comparer quelques valeurs manuellement
   - Vérifier les statistiques

2. **Documenter**
   - Noter les transformations appliquées
   - Noter les paramètres utilisés
   - Garder un log des opérations

---

## 🎯 Résumé Ultra-Rapide

**3 commandes pour tout faire:**

```python
# Dans Colab
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan

# Upload + Transform
from google.colab import files; uploaded = files.upload(); !python src/transform_pivot.py {list(uploaded.keys())[0]}

# Train
!python main.py train --data-path *_transformed.csv --mode both
```

---

## 📞 Support

### Ressources

- **Template CSV**: Téléchargez depuis le notebook 05
- **Exemple complet**: Voir ce guide section "Format d'Entrée"
- **Validation automatique**: Notebook 05 Step 4

### Checklist de Debug

Si ça ne marche pas:
1. ☐ Vérifier que le fichier a au moins 3 colonnes
2. ☐ Vérifier que la colonne 2 contient les indicateurs requis
3. ☐ Vérifier que les colonnes 3+ sont des dates
4. ☐ Vérifier l'encodage (UTF-8 recommandé)
5. ☐ Essayer avec un petit échantillon d'abord

---

## ✅ Transformation Réussie!

Une fois transformé, vos données sont prêtes pour:
- ✅ Upload direct dans Colab
- ✅ Entraînement avec `main.py train`
- ✅ Utilisation dans le pipeline complet
- ✅ Feature engineering automatique
- ✅ Évaluation comparative de modèles

**Prochaine étape:** [UPLOAD_QUICKSTART.md](UPLOAD_QUICKSTART.md)

---

**🚀 Vos données z/OS pivot sont maintenant exploitables pour le ML!**
