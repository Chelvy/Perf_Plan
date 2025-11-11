"""
Model evaluation module for z/OS MIPS prediction

Provides comprehensive metrics and evaluation functions for both
regression and classification models.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from typing import Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluate MIPS prediction models with comprehensive metrics.
    """

    @staticmethod
    def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.

        Args:
            y_true: True target values
            y_pred: Predicted values

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
        }

        # MAPE (handle zero values)
        try:
            metrics['mape'] = mean_absolute_percentage_error(y_true, y_pred) * 100
        except:
            # Calculate manually if sklearn fails
            mask = y_true != 0
            if mask.sum() > 0:
                metrics['mape'] = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            else:
                metrics['mape'] = np.nan

        # Max error
        metrics['max_error'] = np.max(np.abs(y_true - y_pred))

        # Median absolute error
        metrics['median_ae'] = np.median(np.abs(y_true - y_pred))

        # Explained variance
        metrics['explained_variance'] = 1 - (np.var(y_true - y_pred) / np.var(y_true))

        return metrics

    @staticmethod
    def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Calculate classification metrics.

        Args:
            y_true: True class labels
            y_pred: Predicted class labels

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision_macro': precision_score(y_true, y_pred, average='macro', zero_division=0),
            'precision_weighted': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall_macro': recall_score(y_true, y_pred, average='macro', zero_division=0),
            'recall_weighted': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_macro': f1_score(y_true, y_pred, average='macro', zero_division=0),
            'f1_weighted': f1_score(y_true, y_pred, average='weighted', zero_division=0),
        }

        # Confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()

        # Per-class metrics
        try:
            report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            metrics['per_class'] = report
        except:
            metrics['per_class'] = None

        return metrics

    @staticmethod
    def compare_models(results: Dict[str, Dict], metric: str = 'rmse',
                      mode: str = 'regression') -> pd.DataFrame:
        """
        Compare multiple models based on a specific metric.

        Args:
            results: Dictionary of model results
            metric: Metric to compare
            mode: 'regression' or 'classification'

        Returns:
            DataFrame with model comparison
        """
        comparison_data = []

        for model_name, result in results.items():
            if 'error' in result:
                continue

            train_metric = result['train_metrics'].get(metric, np.nan)
            test_metric = result['test_metrics'].get(metric, np.nan)

            comparison_data.append({
                'model': model_name,
                f'train_{metric}': train_metric,
                f'test_{metric}': test_metric,
                'overfitting': abs(train_metric - test_metric) if not np.isnan(train_metric) else np.nan
            })

        df = pd.DataFrame(comparison_data)

        # Sort based on test metric
        if mode == 'regression' and metric in ['mse', 'rmse', 'mae', 'mape']:
            # Lower is better
            df = df.sort_values(f'test_{metric}', ascending=True)
        elif mode == 'classification' and metric in ['accuracy', 'f1_macro', 'precision_macro']:
            # Higher is better
            df = df.sort_values(f'test_{metric}', ascending=False)

        return df

    @staticmethod
    def calculate_baseline_performance(y_true: np.ndarray, strategy: str = 'mean') -> Dict[str, float]:
        """
        Calculate baseline performance metrics.

        Args:
            y_true: True target values
            strategy: 'mean' or 'median'

        Returns:
            Dictionary of baseline metrics
        """
        if strategy == 'mean':
            baseline_pred = np.full_like(y_true, np.mean(y_true))
        else:
            baseline_pred = np.full_like(y_true, np.median(y_true))

        return ModelEvaluator.evaluate_regression(y_true, baseline_pred)

    @staticmethod
    def print_regression_summary(metrics: Dict[str, float], model_name: str = "Model"):
        """
        Print formatted regression metrics.

        Args:
            metrics: Dictionary of metrics
            model_name: Name of the model
        """
        print(f"\n{'='*60}")
        print(f"Regression Metrics - {model_name}")
        print(f"{'='*60}")
        print(f"RMSE:               {metrics['rmse']:>12.2f}")
        print(f"MAE:                {metrics['mae']:>12.2f}")
        print(f"R² Score:           {metrics['r2']:>12.4f}")
        print(f"MAPE (%):           {metrics['mape']:>12.2f}")
        print(f"Max Error:          {metrics['max_error']:>12.2f}")
        print(f"Median AE:          {metrics['median_ae']:>12.2f}")
        print(f"Explained Variance: {metrics['explained_variance']:>12.4f}")
        print(f"{'='*60}\n")

    @staticmethod
    def print_classification_summary(metrics: Dict[str, Any], model_name: str = "Model"):
        """
        Print formatted classification metrics.

        Args:
            metrics: Dictionary of metrics
            model_name: Name of the model
        """
        print(f"\n{'='*60}")
        print(f"Classification Metrics - {model_name}")
        print(f"{'='*60}")
        print(f"Accuracy:           {metrics['accuracy']:>12.4f}")
        print(f"Precision (macro):  {metrics['precision_macro']:>12.4f}")
        print(f"Recall (macro):     {metrics['recall_macro']:>12.4f}")
        print(f"F1 Score (macro):   {metrics['f1_macro']:>12.4f}")
        print(f"\nWeighted Metrics:")
        print(f"Precision:          {metrics['precision_weighted']:>12.4f}")
        print(f"Recall:             {metrics['recall_weighted']:>12.4f}")
        print(f"F1 Score:           {metrics['f1_weighted']:>12.4f}")
        print(f"{'='*60}")

        # Print confusion matrix
        if 'confusion_matrix' in metrics:
            print("\nConfusion Matrix:")
            cm = np.array(metrics['confusion_matrix'])
            print(cm)
        print()

    @staticmethod
    def calculate_improvement_over_baseline(model_metrics: Dict[str, float],
                                           baseline_metrics: Dict[str, float],
                                           metric: str = 'rmse') -> float:
        """
        Calculate percentage improvement over baseline.

        Args:
            model_metrics: Metrics from the model
            baseline_metrics: Metrics from baseline
            metric: Metric to compare

        Returns:
            Percentage improvement (positive means better)
        """
        model_value = model_metrics.get(metric, np.nan)
        baseline_value = baseline_metrics.get(metric, np.nan)

        if np.isnan(model_value) or np.isnan(baseline_value) or baseline_value == 0:
            return np.nan

        # For metrics where lower is better (RMSE, MAE, etc.)
        if metric in ['rmse', 'mse', 'mae', 'mape', 'max_error']:
            improvement = ((baseline_value - model_value) / baseline_value) * 100
        # For metrics where higher is better (R², accuracy, etc.)
        else:
            improvement = ((model_value - baseline_value) / abs(baseline_value)) * 100

        return improvement


