# 🚀 Google Colab Quick Start Guide

Run the z/OS MIPS Prediction system on Google Colab in minutes!

## 📋 Quick Links

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)

**Direct Link:** `https://colab.research.google.com/github/YOUR_USERNAME/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb`

Replace `YOUR_USERNAME` with your GitHub username.

---

## 🎯 What This Does

This Colab notebook provides a complete end-to-end pipeline for z/OS MIPS prediction:

- ✅ **Setup**: Automatically installs all dependencies
- ✅ **Data**: Creates sample data or upload your own
- ✅ **Training**: Trains 15+ regression and classification models
- ✅ **Evaluation**: Compares all models with comprehensive metrics
- ✅ **Visualization**: Creates performance charts and analysis
- ✅ **Download**: Exports trained models for production use

**Runtime:** ~5-10 minutes (free Colab tier)

---

## 🚀 Step-by-Step Instructions

### Method 1: Direct Link (Easiest)

1. **Open the notebook** by clicking the "Open in Colab" badge above
2. **Sign in** to your Google account if prompted
3. **Run all cells** by clicking:
   - `Runtime` → `Run all`
   - OR press `Ctrl+F9` (Windows/Linux) or `Cmd+F9` (Mac)
4. **Wait** for training to complete (~5-10 minutes)
5. **Download** your trained models at the end

### Method 2: Upload Notebook Manually

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click `File` → `Upload notebook`
3. Upload `notebooks/03_colab_full_pipeline.ipynb` from this repository
4. Run all cells

### Method 3: From GitHub

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click `File` → `Open notebook` → `GitHub` tab
3. Enter your GitHub URL or search for your repository
4. Select `03_colab_full_pipeline.ipynb`
5. Run all cells

---

## 📊 Using Your Own Data

The notebook provides three options for data:

### Option A: Sample Data (Default)
```python
# Creates synthetic z/OS MIPS data automatically
# Best for testing and learning the system
```

### Option B: Upload CSV File
```python
# Uncomment the upload section in Step 2
from google.colab import files
uploaded = files.upload()
DATA_PATH = list(uploaded.keys())[0]
```

**Your CSV should have these columns:**
- `application` - Application name/ID
- `timestamp` - Date/time (optional)
- `M24H` - MIPS 24 hours
- `MDIU` - MIPS Diurne (daytime)
- `MPTE` - MIPS Pointe (peak)
- `TXDIU` - Transaction rate DIU
- `EFF` - Efficiency metric
- `TVDIU` - Time value DIU
- `MIPS_consumption` - Target variable (actual MIPS)

### Option C: Google Drive
```python
# Uncomment the Google Drive section in Step 2
from google.colab import drive
drive.mount('/content/drive')
DATA_PATH = '/content/drive/MyDrive/your_folder/mips_data.csv'
```

---

## 🎨 What You'll Get

### 1. Trained Models
- **Regression models**: Linear, Ridge, Lasso, ElasticNet, SGD, Bayesian
- **Classification models**: Logistic, Ridge Classifier, SGD Classifier
- **Baselines**: Mean/Median predictors for comparison

### 2. Performance Metrics

**Regression:**
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- R² Score
- MAPE (Mean Absolute Percentage Error)

**Classification:**
- Accuracy: (1/n) × Σ 𝟙[ŷᵢ = yᵢ]
- Precision, Recall, F1-Score
- Confusion Matrix

### 3. Visualizations
- Predictions vs Actual scatter plots
- Residual analysis
- Error distribution histograms
- Model comparison bar charts
- Confusion matrices
- Feature importance plots

### 4. Downloadable Files
All files packaged in a single ZIP:
- Trained models (`.pkl` files)
- Preprocessor (for production use)
- Training results (JSON)
- Visualizations (PNG images)

---

## ⚙️ Configuration Options

You can customize the training in **Step 4** of the notebook:

```python
config = {
    'test_size': 0.2,              # 20% test set (adjust 0.1-0.3)
    'scaler_type': 'standard',     # 'standard', 'minmax', or 'robust'
    'handle_outliers': True,       # Handle outliers (True/False)
    'outlier_method': 'clip',      # 'clip', 'remove', or 'cap'
    'feature_engineering': True,   # Apply feature engineering
    'n_categories': 3,             # Classification bins (2-5)
    'category_method': 'quantile', # 'quantile' or 'uniform'
}
```

### Recommended Settings:

**For small datasets (<1000 records):**
```python
config['test_size'] = 0.3
config['handle_outliers'] = False
```

