# 🔄 Transform Quickstart - 5 Minutes

Transformez vos données z/OS pivot en format ML en 5 minutes top chrono !

---

## ⚡ Copy-Paste Colab (Méthode Rapide)

### 1-Click Transformation

**Ouvrez ce notebook:**
```
https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/05_transform_pivot_data.ipynb
```

**Exécutez tout** (`Runtime` → `Run all`) et suivez les prompts !

---

## 🎯 3-Commandes Express

```python
# Setup
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan

# Upload + Transform
from google.colab import files
uploaded = files.upload()
!python src/transform_pivot.py {list(uploaded.keys())[0]}

# Le fichier transformé est créé automatiquement !
```

---

## 📊 Format Requis

**Votre fichier pivot doit ressembler à:**

```
code_application | code_indicateur | 2022-01-01 | 2022-02-01 | 2022-03-01
APP-001         | M24H           | 1234,5     | 1456,8     | 1389,2
APP-001         | MDIU           | 0,2717     | 0,196      | 0,2145
APP-001         | MPTE           | 0,3014     | 0,3047     | 0,2876
APP-001         | TXDIU          | 50,2       | 52,1       | 48,9
APP-001         | EFF            | 95,5       | 94,2       | 96,1
APP-001         | TVDIU          | 100,0      | 105,0      | 98,0
APP-002         | M24H           | 2345,6     | 2567,9     | 2456,3
...
```

