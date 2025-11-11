# 📤 Upload de Données z/OS - Résumé Complet

Toutes les méthodes pour uploader vos propres données z/OS dans Google Colab.

---

## 🎯 Vue d'Ensemble

Vous pouvez maintenant **uploader directement vos données z/OS historiques** dans Google Colab pour entraîner les modèles avec vos vraies données de performance.

### 3 Façons d'Uploader:

| Méthode | Temps | Difficulté | Quand l'utiliser |
|---------|-------|------------|------------------|
| **Notebook Principal** | 2 min | ⭐ Facile | Upload rapide, données prêtes |
| **Notebook Dédié** | 3-5 min | ⭐⭐ Moyen | Validation détaillée, débutant |
| **Google Drive** | 1 min | ⭐⭐⭐ Avancé | Fichiers volumineux, réutilisation |

---

## 📚 Documentation Disponible

### Guides Créés:

1. **[UPLOAD_QUICKSTART.md](UPLOAD_QUICKSTART.md)** ⚡
   - Version ultra-rapide (3 minutes)
   - Copy-paste ready
   - Pour les pressés

2. **[UPLOAD_GUIDE.md](UPLOAD_GUIDE.md)** 📖
   - Guide complet et détaillé
   - Troubleshooting exhaustif
   - Exemples et templates
   - Meilleures pratiques

3. **[notebooks/04_upload_your_data.ipynb](notebooks/04_upload_your_data.ipynb)** 📓
   - Notebook interactif dédié
   - Téléchargement de template
   - Validation automatique
   - Auto-fix des problèmes

### Notebooks Mis à Jour:

- **[notebooks/03_colab_full_pipeline.ipynb](notebooks/03_colab_full_pipeline.ipynb)**
  - Option B améliorée dans Step 2
  - Toggle `USE_UPLOADED_DATA`
  - Validation intégrée

---

## 🚀 Démarrage Rapide

### Option 1: Notebook Principal (Recommandé pour upload rapide)

```
1. Ouvrir: https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb

2. Aller à Step 2 → Option B

3. Changer: USE_UPLOADED_DATA = True

4. Exécuter la cellule → Bouton "Choose Files" apparaît

5. Uploader votre CSV

6. Continuer le notebook normalement
```

### Option 2: Notebook Dédié (Recommandé pour validation)

```
1. Ouvrir: https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb

2. Exécuter toutes les cellules (Runtime → Run all)

3. Le notebook va:
   ✅ Télécharger un template CSV
   ✅ Uploader votre fichier
   ✅ Valider les données
   ✅ Corriger les problèmes
   ✅ Préparer pour l'entraînement

4. Retourner au notebook principal avec DATA_PATH
```

---

## 📋 Format de Données Requis

### Colonnes Obligatoires (9):

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
APP_001,2024-01-01,1000,800,1200,50,0.95,100,950
APP_002,2024-01-01,1500,1200,1800,75,0.90,150,1350
```

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| application | string | Nom application | APP_001 |
| timestamp | date | Date/heure | 2024-01-01 |
| M24H | float | MIPS 24 heures | 1000.0 |
| MDIU | float | MIPS Diurne | 800.0 |
| MPTE | float | MIPS Pointe | 1200.0 |
| TXDIU | float | Taux transactions | 50.0 |
| EFF | float | Efficacité (0-1) | 0.95 |
| TVDIU | float | Temps valeur | 100.0 |
| MIPS_consumption | float | **TARGET** MIPS réels | 950.0 |

---

## ✨ Fonctionnalités d'Upload

### ✅ Ce Qui Est Inclus:

1. **Template CSV Téléchargeable**
   - Format exact prêt à remplir
   - Exemples de données
   - Téléchargement en un clic

2. **Validation Automatique**
   - Vérification des colonnes requises
   - Check des types de données
   - Détection des valeurs manquantes
   - Statistiques de qualité

3. **Auto-Fix des Problèmes**
   - Ajout timestamp si manquant
   - Conversion échelle EFF (0-100 → 0-1)
   - Suppression doublons
   - Nettoyage valeurs manquantes

4. **Feedback en Temps Réel**
   - Preview des données
   - Statistiques descriptives
   - Warnings et erreurs clairs
   - Recommandations d'amélioration

5. **Intégration Transparente**
   - Variable DATA_PATH automatique
   - Compatible avec pipeline existant
   - Pas de code supplémentaire

---

## 🎨 Télécharger Template CSV

### Méthode 1: Via Notebook

Exécuter dans Colab:

```python
import pandas as pd
from google.colab import files

