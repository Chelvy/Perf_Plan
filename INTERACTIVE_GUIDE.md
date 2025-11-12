# 🎯 Interactive Notebook Guide

**Step-by-Step Guide for the All-in-One Interactive Notebook**

---

## 🚀 Quick Start

Open notebook: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/01_complete_pipeline.ipynb)

**No coding required! Just click and select your options.**

---

## 📋 How It Works

### **Section 1: Setup** (Auto-runs)
- Click **Run** → Code downloads automatically
- Takes ~30 seconds
- ✅ When done: "✅ All modules imported successfully!"

---

### **Section 2: 🔧 Configuration Panel** ⭐ **INTERACTIVE**

**Click the ⚙️ icon** to open the form panel. You'll see:

#### **📊 Data Source** (Dropdown menu)
Click to select ONE option:
- 🎲 **Sample Data (Test)** ← Default, for testing
- 🔄 **Upload Pivot Data (Transform)** ← Dates in columns
- 📤 **Upload Long-Format Data** ← Standard CSV
- 📁 **Manual Path** ← Advanced users

#### **🎯 Training Configuration**
Interactive sliders and toggles:
- **Test Size**: 0.1 to 0.4 (drag slider)
- **Random State**: Enter number (for reproducibility)
- **Time Based Split**: Toggle On/Off
- **Scaler Type**: Dropdown (standard/minmax/robust)
- **Handle Outliers**: Toggle On/Off
- **Outlier Method**: Dropdown (clip/remove)
- **Feature Engineering**: Toggle On/Off ← Recommended: On
- **N Categories**: 2-5 (drag slider)
- **Category Method**: Dropdown (quantile/equal)

#### **📊 Sample Data Settings** (if Sample Data selected)
- **Sample Size**: 500-5000 records (drag slider)
- **N Applications**: 20-200 apps (drag slider)

#### **💾 Output**
- **Save Models**: Toggle On/Off

**Click ▶️ Run** → Configuration saved!

You'll see:
```
⚙️  CONFIGURATION SUMMARY
📊 Data Source: Sample Data (Test)
🎯 Training Settings: ...
✅ Configuration ready! Continue to Section 3
```

---

### **Section 3: 📤 Data Preparation** ⭐ **AUTO-MAGIC**

**Just click ▶️ Run** - that's it!

The notebook automatically:
- Reads your Section 2 selection
- Performs the right action:
  - **Sample Data**: Creates synthetic data ✨
  - **Pivot Upload**: Shows upload button + transforms data 🔄
  - **Long-Format Upload**: Shows template download + upload button 📤
  - **Manual Path**: Instructions to set path 📁

**For uploads:**
1. Click "Choose Files" button (appears automatically)
2. Select your file
3. Upload completes automatically
4. Preview shows instantly

When done, you'll see:
```
✅ DATA READY
Data file: data/sample/sample_mips_data.csv
Records: 2,000
Columns: ['application', 'timestamp', 'M24H', ...]
✅ Configuration updated - ready for training!
```

---

### **Section 4: 📊 Data Exploration** ⭐ **OPTIONAL**

**Click the ⚙️ icon** to choose visualizations:

#### **Toggle Options:**
- ☑️ **Show Summary** - Data statistics and preview
- ☑️ **Show Distribution** - Histograms and box plots
- ☑️ **Show Correlation** - Correlation heatmap

**Click ▶️ Run** → Selected visualizations appear!

Turn off toggles to skip and speed up execution.

---

### **Section 5: 🚀 Training** ⭐ **ONE-CLICK**

#### **Training Options Form:**
**Click the ⚙️ icon** and select mode:

- 🔵🟢 **Both (Regression + Classification)** ← Recommended
- 🔵 **Regression Only** - Predict exact MIPS values
- 🟢 **Classification Only** - Predict LOW/MEDIUM/HIGH

#### **Execute Training:**
**Click ▶️ Run** on the second cell