**Caractéristiques:**
- ✅ Colonne 1: Code application
- ✅ Colonne 2: Code indicateur (M24H, MDIU, MPTE, TXDIU, EFF, TVDIU)
- ✅ Colonnes 3+: Dates (n'importe quel format)
- ✅ Valeurs: Virgules ou points décimaux (auto-converti)
- ✅ Format: CSV, TSV, ou Excel

---

## 🚀 Workflow Complet (8 Minutes Total)

### Étape 1: Transformation (2 min)

```python
# Colab
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan

# Upload votre pivot
from google.colab import files
uploaded = files.upload()
pivot_file = list(uploaded.keys())[0]

# Transform
!python src/transform_pivot.py {pivot_file}
transformed_file = f"{pivot_file.rsplit('.', 1)[0]}_transformed.csv"
print(f"✅ Fichier transformé: {transformed_file}")
```

### Étape 2: Validation (1 min)

```python
# Vérifier le résultat
import pandas as pd
df = pd.read_csv(transformed_file)

print(f"Shape: {df.shape}")
print(f"Colonnes: {list(df.columns)}")
print(f"Applications: {df['application'].nunique()}")
print(f"\nPreview:")
display(df.head())
```

### Étape 3: Entraînement (5 min)

```python
# Entraîner directement
!python main.py train \
    --data-path {transformed_file} \
    --mode both \
    --feature-engineering

# Télécharger les modèles
from google.colab import files
files.download('models/best_model.pkl')
files.download('models/preprocessor.pkl')
```

---

## 🔄 Qu'est-ce qui est Transformé?

### Avant (Pivot):
```
APP | INDICATOR | 2022-01 | 2022-02 | 2022-03
A   | M24H      | 1234,5  | 1456,8  | 1389,2
A   | MDIU      | 0,27    | 0,20    | 0,21
```

### Après (Long):
```
application | timestamp  | M24H   | MDIU | MPTE | ... | MIPS_consumption
A           | 2022-01-01 | 1234.5 | 0.27 | 0.30 | ... | 1234.5
A           | 2022-02-01 | 1456.8 | 0.20 | 0.30 | ... | 1456.8
A           | 2022-03-01 | 1389.2 | 0.21 | 0.29 | ... | 1389.2
```

### Transformations Automatiques:

1. ✅ **Dépivotage dates**: Colonnes → Lignes
2. ✅ **Pivotage indicateurs**: Lignes → Colonnes
3. ✅ **Décimales**: Virgule → Point
4. ✅ **Target**: Création `MIPS_consumption`
5. ✅ **Nettoyage**: Suppression valeurs manquantes
6. ✅ **Validation**: Vérification format ML

---

## ✅ Checklist Express

Avant de transformer:
- [ ] Format CSV, TSV, ou Excel ✓
- [ ] Colonne 1 = Applications ✓
- [ ] Colonne 2 = Indicateurs ✓
- [ ] Colonnes 3+ = Dates ✓
- [ ] Indicateurs requis présents: M24H, MDIU, MPTE, TXDIU, EFF, TVDIU ✓

Après transformation:
- [ ] 9 colonnes minimum ✓
- [ ] Décimales au format point ✓
- [ ] Colonne MIPS_consumption créée ✓
- [ ] Pas de valeurs manquantes dans target ✓

---

## 🛠️ Dépannage Rapide

### "Could not load file"
→ Vérifiez l'encodage (UTF-8) ou essayez Excel format

### "Missing indicator: [NAME]"
→ Vérifiez que M24H, MDIU, MPTE, TXDIU, EFF, TVDIU sont présents

### "Could not parse dates"
→ Vérifiez que les colonnes 3+ contiennent des dates valides

### "Too few records"
→ Besoin minimum 500 records (applications × dates)

---

## 💡 Pro Tips

1. **Testez avec échantillon d'abord**
   - Prenez 2-3 applications et 3-6 mois de données
   - Vérifiez que la transformation fonctionne
   - Puis utilisez le dataset complet

2. **Vérifiez les indicateurs**
   - Ouvrez votre fichier dans Excel/Sheets
   - Vérifiez que tous les indicateurs requis sont présents
   - Vérifiez l'orthographe exacte

3. **Encodage UTF-8**
   - Si erreurs d'encodage: Ouvrez dans Excel
   - "Save As" → CSV UTF-8
   - Réessayez

4. **Gardez l'original**
   - La transformation ne modifie pas votre fichier original
   - Crée un nouveau fichier avec suffixe `_transformed.csv`

---

## 📞 Besoin d'Aide?

| Question | Ressource |
|----------|-----------|
| Guide détaillé | [TRANSFORM_GUIDE.md](TRANSFORM_GUIDE.md) |
| Notebook interactif | [05_transform_pivot_data.ipynb](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/05_transform_pivot_data.ipynb) |
| Format requis | Section "Format Requis" ci-dessus |
| Après transformation | [UPLOAD_QUICKSTART.md](UPLOAD_QUICKSTART.md) |

---

## 🎯 One-Liner Ultimate

**Tout faire d'un coup (Transform + Train):**

```python
# Colab - Copiez-collez
!git clone https://github.com/chelvy/Perf_Plan.git && cd Perf_Plan && \
from google.colab import files; uploaded = files.upload(); \
!python src/transform_pivot.py {list(uploaded.keys())[0]} && \
!python main.py train --data-path *_transformed.csv --mode both --feature-engineering
```

---

## ⏱️ Temps Total Estimé

- **Setup Colab**: 30 sec
- **Upload fichier**: 30 sec
- **Transformation**: 30 sec - 2 min (selon taille)
- **Validation**: 30 sec
- **Entraînement**: 5-10 min (selon taille)

**Total: ~8-15 minutes de bout en bout**

---

## 🔗 Prochaines Étapes

Après transformation:

1. ✅ Fichier transformé créé
2. ➡️ Option A: [Upload dans Colab](UPLOAD_QUICKSTART.md)
3. ➡️ Option B: [Entraîner directement](COLAB_QUICKSTART.md)
4. ➡️ Option C: [Pipeline complet](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)

---

## 📋 Formats Supportés Résumé

| Aspect | Supporté |
|--------|----------|
| **Fichiers** | CSV, TSV, Excel (.xlsx, .xls) |
| **Séparateurs** | `,` `;` `\|` tab (auto-détecté) |
| **Encodages** | UTF-8, Latin-1, Windows-1252 |
| **Décimales** | Point ou virgule (auto-converti) |
| **Dates** | Tous formats courants |

---

**Vos données pivot sont maintenant prêtes pour le ML ! 🚀**

Pour plus de détails: [TRANSFORM_GUIDE.md](TRANSFORM_GUIDE.md)
