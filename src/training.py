"""
Training pipeline for z/OS MIPS prediction models

Handles end-to-end training workflow including data loading, preprocessing,
feature engineering, model training, and evaluation.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import json
from datetime import datetime

from .data_loader import MIPSDataLoader
from .preprocessing import MIPSPreprocessor, create_mips_categories, OutlierDetector
from .features import MIPSFeatureEngineering
from .models.regression import MIPSRegressionModel, RegressionModelFactory, BaselinePredictor
from .models.classification import MIPSClassificationModel, ClassificationModelFactory, MajorityClassBaseline
from .evaluation import ModelEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSTrainingPipeline:
    """
    End-to-end training pipeline for MIPS prediction.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize training pipeline.

        Args:
            config: Configuration dictionary with training parameters
        """
        self.config = config or self._default_config()
        self.data_loader = None
        self.preprocessor = None
        self.feature_engineer = None
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'data_path': 'data/sample/sample_mips_data.csv',
            'test_size': 0.2,
            'random_state': 42,
            'time_based_split': False,
            'scaler_type': 'standard',
            'handle_outliers': True,
            'outlier_method': 'clip',
            'feature_engineering': True,
            'n_categories': 3,  # For classification
            'category_method': 'quantile',
            'save_models': True,
            'output_dir': 'models',
            'results_dir': 'results'
        }

    def load_data(self, data_path: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load and split data.

        Args:
            data_path: Path to data file. If None, uses config value.

        Returns:
            Tuple of (train_data, test_data)
        """
        data_path = data_path or self.config['data_path']
        logger.info(f"Loading data from {data_path}")

        self.data_loader = MIPSDataLoader(data_path)

        # Check if path is a directory or file
        path_obj = Path(data_path)
        if path_obj.is_dir():
            data = self.data_loader.load_multiple_csvs()
        else:
            data = self.data_loader.load_csv()

        # Print data info
        info = self.data_loader.get_data_info()
        logger.info(f"Loaded {info['n_records']} records with {info['n_features']} features")

        # Split data
        train_data, test_data = self.data_loader.split_train_test(
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            time_based=self.config['time_based_split']
        )

        return train_data, test_data

    def preprocess_data(self, train_data: pd.DataFrame,
                       test_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series]:
        """
        Preprocess training and test data.

        Args:
            train_data: Training dataframe
            test_data: Test dataframe

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        logger.info("Preprocessing data...")

        # Handle outliers if configured
        if self.config['handle_outliers']:
            numeric_cols = train_data.select_dtypes(include=[np.number]).columns
            indicator_cols = [col for col in numeric_cols if col != 'MIPS_consumption']

            train_data = OutlierDetector.handle_outliers(
                train_data, indicator_cols,
                method=self.config['outlier_method']
            )

        # Feature engineering
        if self.config['feature_engineering']:
            logger.info("Applying feature engineering...")
            self.feature_engineer = MIPSFeatureEngineering()
            train_data = self.feature_engineer.create_all_features(train_data)
            test_data = self.feature_engineer.create_all_features(test_data)

        # Split features and target
        X_train, y_train = self.data_loader.get_feature_target_split(train_data)
        X_test, y_test = self.data_loader.get_feature_target_split(test_data)

        # Preprocess features
        self.preprocessor = MIPSPreprocessor(scaler_type=self.config['scaler_type'])
        X_train_scaled = self.preprocessor.fit_transform(X_train)
        X_test_scaled = self.preprocessor.transform(X_test)

        logger.info(f"Training set: {X_train_scaled.shape}, Test set: {X_test_scaled.shape}")

        return X_train_scaled, X_test_scaled, y_train, y_test

    def train_regression_models(self, X_train: np.ndarray, X_test: np.ndarray,
                                y_train: pd.Series, y_test: pd.Series) -> Dict[str, Dict]:
        """
        Train all regression models and evaluate.

        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training targets
            y_test: Test targets

        Returns:
            Dictionary of results for each model
        """
        logger.info("\n" + "="*80)
        logger.info("TRAINING REGRESSION MODELS")
        logger.info("="*80)

        # Create models
        models = RegressionModelFactory.create_all_linear_models()

        # Add baseline models
        models['baseline_mean'] = BaselinePredictor('mean')
        models['baseline_median'] = BaselinePredictor('median')

        results = {}

        # Train and evaluate each model
        for name, model in models.items():
            logger.info(f"\n--- Training {name} ---")

            try:
                # Train
                model.fit(X_train, y_train)

                # Predict
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                # Evaluate
                evaluator = ModelEvaluator()
                train_metrics = evaluator.evaluate_regression(y_train, y_train_pred)
                test_metrics = evaluator.evaluate_regression(y_test, y_test_pred)

                results[name] = {
                    'model': model,
                    'train_metrics': train_metrics,
                    'test_metrics': test_metrics,
                    'predictions': {
                        'train': y_train_pred,
                        'test': y_test_pred
                    }
                }

                logger.info(f"Train RMSE: {train_metrics['rmse']:.2f}, Test RMSE: {test_metrics['rmse']:.2f}")
                logger.info(f"Train R²: {train_metrics['r2']:.4f}, Test R²: {test_metrics['r2']:.4f}")

            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                results[name] = {'error': str(e)}

        # Find best model based on test RMSE
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        if valid_results:
            best_name = min(valid_results.keys(),
                          key=lambda k: valid_results[k]['test_metrics']['rmse'])
            self.best_model = valid_results[best_name]['model']
            self.best_model_name = best_name
            logger.info(f"\nBest regression model: {best_name}")

        self.results['regression'] = results
        return results

    def train_classification_models(self, X_train: np.ndarray, X_test: np.ndarray,
                                   y_train: pd.Series, y_test: pd.Series) -> Dict[str, Dict]:
        """
        Train all classification models and evaluate.

        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training targets (continuous)
            y_test: Test targets (continuous)

        Returns:
            Dictionary of results for each model
        """
        logger.info("\n" + "="*80)
        logger.info("TRAINING CLASSIFICATION MODELS")
        logger.info("="*80)

        # Convert continuous MIPS to categories
        logger.info("Converting MIPS to categories...")
        y_train_cat, bins_info = create_mips_categories(
            y_train,
            method=self.config['category_method'],
            n_bins=self.config['n_categories']
        )

        # Apply same binning to test set
        if self.config['category_method'] == 'quantile':
            quantiles = list(bins_info['quantiles'].values())
            y_test_cat = pd.cut(y_test, bins=quantiles, labels=['LOW', 'MEDIUM', 'HIGH'][:self.config['n_categories']],
                               include_lowest=True, duplicates='drop')
        else:
            y_test_cat = pd.cut(y_test, bins=self.config['n_categories'],
                               labels=['LOW', 'MEDIUM', 'HIGH'][:self.config['n_categories']])

        # Create models
        models = ClassificationModelFactory.create_all_linear_classifiers()

        # Add baseline
        models['baseline_majority'] = MajorityClassBaseline()

        results = {}

        # Train and evaluate each model
        for name, model in models.items():
            logger.info(f"\n--- Training {name} ---")

            try:
                # Train
                model.fit(X_train, y_train_cat)

                # Predict
                y_train_pred = model.predict(X_train)
                y_test_pred = model.predict(X_test)

                # Evaluate
                evaluator = ModelEvaluator()
                train_metrics = evaluator.evaluate_classification(y_train_cat, y_train_pred)
                test_metrics = evaluator.evaluate_classification(y_test_cat, y_test_pred)

                results[name] = {
                    'model': model,
                    'train_metrics': train_metrics,
                    'test_metrics': test_metrics,
                    'predictions': {
                        'train': y_train_pred,
                        'test': y_test_pred
                    }
                }

                logger.info(f"Train Accuracy: {train_metrics['accuracy']:.4f}, Test Accuracy: {test_metrics['accuracy']:.4f}")

            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                results[name] = {'error': str(e)}

        # Find best model based on test accuracy
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        if valid_results:
            best_name = max(valid_results.keys(),
                          key=lambda k: valid_results[k]['test_metrics']['accuracy'])
            logger.info(f"\nBest classification model: {best_name}")

        self.results['classification'] = results
        self.results['classification_bins'] = bins_info

        return results

    def save_models(self):
        """Save trained models and preprocessor."""
        if not self.config['save_models']:
            return

        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save preprocessor
        if self.preprocessor:
            preprocessor_path = output_dir / f"preprocessor_{timestamp}.pkl"
            self.preprocessor.save(str(preprocessor_path))

        # Save best regression model
        if self.best_model:
            model_path = output_dir / f"best_regression_{self.best_model_name}_{timestamp}.pkl"
            if hasattr(self.best_model, 'save'):
                self.best_model.save(str(model_path))
            logger.info(f"Saved best model to {model_path}")

    def save_results(self):
        """Save training results and metrics."""
        results_dir = Path(self.config['results_dir'])
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Prepare results summary
        summary = {
            'timestamp': timestamp,
            'config': self.config,
            'regression': {},
            'classification': {}
        }

        # Add regression results
        if 'regression' in self.results:
            for name, result in self.results['regression'].items():
                if 'error' not in result:
                    summary['regression'][name] = {
                        'train': result['train_metrics'],
                        'test': result['test_metrics']
                    }

        # Add classification results
        if 'classification' in self.results:
            for name, result in self.results['classification'].items():
                if 'error' not in result:
                    summary['classification'][name] = {
                        'train': result['train_metrics'],
                        'test': result['test_metrics']
                    }

        # Save to JSON
        summary_path = results_dir / f"training_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Saved results to {summary_path}")

    def run_full_pipeline(self, mode: str = 'both') -> Dict[str, Any]:
        """
        Run the complete training pipeline.

        Args:
            mode: 'regression', 'classification', or 'both'

        Returns:
            Dictionary containing all results
        """
        logger.info("Starting full training pipeline...")

        # Load data
        train_data, test_data = self.load_data()

        # Preprocess
        X_train, X_test, y_train, y_test = self.preprocess_data(train_data, test_data)

        # Train models based on mode
        if mode in ['regression', 'both']:
            self.train_regression_models(X_train, X_test, y_train, y_test)

        if mode in ['classification', 'both']:
            self.train_classification_models(X_train, X_test, y_train, y_test)

        # Save models and results
        self.save_models()
        self.save_results()

        logger.info("\nTraining pipeline completed!")

        return self.results


if __name__ == "__main__":
    # Example usage
    config = {
        'data_path': 'data/sample/sample_mips_data.csv',
        'test_size': 0.2,
        'random_state': 42,
        'feature_engineering': True,
        'save_models': True
    }

    pipeline = MIPSTrainingPipeline(config)
    results = pipeline.run_full_pipeline(mode='both')

    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