template = pd.DataFrame({
    'application': ['APP_001', 'APP_002', 'APP_003'],
    'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'M24H': [1000, 1500, 900],
    'MDIU': [800, 1200, 750],
    'MPTE': [1200, 1800, 1100],
    'TXDIU': [50, 75, 45],
    'EFF': [0.95, 0.90, 0.92],
    'TVDIU': [100, 150, 90],
    'MIPS_consumption': [950, 1350, 850]
})

template.to_csv('mips_template.csv', index=False)
files.download('mips_template.csv')
print("✅ Template téléchargé!")
```

### Méthode 2: Créer Manuellement

1. Créez un fichier CSV
2. Ajoutez l'en-tête exact:
   ```
   application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
   ```
3. Ajoutez vos données
4. Sauvegardez en UTF-8

---

## 🔍 Validation des Données

Le système vérifie automatiquement:

### ✅ Checks Effectués:

- [x] Présence des 9 colonnes requises
- [x] Types de données corrects
- [x] Valeurs numériques dans colonnes numériques
- [x] Pas de target (MIPS_consumption) manquante
- [x] Format timestamp valide
- [x] Pas de doublons exacts
- [x] Range de valeurs raisonnable
- [x] Nombre d'applications
- [x] Période couverte
- [x] Distribution des données

### 📊 Statistiques Affichées:

- Nombre total d'enregistrements
- Nombre d'applications uniques
- Période couverte (date début → fin)
- Range des valeurs MIPS
- Valeurs manquantes par colonne
- Types de données détectés
- Preview des premières lignes
- Statistiques descriptives

---

## 🛠️ Auto-Fix des Problèmes

### Corrections Automatiques:

1. **Timestamp Manquant**
   - Crée des dates par défaut
   - Séquence journalière depuis 2022-01-01

2. **Échelle EFF Incorrecte**
   - Détecte si EFF > 1 (échelle 0-100)
   - Convertit automatiquement en 0-1

3. **Target Manquante**
   - Supprime les lignes sans MIPS_consumption
   - Affiche combien de lignes retirées

4. **Doublons**
   - Détecte les lignes identiques
   - Garde une seule occurrence

5. **Fichier Nettoyé**
   - Sauvegarde comme `cleaned_[filename].csv`
   - Met à jour DATA_PATH automatiquement

---

## 💡 Recommandations de Qualité

### Pour Meilleurs Résultats:

**Quantité:**
- ✅ Minimum: 500 records
- ✅ Recommandé: 1000+ records
- ✅ Idéal: 5000+ records

**Couverture Temporelle:**
- ✅ Minimum: 3 mois
- ✅ Recommandé: 1 an
- ✅ Idéal: 3 ans (comme spécifié)

**Diversité:**
- ✅ Multiple applications (10+)
- ✅ Différents types de charge
- ✅ Périodes variées (jour/nuit, semaine/weekend)

**Qualité:**
- ✅ < 10% valeurs manquantes
- ✅ Données cohérentes
- ✅ Outliers gérés
- ✅ Unités consistantes

---

## 🚨 Troubleshooting

### Erreur: "Missing columns"
**Cause:** Noms de colonnes incorrects
**Solution:** 
- Vérifier l'orthographe exacte
- Respecter la casse (majuscules/minuscules)
- Utiliser le template

### Erreur: "Wrong data type"
**Cause:** Texte dans colonne numérique
**Solution:**
- Vérifier les données
- Enlever caractères spéciaux
- S'assurer que les nombres sont des nombres

### Erreur: "Encoding error"
**Cause:** Mauvais encodage du fichier
**Solution:**
- Sauvegarder en UTF-8
- Excel: "Save As" → "CSV UTF-8"
- Google Sheets: Download → "CSV"

### Erreur: "File too large"
**Cause:** Fichier > limite Colab
**Solution:**
- Utiliser Google Drive (pas de limite)
- Ou diviser le fichier en parties

### Warning: "Small dataset"
**Cause:** < 1000 records
**Solution:**
- Collecter plus de données si possible
- Ou continuer (résultats moins optimaux)

---

## 📊 Exemples de Données

### Exemple 1: Données Quotidiennes

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
CICS_PROD,2024-01-01,1250,1000,1500,65,0.94,125,1180
DB2_MAIN,2024-01-01,2100,1800,2400,85,0.91,200,1910
WAS_APP1,2024-01-01,950,800,1100,45,0.96,95,912
CICS_PROD,2024-01-02,1300,1050,1550,68,0.93,130,1210
```

