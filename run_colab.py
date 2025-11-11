#!/usr/bin/env python3
"""
Quick start script for running z/OS MIPS prediction on Google Colab

Usage in Colab:
    !python run_colab.py

Or with custom options:
    !python run_colab.py --n-samples 5000 --mode regression
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_step(step, total, text):
    """Print step information."""
    print(f"\n{'='*70}")
    print(f"  Step {step}/{total}: {text}")
    print(f"{'='*70}\n")


def check_environment():
    """Check if running on Colab."""
    try:
        import google.colab
        return True
    except:
        return False


def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
        check=True,
        capture_output=True
    )
    print("✅ Dependencies installed")


def create_sample_data(n_samples=2000, n_apps=100):
    """Create sample z/OS MIPS data."""
    print(f"Creating {n_samples} sample records with {n_apps} applications...")

    # Add src to path
    sys.path.insert(0, 'src')
    from src.data_loader import create_sample_data

    output_path = 'data/sample/sample_mips_data.csv'
    df = create_sample_data(
        output_path=output_path,
        n_samples=n_samples,
        n_apps=n_apps,
        random_state=42
    )

    print(f"✅ Created {len(df)} records")
    print(f"   Applications: {df['application'].nunique()}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Saved to: {output_path}")

    return output_path


def train_models(data_path, mode='both', config=None):
    """Train the models."""
    print(f"Training models in '{mode}' mode...")

    # Build command
    cmd = [
        sys.executable, 'main.py', 'train',
        '--data-path', data_path,
        '--mode', mode,
        '--feature-engineering',
    ]

    if config:
        cmd.extend(['--test-size', str(config.get('test_size', 0.2))])
        cmd.extend(['--scaler', config.get('scaler_type', 'standard')])
        cmd.extend(['--n-categories', str(config.get('n_categories', 3))])
        cmd.extend(['--random-state', str(config.get('random_state', 42))])

        if not config.get('handle_outliers', True):
            cmd.append('--no-handle-outliers')

    # Run training
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Training completed successfully")
    else:
        print("❌ Training failed")
        print(result.stderr)
        sys.exit(1)


def generate_summary():
    """Generate and display training summary."""
    print("Generating summary report...")

    results_dir = Path('results')
    if not results_dir.exists():
        print("⚠️  Results directory not found")
        return

    # Find latest results file
    json_files = list(results_dir.glob('training_summary_*.json'))
    if not json_files:
        print("⚠️  No results file found")
        return

    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)

    with open(latest_file, 'r') as f:
        results = json.load(f)

    print_header("📊 TRAINING RESULTS SUMMARY")

    # Regression results
    if 'regression' in results:
        print("\n🔵 REGRESSION MODELS:")
        print("-" * 70)

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
            print(f"   RMSE:              {metrics.get('rmse', 0):>10.2f}")
            print(f"   MAE:               {metrics.get('mae', 0):>10.2f}")
            print(f"   R² Score:          {metrics.get('r2', 0):>10.4f}")
            print(f"   MAPE (%):          {metrics.get('mape', 0):>10.2f}")

            # Compare with baseline
            if 'baseline_mean' in results['regression']:
                baseline_rmse = results['regression']['baseline_mean']['test']['rmse']
                improvement = ((baseline_rmse - best_rmse) / baseline_rmse) * 100
                print(f"\n   📈 Improvement over baseline: {improvement:.1f}%")

    # Classification results
    if 'classification' in results:
        print("\n\n🟢 CLASSIFICATION MODELS:")
        print("-" * 70)

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
            print(f"   Accuracy:          {metrics.get('accuracy', 0):>10.4f}")
            print(f"   F1 (macro):        {metrics.get('f1_macro', 0):>10.4f}")
            print(f"   Precision (macro): {metrics.get('precision_macro', 0):>10.4f}")
            print(f"   Recall (macro):    {metrics.get('recall_macro', 0):>10.4f}")

            # Compare with baseline
            if 'baseline_majority' in results['classification']:
                baseline_acc = results['classification']['baseline_majority']['test']['accuracy']
                improvement = ((best_acc - baseline_acc) / baseline_acc) * 100
                print(f"\n   📈 Improvement over baseline: {improvement:.1f}%")

    print("\n" + "="*70)
    print("✅ Summary generated successfully")
    print("="*70)


def package_results():
    """Package results into a ZIP file."""
    print("Packaging results...")

    import zipfile

    zip_filename = 'zos_mips_models_results.zip'

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add models
        if os.path.exists('models'):
            for file in Path('models').rglob('*'):
                if file.is_file():
                    zipf.write(file, arcname=f'models/{file.name}')

        # Add results
        if os.path.exists('results'):
            for file in Path('results').rglob('*'):
                if file.is_file():
                    zipf.write(file, arcname=f'results/{file.name}')

    size_mb = Path(zip_filename).stat().st_size / (1024 * 1024)
    print(f"✅ Created {zip_filename} ({size_mb:.2f} MB)")

    return zip_filename


def download_results(zip_filename):
    """Download results (Colab only)."""
    try:
        from google.colab import files
        print(f"⬇️  Downloading {zip_filename}...")
        files.download(zip_filename)
        print("✅ Download complete!")
        return True
    except:
        print("ℹ️  Not running on Colab - files saved locally")
        return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Quick start for z/OS MIPS prediction on Colab'
    )
    parser.add_argument('--n-samples', type=int, default=2000,
                       help='Number of sample records to create')
    parser.add_argument('--n-apps', type=int, default=100,
                       help='Number of applications')
    parser.add_argument('--mode', type=str, default='both',
                       choices=['regression', 'classification', 'both'],
                       help='Training mode')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size (0.1-0.3)')
    parser.add_argument('--no-download', action='store_true',
                       help='Skip automatic download')
    parser.add_argument('--config', type=str,
                       help='Path to JSON config file')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f).get('training', {})
    else:
        config = {'test_size': args.test_size}

    # Print header
    print_header("🚀 z/OS MIPS Prediction - Quick Start")

    # Check environment
    is_colab = check_environment()
    print(f"Environment: {'Google Colab ✅' if is_colab else 'Local 💻'}")
    print(f"Working directory: {os.getcwd()}")

    try:
        # Step 1: Install dependencies
        print_step(1, 5, "Installing dependencies")
        install_dependencies()

        # Step 2: Create sample data
        print_step(2, 5, "Creating sample data")
        data_path = create_sample_data(args.n_samples, args.n_apps)

        # Step 3: Train models
        print_step(3, 5, "Training models")
        train_models(data_path, args.mode, config)

        # Step 4: Generate summary
        print_step(4, 5, "Generating summary report")
        generate_summary()

        # Step 5: Package and download
        print_step(5, 5, "Packaging results")
        zip_filename = package_results()

        if is_colab and not args.no_download:
            download_results(zip_filename)

        # Final message
        print_header("🎉 ALL STEPS COMPLETED!")

        print("\n📁 Generated files:")
        print("   - models/          (Trained models)")
        print("   - results/         (Metrics and visualizations)")
        print(f"   - {zip_filename}   (Complete package)")

        print("\n🚀 Next steps:")
        print("   1. Review results in results/ directory")
        print("   2. Load best model from models/ directory")
        print("   3. Use for predictions on new data")

        print("\n📖 For more information:")
        print("   - README.md          (Full documentation)")
        print("   - COLAB_GUIDE.md     (Colab-specific guide)")
        print("   - notebooks/         (Interactive examples)")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