Training starts automatically:
```
🎯 STARTING TRAINING PIPELINE
Data: data/sample/sample_mips_data.csv
Mode: Both (Regression + Classification)
Feature Engineering: True

Training in progress...
[Progress bars and status updates]

✅ TRAINING COMPLETED!
Models trained: ['regression', 'classification']
Models saved to: models/
```

**Takes 5-10 minutes** (sit back and relax ☕)

---

### **Sections 6-7: 📊 Results** (Auto-display)

Just **click ▶️ Run** on each cell - results appear automatically:

**Section 6 - Regression:**
- Model comparison tables
- Best model performance
- Predictions vs Actual plots
- Residual analysis

**Section 7 - Classification:**
- Accuracy comparison tables
- Best model performance
- Confusion matrices
- F1 scores

---

### **Section 8: 📋 Summary** (Auto-display)

**Click ▶️ Run** → See final summary:
```
📋 FINAL SUMMARY

🔵 REGRESSION RESULTS:
   Best Model: Ridge Regression
   Test RMSE: 125.43
   Test R²: 0.8756
   📈 Improvement over baseline: 45.2%

🟢 CLASSIFICATION RESULTS:
   Best Model: Logistic Regression
   Test Accuracy: 0.8923
   Test F1 (macro): 0.8745
   📈 Improvement over baseline: 32.1%
```

---

### **Section 9: 💾 Download** (Auto-download)

**Click ▶️ Run** → Automatic ZIP download!

Downloads file: `zos_mips_models_results.zip`

Contains:
- `models/` - All trained models (.pkl files)
- `results/` - Performance metrics and plots

---

### **Sections 10-11: Bonus** (Optional)

**Section 10** - Make predictions on new data (example)
**Section 11** - Production deployment guide

---

## 🎨 Visual Flow

```
┌─────────────────────────────────────┐
│ 1. SETUP                           │
│ ▶️ Run (auto-install)              │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 2. CONFIGURATION ⭐                │
│ 🔧 Open Form Panel                 │
│ ✓ Select Data Source (dropdown)    │
│ ✓ Adjust Sliders                   │
│ ✓ Toggle Options                   │
│ ▶️ Run                              │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 3. DATA PREP ⭐                    │
│ ▶️ Run (auto-magic!)               │
│ • Sample → Creates data             │
│ • Upload → Click "Choose Files"     │
│ ✅ Data Ready!                      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 4. EXPLORATION ⭐ (optional)       │
│ 🔧 Toggle visualizations           │
│ ▶️ Run                              │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 5. TRAINING ⭐                     │
│ 🔧 Select Mode (dropdown)          │
│ ▶️ Run (wait 5-10 min ☕)          │
│ ✅ Training Complete!               │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 6-8. RESULTS                       │
│ ▶️ Run each section                │
│ 📊 See performance                  │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 9. DOWNLOAD                        │
│ ▶️ Run → Auto-download ZIP         │
│ 💾 Get your trained models!         │
└─────────────────────────────────────┘
```

---

## 💡 Pro Tips

### **For Testing:**
1. Section 2: Select "Sample Data (Test)"
2. Keep all defaults
3. Click ▶️ Run on each section
4. Total time: ~8 minutes

### **For Your Data (Pivot Format):**
1. Section 2: Select "Upload Pivot Data (Transform)"
2. Section 3: Upload when prompted
3. Continue normally

### **For Your Data (Long Format):**
1. Section 2: Select "Upload Long-Format Data"
2. Section 3: Download template first (optional)
3. Upload your data when prompted

### **Speed Optimization:**
- Section 2: Turn OFF "Feature Engineering" (faster training)
- Section 2: Reduce "Sample Size" to 1000
- Section 4: Toggle OFF visualizations you don't need

### **Maximum Accuracy:**
- Section 2: Keep "Feature Engineering" ON
- Section 2: Set "Test Size" to 0.2 (more training data)
- Section 5: Select "Both" mode (compare all models)

