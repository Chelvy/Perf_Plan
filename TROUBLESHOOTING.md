# 🔧 Troubleshooting Guide

Common issues and solutions for z/OS MIPS Prediction system.

---

## ❌ Error: "fatal: could not read Username for 'https://github.com'"

**Problem:** Git clone fails in Google Colab with authentication error.

**Cause:** The GitHub repository is **PRIVATE** and requires authentication.

### 🔧 Solutions:

### ✅ Solution 1: Make Repository Public (Recommended)

This is the easiest solution for notebooks:

1. Go to https://github.com/chelvy/Perf_Plan
2. Click **Settings** (gear icon)
3. Scroll to **Danger Zone**
4. Click **Change visibility**
5. Select **Make public**
6. Confirm by typing repository name
7. Re-run the notebook

**Pros:**
- ✅ Works seamlessly with Colab
- ✅ No authentication needed
- ✅ Easy sharing
- ✅ One-click execution

**Cons:**
- ⚠️ Code is publicly visible

---

### ✅ Solution 2: Manual Upload (Quick Fix)

If you can't make repository public:

1. Download repository as ZIP:
   - Go to https://github.com/chelvy/Perf_Plan
   - Click **Code** → **Download ZIP**
2. In Colab, the notebook will prompt you to upload
3. Upload the ZIP file
4. Notebook extracts it automatically
5. Continue from Section 2

**Pros:**
- ✅ Repository stays private
- ✅ Quick workaround
- ✅ No authentication needed

**Cons:**
- ⚠️ Manual step required
- ⚠️ Need to re-upload for updates

---

### ✅ Solution 3: GitHub Personal Access Token

For programmatic access while keeping repository private:

1. Generate a PAT:
   - Go to https://github.com/settings/tokens
   - **Generate new token (classic)**
   - Select scope: `repo` (Full control of private repositories)
   - Generate and **copy the token**

2. In Colab, replace the clone cell with:

```python
# Use PAT for authentication
import os
USERNAME = "chelvy"
TOKEN = "ghp_your_token_here"  # ⬅️ Paste your PAT
REPO = "Perf_Plan"

!git clone https://{USERNAME}:{TOKEN}@github.com/{USERNAME}/{REPO}.git
```

**Pros:**
- ✅ Repository stays private
- ✅ Automated cloning
- ✅ Can commit/push

**Cons:**
- ⚠️ Token visible in notebook (use Colab secrets)
- ⚠️ Need to manage token expiration
- ⚠️ More complex

---

## 📝 Using Colab Secrets (Secure PAT Storage)

To securely store your PAT:

1. In Colab, click **🔑 (Key icon)** in left sidebar
2. Add new secret:
   - Name: `GITHUB_TOKEN`
   - Value: Your PAT
3. Update clone cell:

```python
from google.colab import userdata
import subprocess

TOKEN = userdata.get('GITHUB_TOKEN')
USERNAME = "chelvy"
REPO = "Perf_Plan"

subprocess.run([
    "git", "clone",
    f"https://{USERNAME}:{TOKEN}@github.com/{USERNAME}/{REPO}.git"
])
```

---

## ❌ Error: "ModuleNotFoundError" after clone

**Problem:** Python modules not found after cloning.

**Solution:**

```python
import sys
import os

# Ensure we're in the right directory
os.chdir('Perf_Plan')

# Add src to Python path
sys.path.insert(0, 'src')

# Now imports should work
from src.data_loader import MIPSDataLoader
```

---

## ❌ Error: "No module named 'sklearn'"

**Problem:** Dependencies not installed.

**Solution:**

```python
# Install dependencies
!pip install -q -r requirements.txt

# Verify installation
import sklearn
import pandas
import numpy
print("✅ All dependencies installed")
```

---

## ❌ Error: "DATA_PATH not set"

**Problem:** Forgot to upload data or create sample data.

**Solution:**

1. Go to **Section 2: Configuration**
2. Set ONE of these to `True`:
   - `USE_PIVOT_DATA = True` (for pivot format)
   - `USE_UPLOADED_DATA = True` (for long format)
   - `USE_SAMPLE_DATA = True` (for testing)
3. Execute **Section 3** (corresponding subsection)

---

## ❌ Error: "FileNotFoundError: requirements.txt"

