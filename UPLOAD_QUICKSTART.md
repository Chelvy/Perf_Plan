# 📤 Upload Quickstart - 3 Minutes

Uploadez vos données z/OS en 3 minutes top chrono !

---

## ⚡ Super Rapide (Copy-Paste)

### Méthode 1: Dans le Notebook Principal

1. **Ouvrez:** https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb

2. **Trouvez Step 2 → Option B**

3. **Changez cette ligne:**
   ```python
   USE_UPLOADED_DATA = False  # Change to True
   ```
   en:
   ```python
   USE_UPLOADED_DATA = True   # ✅ Activé
   ```

4. **Exécutez la cellule** - Un bouton "Choose Files" apparaît

5. **Cliquez** et sélectionnez votre CSV

6. **Continuez** le notebook normalement

**C'est tout ! ✨**

---

### Méthode 2: Notebook Dédié (Plus de Contrôle)

1. **Ouvrez:** https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb

2. **Exécutez toutes les cellules** (`Runtime` → `Run all`)

3. Le notebook va:
   - ✅ Télécharger un template CSV
   - ✅ Vous demander d'uploader votre fichier
   - ✅ Valider automatiquement vos données
   - ✅ Corriger les problèmes courants
   - ✅ Préparer tout pour l'entraînement

4. **Retournez** au notebook principal avec votre `DATA_PATH`

---

## 📋 Format Requis (30 secondes)

Votre CSV doit avoir ces 9 colonnes:

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
APP_001,2024-01-01,1000,800,1200,50,0.95,100,950
```

**Colonnes:**
- `application` - Nom app
- `timestamp` - Date (YYYY-MM-DD)
- `M24H` - MIPS 24h
- `MDIU` - MIPS jour
- `MPTE` - MIPS pointe
- `TXDIU` - Taux transactions
- `EFF` - Efficacité (0-1)
- `TVDIU` - Temps valeur
- `MIPS_consumption` - **Cible** (MIPS réels)

---

## 🎯 Template Express

Copiez-collez dans Colab:

```python
import pandas as pd
from google.colab import files

# Créer template
template = pd.DataFrame({
    'application': ['APP_001', 'APP_002'],
    'timestamp': ['2024-01-01', '2024-01-02'],
    'M24H': [1000, 1500],
    'MDIU': [800, 1200],
    'MPTE': [1200, 1800],
    'TXDIU': [50, 75],
    'EFF': [0.95, 0.90],
    'TVDIU': [100, 150],
    'MIPS_consumption': [950, 1350]
})

# Télécharger
template.to_csv('template.csv', index=False)
files.download('template.csv')
```

**Remplissez avec vos données et re-uploadez !**

---

## ✅ Checklist Express

Avant d'uploader:

- [ ] Format CSV ✓
- [ ] 9 colonnes requises ✓
- [ ] Noms de colonnes exacts ✓
- [ ] Nombres dans les colonnes numériques ✓
- [ ] Minimum 500 lignes (1000+ recommandé) ✓

**Si tout est ✓, uploadez !**

---

## 🔧 Problème? Fix Rapide

### "Missing columns"
→ Vérifiez les noms exactement (sensible à la casse)

### "Wrong data type"
→ Colonnes numériques = nombres uniquement

### "Encoding error"
→ Sauvegardez en UTF-8 dans Excel/Sheets

### "Too small"
→ Minimum 500 records, idéalement 1000+

---

## 🚀 Upload + Train en Une Commande

Tout faire d'un coup:

```python
# Upload
from google.colab import files
uploaded = files.upload()
DATA_PATH = list(uploaded.keys())[0]

# Train immédiatement
!python run_colab.py --mode both
```

---

## 💾 Alternative: Google Drive

Si votre fichier est déjà dans Drive:

```python
from google.colab import drive
drive.mount('/content/drive')

DATA_PATH = '/content/drive/MyDrive/votre_dossier/mips_data.csv'
print(f"✅ Using: {DATA_PATH}")
```

---

## 📞 Aide Rapide

| Besoin | Solution |
|--------|----------|
| Template | Exécuter code "Template Express" ci-dessus |
| Validation | Utiliser notebook 04_upload_your_data.ipynb |
| Format exact | Voir section "Format Requis" |
| Erreur upload | Vérifier UTF-8, CSV, colonnes |
| Guide complet | Lire [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md) |

---

## ⏱️ Temps Total: ~3 Minutes

1. **Préparer CSV:** 1 min (si déjà au bon format)
2. **Upload:** 30 sec
3. **Validation:** 30 sec
4. **Lancer training:** 1 min setup

**Puis attendre ~8-12 min pour l'entraînement**

---

## 🎯 One-Liner Ultimate

Copiez ceci dans Colab pour TOUT faire:

```python
# Setup
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan && pip install -q -r requirements.txt

# Upload
from google.colab import files
uploaded = files.upload()

# Train
import os
os.chdir('Perf_Plan')
!python main.py train --data-path ../{list(uploaded.keys())[0]} --mode both --feature-engineering
```

---

**Voilà ! Vos données z/OS sont maintenant dans le système ! 🚀**

Pour plus de détails: [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md)