class ErrorAnalyzer:
    """
    Analyze prediction errors in detail.
    """

    @staticmethod
    def analyze_residuals(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Analyze residuals (errors) in predictions.

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with residual analysis
        """
        residuals = y_true - y_pred

        analysis = {
            'mean': np.mean(residuals),
            'std': np.std(residuals),
            'min': np.min(residuals),
            'max': np.max(residuals),
            'q25': np.percentile(residuals, 25),
            'median': np.median(residuals),
            'q75': np.percentile(residuals, 75),
            'skewness': pd.Series(residuals).skew(),
            'kurtosis': pd.Series(residuals).kurtosis(),
        }

        # Test for normality (should be ~0 mean, normally distributed)
        analysis['is_unbiased'] = abs(analysis['mean']) < 0.1 * analysis['std']

        return analysis

    @staticmethod
    def identify_worst_predictions(y_true: np.ndarray, y_pred: np.ndarray,
                                  n: int = 10) -> pd.DataFrame:
        """
        Identify samples with worst predictions.

        Args:
            y_true: True values
            y_pred: Predicted values
            n: Number of worst predictions to return

        Returns:
            DataFrame with worst predictions
        """
        errors = np.abs(y_true - y_pred)
        worst_indices = np.argsort(errors)[-n:][::-1]

        worst_df = pd.DataFrame({
            'index': worst_indices,
            'true_value': y_true[worst_indices],
            'predicted_value': y_pred[worst_indices],
            'absolute_error': errors[worst_indices],
            'percentage_error': (errors[worst_indices] / np.abs(y_true[worst_indices])) * 100
        })

        return worst_df

    @staticmethod
    def error_by_magnitude(y_true: np.ndarray, y_pred: np.ndarray,
                          n_bins: int = 5) -> pd.DataFrame:
        """
        Analyze errors by magnitude of true values.

        Args:
            y_true: True values
            y_pred: Predicted values
            n_bins: Number of bins to divide true values into

        Returns:
            DataFrame with error analysis by magnitude
        """
        # Create bins based on true values
        bins = pd.qcut(y_true, q=n_bins, duplicates='drop')

        df = pd.DataFrame({
            'true_value': y_true,
            'pred_value': y_pred,
            'error': y_true - y_pred,
            'abs_error': np.abs(y_true - y_pred),
            'bin': bins
        })

        # Group by bin and calculate statistics
        summary = df.groupby('bin').agg({
            'error': ['mean', 'std'],
            'abs_error': ['mean', 'median'],
            'true_value': 'count'
        }).round(2)

        return summary


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_regression

    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=10, noise=10, random_state=42)

    # Simulate predictions (with some error)
    y_pred = y + np.random.normal(0, 20, size=len(y))

    # Evaluate
    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate_regression(y, y_pred)

    # Print summary
    evaluator.print_regression_summary(metrics, "Example Model")

    # Analyze residuals
    analyzer = ErrorAnalyzer()
    residual_analysis = analyzer.analyze_residuals(y, y_pred)
    print("\nResidual Analysis:")
    for key, value in residual_analysis.items():
        print(f"  {key}: {value}")

    # Worst predictions
    worst = analyzer.identify_worst_predictions(y, y_pred, n=5)
    print("\nWorst Predictions:")
    print(worst)