**For large datasets (>10,000 records):**
```python
config['test_size'] = 0.15
config['feature_engineering'] = True
```

**For noisy data:**
```python
config['scaler_type'] = 'robust'
config['handle_outliers'] = True
config['outlier_method'] = 'clip'
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'src'"

**Solution:** Make sure you ran the cell that clones the repository:
```bash
!git clone https://github.com/YOUR_USERNAME/Perf_Plan.git
%cd Perf_Plan
```

### Issue: "CUDA out of memory" or slow performance

**Solution:** Use CPU runtime (default) - GPU not needed for this project
- `Runtime` → `Change runtime type` → `Hardware accelerator: None`

### Issue: "File not found" when loading data

**Solution:** Check your DATA_PATH:
```python
print(f"Current directory: {os.getcwd()}")
print(f"Data path: {DATA_PATH}")
print(f"File exists: {os.path.exists(DATA_PATH)}")
```

### Issue: Session disconnected before download

**Solution:** Save to Google Drive instead:
```python
# Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy models to Drive
!cp -r models /content/drive/MyDrive/zos_mips_models
!cp -r results /content/drive/MyDrive/zos_mips_results
```

### Issue: Models not improving over baseline

**Solutions:**
1. Check data quality (missing values, outliers)
2. Enable feature engineering: `config['feature_engineering'] = True`
3. Try different scalers: `config['scaler_type'] = 'robust'`
4. Increase dataset size (need more than ~100 samples)

---

## 📈 Understanding Results

### Good Model Performance:

**Regression:**
- R² > 0.70 (good fit)
- MAPE < 15% (accurate predictions)
- Test RMSE close to Train RMSE (not overfitting)

**Classification:**
- Accuracy > 60% for 3 classes (baseline ~33%)
- F1-Score > 0.60
- Balanced confusion matrix (no class dominating)

### Baseline Comparison:

Your models should beat:
- **Regression baseline**: Always predicting mean/median (~R² = 0)
- **Classification baseline**: Always predicting majority class (~33% accuracy)

Typical improvements:
- 40-80% better than mean predictor (regression)
- 50-100% better than majority class (classification)

---

## 💡 Tips for Best Results

1. **More data is better**: Aim for 1000+ records minimum
2. **Quality matters**: Clean your data first
3. **Feature engineering helps**: Keep it enabled for linear models
4. **Try multiple runs**: Use different random_state values
5. **Compare models**: Don't just use the first one
6. **Validate on new data**: Test on truly unseen data

---

## 🎓 Next Steps After Colab

### 1. Deploy to Production
```python
# Load trained model
from src.models.regression import MIPSRegressionModel
model = MIPSRegressionModel.load('models/best_model.pkl')

# Make predictions
predictions = model.predict(new_data_scaled)
```

### 2. Schedule Retraining
- Weekly/monthly with new data
- Monitor performance drift
- Update models as needed

### 3. Create API Endpoint
```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # ... preprocessing and prediction ...
    return jsonify({'prediction': float(pred)})
```

### 4. Build Dashboard
- Track predictions over time
- Monitor model performance
- Alert on anomalies

---

## 📚 Additional Resources

- **Full Documentation**: See `README.md` in repository
- **CLI Usage**: `python main.py --help`
- **Local Setup**: `pip install -r requirements.txt`
- **API Reference**: Check docstrings in `src/` modules

---

## 🤝 Support

Having issues? Check:
1. This guide's troubleshooting section
2. Repository README.md
3. Code comments in the notebook
4. Source code in `src/` directory

---

## ⏱️ Estimated Timing

| Step | Time | Description |
|------|------|-------------|
| Setup | 2-3 min | Install dependencies |
| Data Load | <1 min | Create/upload data |
| Training | 3-5 min | Train all models |
| Evaluation | 1-2 min | Generate metrics |
| Visualization | 1-2 min | Create plots |
| Download | <1 min | Package files |
| **Total** | **~8-15 min** | Complete pipeline |

*Times are for ~1000-2000 records on free Colab tier*

---

## 🎯 Success Checklist

After running the notebook, you should have:

- [ ] All dependencies installed successfully
- [ ] Data loaded and explored
- [ ] Correlation matrix visualized
- [ ] 15+ models trained
- [ ] Performance comparison tables generated
- [ ] Best model identified
- [ ] Visualizations created (predictions vs actual, residuals, etc.)
- [ ] Models downloaded as ZIP file
- [ ] Able to make predictions on new data

If all boxes are checked, you're ready for production! 🚀

---

**Happy Predicting! 📊✨**
