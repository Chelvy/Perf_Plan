# 📤 Guide: Upload Your Own z/OS Data

Quick guide to upload and use your own z/OS MIPS performance data in Google Colab.

---

## 🎯 Quick Start (3 Steps)

### Step 1: Prepare Your Data

Your CSV file must have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `application` | App name/ID | APP_001, CICS_PROD |
| `timestamp` | Date/time | 2024-01-01 or 2024-01-01 14:30:00 |
| `M24H` | MIPS 24 hours | 1000.5 |
| `MDIU` | MIPS Diurne (daytime) | 850.0 |
| `MPTE` | MIPS Pointe (peak) | 1200.0 |
| `TXDIU` | Transaction rate DIU (×1000) | 50.0 |
| `EFF` | Efficiency (0-1 or 0-100) | 0.95 or 95 |
| `TVDIU` | Time value DIU | 100.0 |
| `MIPS_consumption` | **Target** - Actual MIPS | 950.0 |

### Step 2: Upload in Colab

**Method A: Using Main Notebook**

1. Open the [main Colab notebook](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/03_colab_full_pipeline.ipynb)
2. Go to **Step 2: Prepare Data**
3. Find **Option B: Upload Your Own Data**
4. Change `USE_UPLOADED_DATA = False` to `USE_UPLOADED_DATA = True`
5. Run the cell
6. Click "Choose Files" and select your CSV
7. Continue to Step 3

**Method B: Using Upload Notebook**

1. Open the [upload notebook](https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb)
2. Download template (optional)
3. Upload your CSV file
4. Auto-validation will check your data
5. Fix any issues if needed
6. Copy the `DATA_PATH` value
7. Use it in the main notebook

### Step 3: Train Models

Once uploaded, your data will be used automatically for training!

---

## 📋 Example CSV Format

```csv
application,timestamp,M24H,MDIU,MPTE,TXDIU,EFF,TVDIU,MIPS_consumption
APP_001,2024-01-01,1000,800,1200,50,0.95,100,950
APP_002,2024-01-01,1500,1200,1800,75,0.90,150,1350
APP_003,2024-01-01,900,750,1100,45,0.92,90,850
APP_001,2024-01-02,1050,850,1250,52,0.94,105,1000
APP_002,2024-01-02,1550,1250,1850,78,0.91,155,1400
```

---

## ✅ Data Validation Checklist

Before uploading, check:

- [ ] File is in CSV format
- [ ] File encoding is UTF-8
- [ ] All 9 required columns are present
- [ ] Column names match exactly (case-sensitive)
- [ ] No extra spaces in column names
- [ ] Numeric columns contain only numbers
- [ ] No missing values in `MIPS_consumption` column
- [ ] At least 500+ records (1000+ recommended)
- [ ] Data covers multiple time periods
- [ ] Multiple applications included

---

## 🛠️ Common Issues & Fixes

### Issue: "Missing columns"
**Solution:** Check column names match exactly. Download template for reference.

### Issue: "Could not parse timestamp"
**Solution:** Use format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`

### Issue: "Data type error"
**Solution:** Ensure numeric columns (M24H, MDIU, etc.) contain only numbers, no text.

### Issue: "File encoding error"
**Solution:** Save your CSV with UTF-8 encoding:
- Excel: Save As → CSV UTF-8
- Google Sheets: Download → CSV

### Issue: "Too few records"
**Solution:** Minimum 500 records recommended. More data = better results.

### Issue: "EFF values > 1"
**Solution:** No problem! Will auto-convert from 0-100 to 0-1 scale.

---

## 🎨 Option: Download Template

Run this in a Colab cell to get a template:

```python
import pandas as pd
from google.colab import files

# Create template
template = pd.DataFrame({
    'application': ['APP_001', 'APP_002', 'APP_003'],
    'timestamp': ['2024-01-01', '2024-01-01', '2024-01-01'],
    'M24H': [1000.0, 1500.0, 900.0],
    'MDIU': [800.0, 1200.0, 750.0],
    'MPTE': [1200.0, 1800.0, 1100.0],
    'TXDIU': [50.0, 75.0, 45.0],
    'EFF': [0.95, 0.90, 0.92],
    'TVDIU': [100.0, 150.0, 90.0],
    'MIPS_consumption': [950.0, 1350.0, 850.0]
})

template.to_csv('mips_template.csv', index=False)
files.download('mips_template.csv')
```

---

## 🚀 Full Upload Workflow

### Detailed Steps:

1. **Prepare your z/OS data**
   - Export from your mainframe monitoring system
   - Format as CSV with required columns
   - Ensure 3 years of historical data if possible

2. **Open Colab notebook**
   ```
   https://colab.research.google.com/github/chelvy/Perf_Plan/blob/main/notebooks/04_upload_your_data.ipynb
   ```

3. **Download template** (optional)
   - Run Step 1 in the notebook
   - Use template to format your data

4. **Upload your file**
   - Run Step 2 in the notebook
   - Click "Choose Files" button
   - Select your CSV file
   - Wait for upload to complete

5. **Validate data**
   - Automatic validation runs
   - Check for errors or warnings
   - Review data preview

6. **Fix issues** (if any)
   - Run Step 4 to auto-fix common issues
   - Or manually correct in your CSV

7. **Train models**
   - Copy the `DATA_PATH` value
   - Go to main notebook
   - Use uploaded data for training

---

## 📊 Data Quality Tips

For best results:

✅ **DO:**
- Include 1000+ records minimum
- Cover multiple time periods (days, weeks, months)
- Include diverse applications
- Use actual production data
- Clean outliers beforehand
- Ensure consistent units

❌ **DON'T:**
- Mix different time granularities
- Include test/development data only
- Have too many missing values (>10%)
- Use inconsistent column names
- Include sensitive information

---

## 💡 Pro Tips

1. **More data = better models**
   - 1000 records: Good
   - 5000 records: Better
   - 10000+ records: Best

2. **Time coverage matters**
   - Daily data: Minimum 6 months
   - Weekly data: Minimum 2 years
   - Monthly data: Minimum 3 years

3. **Application diversity helps**
   - Include various app types
   - Mix of high/low MIPS consumers
   - Different usage patterns

4. **Clean data first**
   - Remove obvious errors
   - Check for duplicate records
   - Validate ranges make sense

5. **Test with sample first**
   - Use the sample data initially
   - Verify the pipeline works
   - Then upload your real data

---

## 🔄 Alternative: Google Drive

If your file is already in Google Drive:

```python
from google.colab import drive

# Mount Drive
drive.mount('/content/drive')

# Set path to your data
DATA_PATH = '/content/drive/MyDrive/zos_data/mips_historical.csv'

# Verify
import pandas as pd
data = pd.read_csv(DATA_PATH)
print(f"Loaded {len(data)} records from Drive")
```

---

## 📞 Need Help?

- **Template issues**: Use 04_upload_your_data.ipynb Step 1
- **Validation errors**: Check column names and data types
- **Format questions**: See example CSV above
- **Large files**: Use Google Drive method instead

---

## ✅ Success Checklist

After upload, you should have:

- [x] File uploaded successfully
- [x] All required columns present
- [x] Data validation passed
- [x] No critical errors shown
- [x] DATA_PATH variable set
- [x] Ready to train models

**If all checked, you're ready! 🎉**

---

## 🎯 Next Steps

1. ✅ Data uploaded and validated
2. ➡️ Return to main notebook
3. ➡️ Continue to Step 4: Configure Training
4. ➡️ Run training with your data
5. ➡️ Download trained models

**Good luck! 🚀**
