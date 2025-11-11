#!/bin/bash
#
# Quick Start Script for z/OS MIPS Prediction on Colab
# This script automates the setup and execution on Google Colab
#
# Usage in Colab:
#   !bash run_colab.sh
#

set -e  # Exit on error

echo "=========================================="
echo "🚀 z/OS MIPS Prediction - Quick Start"
echo "=========================================="
echo ""

# Detect environment
if [ -d "/content" ]; then
    echo "✅ Running on Google Colab"
    IN_COLAB=true
    WORK_DIR="/content/Perf_Plan"
else
    echo "ℹ️  Running locally"
    IN_COLAB=false
    WORK_DIR="$(pwd)"
fi

echo ""
echo "Step 1/5: Installing dependencies..."
echo "--------------------------------------"

if [ "$IN_COLAB" = true ]; then
    # Install requirements silently
    pip install -q -r requirements.txt 2>&1 | grep -v "Requirement already satisfied" || true
else
    pip install -r requirements.txt
fi

echo "✅ Dependencies installed"
echo ""

echo "Step 2/5: Creating sample data..."
echo "--------------------------------------"

python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from src.data_loader import create_sample_data

print("Creating 2000 sample records...")
df = create_sample_data(
    output_path='data/sample/sample_mips_data.csv',
    n_samples=2000,
    n_apps=100,
    random_state=42
)
print(f"✅ Created {len(df)} records")
EOF

echo ""
echo "Step 3/5: Training models..."
echo "--------------------------------------"

python3 main.py train \
    --data-path data/sample/sample_mips_data.csv \
    --mode both \
    --feature-engineering \
    --scaler standard \
    --test-size 0.2 \
    --n-categories 3 \
    --output-dir models \
    --results-dir results

echo ""
echo "Step 4/5: Generating summary report..."
echo "--------------------------------------"

python3 << 'EOF'
import json
import sys
from pathlib import Path

# Find latest results file
results_dir = Path('results')
if results_dir.exists():
    json_files = list(results_dir.glob('training_summary_*.json'))
    if json_files:
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)

        with open(latest_file, 'r') as f:
            results = json.load(f)

        print("\n" + "="*60)
        print("📊 TRAINING RESULTS SUMMARY")
        print("="*60)

        # Regression results
        if 'regression' in results:
            print("\n🔵 REGRESSION MODELS:")
            print("-" * 60)

            # Find best model
            best_rmse = float('inf')
            best_model = None

            for model_name, metrics in results['regression'].items():
                if 'test' in metrics:
                    rmse = metrics['test'].get('rmse', float('inf'))
                    if rmse < best_rmse:
                        best_rmse = rmse
                        best_model = model_name

            if best_model:
                metrics = results['regression'][best_model]['test']
                print(f"\n🏆 Best Model: {best_model}")
                print(f"   RMSE:  {metrics.get('rmse', 0):.2f}")
                print(f"   MAE:   {metrics.get('mae', 0):.2f}")
                print(f"   R²:    {metrics.get('r2', 0):.4f}")
                print(f"   MAPE:  {metrics.get('mape', 0):.2f}%")

        # Classification results
        if 'classification' in results:
            print("\n🟢 CLASSIFICATION MODELS:")
            print("-" * 60)

            # Find best model
            best_acc = 0
            best_model = None

            for model_name, metrics in results['classification'].items():
                if 'test' in metrics:
                    acc = metrics['test'].get('accuracy', 0)
                    if acc > best_acc:
                        best_acc = acc
                        best_model = model_name

            if best_model:
                metrics = results['classification'][best_model]['test']
                print(f"\n🏆 Best Model: {best_model}")
                print(f"   Accuracy:     {metrics.get('accuracy', 0):.4f}")
                print(f"   F1 (macro):   {metrics.get('f1_macro', 0):.4f}")
                print(f"   Precision:    {metrics.get('precision_macro', 0):.4f}")
                print(f"   Recall:       {metrics.get('recall_macro', 0):.4f}")

        print("\n" + "="*60)
        print("✅ Training completed successfully!")
        print("="*60)
    else:
        print("⚠️  No results file found")
else:
    print("⚠️  Results directory not found")
EOF

echo ""
echo "Step 5/5: Packaging results..."
echo "--------------------------------------"

# Create zip file for download
if command -v zip &> /dev/null; then
    ZIP_FILE="zos_mips_models_results.zip"

    echo "Creating ZIP archive..."
    zip -q -r "$ZIP_FILE" models/ results/ 2>/dev/null || true

    if [ -f "$ZIP_FILE" ]; then
        SIZE=$(du -h "$ZIP_FILE" | cut -f1)
        echo "✅ Created $ZIP_FILE ($SIZE)"
    fi
fi

echo ""
echo "=========================================="
echo "🎉 ALL STEPS COMPLETED!"
echo "=========================================="
echo ""
echo "📁 Generated files:"
echo "   - models/          (Trained models)"
echo "   - results/         (Metrics and plots)"
if [ -f "zos_mips_models_results.zip" ]; then
    echo "   - zos_mips_models_results.zip (All results)"
fi
echo ""

if [ "$IN_COLAB" = true ]; then
    echo "📥 To download in Colab, run:"
    echo "   from google.colab import files"
    echo "   files.download('zos_mips_models_results.zip')"
else
    echo "📁 Files are available in the current directory"
fi

echo ""
echo "🚀 Next steps:"
echo "   1. Review results in results/ directory"
echo "   2. Load best model from models/ directory"
echo "   3. Use for predictions on new data"
echo ""
echo "📖 For more info, see README.md and COLAB_GUIDE.md"
echo "=========================================="