### Exemple 2: Données Horaires

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
CICS_PROD,2024-01-01 08:00,1250,1000,1500,65,0.94,125,1180
CICS_PROD,2024-01-01 09:00,1280,1020,1520,67,0.94,127,1200
CICS_PROD,2024-01-01 10:00,1300,1050,1550,68,0.93,130,1210
```

---

## 🎯 Workflow Complet

```
1. PRÉPARATION
   ↓
   - Exporter données z/OS
   - Formater en CSV
   - Vérifier colonnes

2. TEMPLATE (optionnel)
   ↓
   - Télécharger template
   - Remplir avec vos données
   - Sauvegarder

3. UPLOAD
   ↓
   - Ouvrir notebook Colab
   - Activer USE_UPLOADED_DATA=True
   - Uploader fichier CSV

4. VALIDATION
   ↓
   - Système vérifie automatiquement
   - Affiche résultats
   - Corrige problèmes

5. TRAINING
   ↓
   - Continuer notebook
   - Models s'entraînent avec vos données
   - Résultats sur vos données réelles

6. RÉSULTATS
   ↓
   - Modèles entraînés
   - Métriques de performance
   - Prédictions sur vos apps
```

---

## 📞 Support et Ressources

### Guides par Cas d'Usage:

| Situation | Lire |
|-----------|------|
| Première fois | [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md) |
| Upload rapide | [UPLOAD_QUICKSTART.md](UPLOAD_QUICKSTART.md) |
| Problème format | Notebook 04_upload_your_data.ipynb |
| Erreur upload | Section Troubleshooting ci-dessus |
| Gros fichier | Méthode Google Drive |
| Questions générales | [README.md](README.md) |

### URLs Importantes:

- **Notebook Upload:** https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb
- **Notebook Principal:** https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb
- **Repository:** https://github.com/chelvy/Perf_Plan

---

## ✅ Checklist Finale

Avant de commencer:

- [ ] Données z/OS exportées (3 ans recommandé)
- [ ] Format CSV prêt
- [ ] 9 colonnes requises présentes
- [ ] Colonnes nommées exactement comme spécifié
- [ ] Valeurs numériques dans colonnes numériques
- [ ] Minimum 500+ records (1000+ idéal)
- [ ] Encodage UTF-8
- [ ] Compte Google pour Colab

Après upload:

- [ ] Validation passée sans erreurs critiques
- [ ] DATA_PATH défini correctement
- [ ] Preview des données OK
- [ ] Statistiques raisonnables
- [ ] Prêt pour training

---

## 🎓 Conclusion

Vous pouvez maintenant:

✅ **Uploader vos données z/OS directement dans Colab**
✅ **Obtenir validation automatique**
✅ **Corriger problèmes en un clic**
✅ **Entraîner avec vos vraies données**
✅ **Obtenir prédictions sur vos apps**

**Temps total:** 3-5 minutes pour l'upload + 8-12 minutes pour le training

**Prêt à commencer ! 🚀**

---

*Dernière mise à jour: Intégration complète upload dataset*
