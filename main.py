#!/usr/bin/env python3
"""
Main script for z/OS MIPS prediction

Command-line interface for training and evaluating MIPS prediction models.
"""

import argparse
import sys
import logging
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_loader import MIPSDataLoader, create_sample_data
from src.training import MIPSTrainingPipeline
from src.evaluation import ModelEvaluator
from src.visualization import MIPSVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data_command(args):
    """Create sample data for testing."""
    logger.info("Creating sample data...")

    output_path = Path(args.output) if args.output else Path("data/sample/sample_mips_data.csv")

    df = create_sample_data(
        output_path=str(output_path),
        n_samples=args.n_samples,
        n_apps=args.n_apps,
        random_state=args.random_state
    )

    logger.info(f"Sample data created: {len(df)} records")
    logger.info(f"Saved to: {output_path}")


def train_command(args):
    """Train models."""
    logger.info("Starting training pipeline...")

    # Build config from arguments
    config = {
        'data_path': args.data_path,
        'test_size': args.test_size,
        'random_state': args.random_state,
        'time_based_split': args.time_based,
        'scaler_type': args.scaler,
        'handle_outliers': args.handle_outliers,
        'outlier_method': args.outlier_method,
        'feature_engineering': args.feature_engineering,
        'n_categories': args.n_categories,
        'category_method': args.category_method,
        'save_models': not args.no_save,
        'output_dir': args.output_dir,
        'results_dir': args.results_dir
    }

    # Create and run pipeline
    pipeline = MIPSTrainingPipeline(config)

    # Determine mode
    mode = args.mode
    results = pipeline.run_full_pipeline(mode=mode)

    # Print summary
    print("\n" + "="*80)
    print("TRAINING RESULTS SUMMARY")
    print("="*80)

    if 'regression' in results and args.mode in ['regression', 'both']:
        print("\nREGRESSION MODELS:")
        print("-" * 80)

        # Create comparison
        evaluator = ModelEvaluator()
        comparison = evaluator.compare_models(results['regression'], metric='rmse', mode='regression')
        print(comparison.head(10).to_string(index=False))

    if 'classification' in results and args.mode in ['classification', 'both']:
        print("\n\nCLASSIFICATION MODELS:")
        print("-" * 80)

        # Create comparison
        evaluator = ModelEvaluator()
        comparison = evaluator.compare_models(results['classification'], metric='accuracy', mode='classification')
        print(comparison.head(10).to_string(index=False))

    print("\n" + "="*80)
    logger.info("Training completed!")


def evaluate_command(args):
    """Evaluate a trained model."""
    logger.info(f"Evaluating model from {args.model_path}")

    # Load model
    from src.models.regression import MIPSRegressionModel

    model = MIPSRegressionModel.load(args.model_path)

    # Load data
    loader = MIPSDataLoader(args.data_path)
    data = loader.load_csv()

    X, y = loader.get_feature_target_split(data)

    # Preprocess (would need saved preprocessor in production)
    from src.preprocessing import MIPSPreprocessor

    preprocessor = MIPSPreprocessor()
    X_scaled = preprocessor.fit_transform(X)

    # Predict
    y_pred = model.predict(X_scaled)

    # Evaluate
    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate_regression(y, y_pred)

    # Print results
    evaluator.print_regression_summary(metrics, "Loaded Model")

    # Create visualizations if requested
    if args.visualize:
        viz = MIPSVisualizer(output_dir=args.output_dir)
        viz.create_full_report(y, y_pred, model_name="loaded_model")


def predict_command(args):
    """Make predictions on new data."""
    logger.info(f"Making predictions using model from {args.model_path}")

    # Load model and preprocessor
    from src.models.regression import MIPSRegressionModel
    from src.preprocessing import MIPSPreprocessor

    model = MIPSRegressionModel.load(args.model_path)
    preprocessor = MIPSPreprocessor.load(args.preprocessor_path)

    # Load data
    loader = MIPSDataLoader(args.input)
    data = loader.load_csv()

    # Get features
    if 'MIPS_consumption' in data.columns:
        X, _ = loader.get_feature_target_split(data)
    else:
        X = data

    # Preprocess
    X_scaled = preprocessor.transform(X)

    # Predict
    predictions = model.predict(X_scaled)

    # Add predictions to dataframe
    data['MIPS_prediction'] = predictions

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    logger.info(f"Predictions saved to {output_path}")
    logger.info(f"Made {len(predictions)} predictions")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="z/OS MIPS Prediction System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Create sample data command
    sample_parser = subparsers.add_parser('create-sample', help='Create sample data')
    sample_parser.add_argument('--output', type=str, help='Output path for sample data')
    sample_parser.add_argument('--n-samples', type=int, default=1000, help='Number of samples')
    sample_parser.add_argument('--n-apps', type=int, default=50, help='Number of applications')
    sample_parser.add_argument('--random-state', type=int, default=42, help='Random seed')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train models')
    train_parser.add_argument('--data-path', type=str, required=True, help='Path to training data')
    train_parser.add_argument('--mode', type=str, default='both',
                            choices=['regression', 'classification', 'both'],
                            help='Training mode')
    train_parser.add_argument('--test-size', type=float, default=0.2, help='Test set size')
    train_parser.add_argument('--random-state', type=int, default=42, help='Random seed')
    train_parser.add_argument('--time-based', action='store_true', help='Use time-based split')
    train_parser.add_argument('--scaler', type=str, default='standard',
                            choices=['standard', 'minmax', 'robust'],
                            help='Scaler type')
    train_parser.add_argument('--no-handle-outliers', dest='handle_outliers',
                            action='store_false', help='Disable outlier handling')
    train_parser.add_argument('--outlier-method', type=str, default='clip',
                            choices=['clip', 'remove', 'cap'],
                            help='Outlier handling method')
    train_parser.add_argument('--no-feature-engineering', dest='feature_engineering',
                            action='store_false', help='Disable feature engineering')
    train_parser.add_argument('--n-categories', type=int, default=3,
                            help='Number of categories for classification')
    train_parser.add_argument('--category-method', type=str, default='quantile',
                            choices=['quantile', 'uniform'],
                            help='Category binning method')
    train_parser.add_argument('--no-save', action='store_true', help='Do not save models')
    train_parser.add_argument('--output-dir', type=str, default='models',
                            help='Output directory for models')
    train_parser.add_argument('--results-dir', type=str, default='results',
                            help='Output directory for results')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a trained model')
    eval_parser.add_argument('--model-path', type=str, required=True, help='Path to model file')
    eval_parser.add_argument('--data-path', type=str, required=True, help='Path to test data')
    eval_parser.add_argument('--visualize', action='store_true', help='Create visualizations')
    eval_parser.add_argument('--output-dir', type=str, default='results',
                           help='Output directory for visualizations')

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Make predictions on new data')
    predict_parser.add_argument('--model-path', type=str, required=True, help='Path to model file')
    predict_parser.add_argument('--preprocessor-path', type=str, required=True,
                              help='Path to preprocessor file')
    predict_parser.add_argument('--input', type=str, required=True, help='Input data path')
    predict_parser.add_argument('--output', type=str, required=True, help='Output predictions path')

    args = parser.parse_args()

    if args.command == 'create-sample':
        create_sample_data_command(args)
    elif args.command == 'train':
        train_command(args)
    elif args.command == 'evaluate':
        evaluate_command(args)
    elif args.command == 'predict':
        predict_parser(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