---

## 🎯 Common Workflows

### **Workflow 1: Quick Test (8 minutes)**
```
Section 1: ▶️ Run
Section 2: ⚙️ Select "Sample Data" → ▶️ Run
Section 3: ▶️ Run
Section 4: Skip
Section 5: ⚙️ Select "Both" → ▶️ Run (wait)
Section 6-8: ▶️ Run each
Section 9: ▶️ Run → Download
```

### **Workflow 2: Your Pivot Data (12 minutes)**
```
Section 1: ▶️ Run
Section 2: ⚙️ Select "Upload Pivot Data" → ▶️ Run
Section 3: ▶️ Run → Upload file when prompted
Section 4: ▶️ Run (check your data)
Section 5: ⚙️ Select "Both" → ▶️ Run (wait)
Section 6-8: ▶️ Run each
Section 9: ▶️ Run → Download
```

### **Workflow 3: Your Long-Format Data (12 minutes)**
```
Section 1: ▶️ Run
Section 2: ⚙️ Select "Upload Long-Format Data" → ▶️ Run
Section 3: ▶️ Run → Download template (optional) → Upload file
Section 4: ▶️ Run (check your data)
Section 5: ⚙️ Select "Both" → ▶️ Run (wait)
Section 6-8: ▶️ Run each
Section 9: ▶️ Run → Download
```

### **Workflow 4: Regression Only (6 minutes)**
```
Section 1: ▶️ Run
Section 2: ⚙️ Sample Data, Feature Eng OFF → ▶️ Run
Section 3: ▶️ Run
Section 4: Skip
Section 5: ⚙️ Select "Regression Only" → ▶️ Run (faster)
Section 6: ▶️ Run (regression results only)
Section 8: ▶️ Run (summary)
Section 9: ▶️ Run → Download
```

---

## 🆘 Troubleshooting

### "No configuration form appears"
- Look for the ⚙️ icon on the right side of the cell
- Click it to expand the form
- If not visible, the cell may not have `#@title` - check notebook version

### "Upload button doesn't appear"
- Make sure you selected "Upload..." option in Section 2
- Re-run Section 2 to confirm selection
- Check Section 3 output for prompts

### "Training stuck or slow"
- Normal! Training takes 5-10 minutes for 2000 records
- Reduce sample size in Section 2 for faster testing
- Turn off Feature Engineering for 2x speed boost
- Check Colab isn't disconnected (keep tab active)

### "Results don't appear"
- Make sure training (Section 5) completed successfully
- Look for "✅ TRAINING COMPLETED!" message
- Re-run result sections if needed

---

## 🎓 Learning Mode

Want to understand the code? Each cell has:
- **Top**: Interactive form (@title, @param)
- **Bottom**: Actual Python code (visible)

You can:
- ✅ Use forms (beginner-friendly)
- ✅ Edit code directly (advanced)
- ✅ Switch between both approaches

---

## ✨ What Makes This Special?

### **Before (Old Notebooks):**
```python
# You had to edit code:
USE_PIVOT_DATA = False  # ← Change this
USE_UPLOADED_DATA = False  # ← Or this?
USE_SAMPLE_DATA = True  # ← Maybe this?
```
Risk of errors, confusion! ❌

### **After (This Notebook):**
```
🔧 Configuration Panel
📊 Data Source: [Sample Data (Test) ▼]
                 ↑ Just click dropdown!
```
Easy, visual, error-free! ✅

---

## 📊 Full Feature List

✅ 4 Data source options (dropdown)
✅ 15+ Configuration sliders/toggles
✅ Automatic data routing
✅ 3 Visualization toggles
✅ 3 Training mode options
✅ One-click execution
✅ Real-time validation
✅ Progress indicators
✅ Auto-download results
✅ Zero code editing required
✅ Professional UI

---

**🚀 You're ready! Open the notebook and start training!**

[Open Interactive Notebook](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/01_complete_pipeline.ipynb)