**Problem:** Not in correct directory.

**Solution:**

```python
import os

# Check current directory
print(os.getcwd())
print(os.listdir())

# Change to Perf_Plan if needed
if os.path.exists('Perf_Plan'):
    os.chdir('Perf_Plan')
    print(f"✅ Changed to: {os.getcwd()}")
```

---

## ❌ Transformation Error: "Could not parse timestamp"

**Problem:** Date columns in pivot data have unusual format.

**Solution:**

Pivot data dates should be:
- `YYYY-MM-DD` (e.g., 2022-01-01)
- `DD/MM/YYYY` (e.g., 01/01/2022)
- `YYYY/MM/DD` (e.g., 2022/01/01)

If your dates are different:
1. Open your data in Excel
2. Format date columns to `YYYY-MM-DD`
3. Save and re-upload

---

## ❌ Training Error: "Missing required columns"

**Problem:** Data doesn't have all required columns.

**Required columns:**
- `application`
- `timestamp` (optional, can be auto-generated)
- `M24H`, `MDIU`, `MPTE`, `TXDIU`, `EFF`, `TVDIU`
- `MIPS_consumption`

**Solution:**

Check your data:
```python
import pandas as pd
df = pd.read_csv('your_file.csv')
print(df.columns)

# Required columns
required = ['application', 'M24H', 'MDIU', 'MPTE',
            'TXDIU', 'EFF', 'TVDIU', 'MIPS_consumption']

missing = [col for col in required if col not in df.columns]
if missing:
    print(f"Missing: {missing}")
```

---

## ❌ Error: "Memory Error" or Colab Crash

**Problem:** Dataset too large for Colab.

**Solutions:**

1. **Reduce sample size:**
```python
# In Section 2
SAMPLE_CONFIG = {
    'n_samples': 1000,  # ⬇️ Reduce from 2000
    'n_apps': 50,       # ⬇️ Reduce from 100
    'random_state': 42
}
```

2. **Use Colab Pro** (more RAM)

3. **Sample your data:**
```python
# Sample 50% of data
df_sampled = df.sample(frac=0.5, random_state=42)
df_sampled.to_csv('sampled_data.csv', index=False)
```

---

## 📊 Performance Issues

### Models training too slowly

1. **Disable feature engineering:**
```python
CONFIG = {
    ...
    'feature_engineering': False,  # ⬅️ Faster training
    ...
}
```

2. **Reduce categories:**
```python
CONFIG = {
    ...
    'n_categories': 2,  # ⬅️ 2 instead of 3 (binary classification)
    ...
}
```

3. **Use faster scalers:**
```python
CONFIG = {
    ...
    'scaler_type': 'minmax',  # ⬅️ Faster than 'standard'
    ...
}
```

---

## 🆘 Still Need Help?

### Check Documentation:
- [README.md](README.md) - Main documentation
- [TRANSFORM_GUIDE.md](TRANSFORM_GUIDE.md) - Data transformation
- [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md) - Upload instructions

### Common Checks:
- ✅ Repository is public or PAT is configured
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ In correct directory (`Perf_Plan/`)
- ✅ Data format is correct
- ✅ ONE data source selected in Section 2

### Debug Mode:

Run this in a Colab cell to check everything:

```python
import os
import sys

print("=== ENVIRONMENT CHECK ===")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')[:10]}")
print(f"Python path: {sys.path[:3]}")

print("\n=== DEPENDENCY CHECK ===")
try:
    import pandas
    print(f"✅ pandas {pandas.__version__}")
except:
    print("❌ pandas not installed")

try:
    import sklearn
    print(f"✅ scikit-learn {sklearn.__version__}")
except:
    print("❌ scikit-learn not installed")

try:
    import numpy
    print(f"✅ numpy {numpy.__version__}")
except:
    print("❌ numpy not installed")

print("\n=== DATA CHECK ===")
if 'DATA_PATH' in dir():
    print(f"✅ DATA_PATH set: {DATA_PATH}")
    if os.path.exists(DATA_PATH):
        print(f"✅ File exists")
    else:
        print(f"❌ File not found")
else:
    print("❌ DATA_PATH not set")
```

---

**If none of these solutions work, check the GitHub Issues or create a new one with your error message.**
