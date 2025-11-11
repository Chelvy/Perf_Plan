"""
Visualization module for z/OS MIPS prediction

Creates plots and charts for model performance analysis and results presentation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class MIPSVisualizer:
    """
    Create visualizations for MIPS prediction models.
    """

    def __init__(self, output_dir: str = "results"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_predictions_vs_actual(self, y_true: np.ndarray, y_pred: np.ndarray,
                                   title: str = "Predictions vs Actual",
                                   save_name: Optional[str] = None):
        """
        Plot predicted values vs actual values.

        Args:
            y_true: True values
            y_pred: Predicted values
            title: Plot title
            save_name: Filename to save (if None, just display)
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Scatter plot
        ax.scatter(y_true, y_pred, alpha=0.5, s=30, edgecolors='k', linewidths=0.5)

        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

        ax.set_xlabel('Actual MIPS', fontsize=12)
        ax.set_ylabel('Predicted MIPS', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add R² annotation
        from sklearn.metrics import r2_score
        r2 = r2_score(y_true, y_pred)
        ax.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax.transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_residuals(self, y_true: np.ndarray, y_pred: np.ndarray,
                      title: str = "Residual Plot",
                      save_name: Optional[str] = None):
        """
        Plot residuals (errors) vs predicted values.

        Args:
            y_true: True values
            y_pred: Predicted values
            title: Plot title
            save_name: Filename to save
        """
        residuals = y_true - y_pred

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Residuals vs Predicted
        axes[0].scatter(y_pred, residuals, alpha=0.5, s=30, edgecolors='k', linewidths=0.5)
        axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[0].set_xlabel('Predicted MIPS', fontsize=12)
        axes[0].set_ylabel('Residuals', fontsize=12)
        axes[0].set_title('Residuals vs Predicted', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # Residuals histogram
        axes[1].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
        axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel('Residuals', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Residuals Distribution', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_model_comparison(self, comparison_df: pd.DataFrame,
                            metric: str = 'rmse',
                            title: Optional[str] = None,
                            save_name: Optional[str] = None):
        """
        Plot comparison of multiple models.

        Args:
            comparison_df: DataFrame with model comparison data
            metric: Metric to plot
            title: Plot title
            save_name: Filename to save
        """
        if title is None:
            title = f"Model Comparison - {metric.upper()}"

        fig, ax = plt.subplots(figsize=(14, 8))

        train_col = f'train_{metric}'
        test_col = f'test_{metric}'

        x = np.arange(len(comparison_df))
        width = 0.35

        # Create bars
        bars1 = ax.bar(x - width/2, comparison_df[train_col], width, label='Train', alpha=0.8)
        bars2 = ax.bar(x + width/2, comparison_df[test_col], width, label='Test', alpha=0.8)

        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel(metric.upper(), fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_df['model'], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_feature_importance(self, importance_df: pd.DataFrame,
                               top_n: int = 20,
                               title: str = "Feature Importance",
                               save_name: Optional[str] = None):
        """
        Plot feature importance.

        Args:
            importance_df: DataFrame with feature importance
            top_n: Number of top features to show
            title: Plot title
            save_name: Filename to save
        """
        # Get top N features
        top_features = importance_df.head(top_n).copy()

        fig, ax = plt.subplots(figsize=(12, max(8, top_n * 0.4)))

        # Create horizontal bar plot
        y_pos = np.arange(len(top_features))
        ax.barh(y_pos, top_features['abs_coefficient'], alpha=0.8)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_features['feature'])
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('Absolute Coefficient', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_confusion_matrix(self, cm: np.ndarray, classes: List[str],
                            title: str = "Confusion Matrix",
                            save_name: Optional[str] = None,
                            normalize: bool = False):
        """
        Plot confusion matrix for classification.

        Args:
            cm: Confusion matrix
            classes: Class labels
            title: Plot title
            save_name: Filename to save
            normalize: Whether to normalize values
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)

        ax.set(xticks=np.arange(cm.shape[1]),
               yticks=np.arange(cm.shape[0]),
               xticklabels=classes,
               yticklabels=classes,
               title=title,
               ylabel='True Label',
               xlabel='Predicted Label')

        # Rotate the tick labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add text annotations
        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                       ha="center", va="center",
                       color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_learning_curve(self, train_scores: np.ndarray, test_scores: np.ndarray,
                           train_sizes: np.ndarray,
                           title: str = "Learning Curve",
                           save_name: Optional[str] = None):
        """
        Plot learning curve showing model performance vs training size.

        Args:
            train_scores: Training scores
            test_scores: Test scores
            train_sizes: Training set sizes
            title: Plot title
            save_name: Filename to save
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate mean and std
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        # Plot
        ax.plot(train_sizes, train_mean, 'o-', color='r', label='Training score')
        ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                        alpha=0.1, color='r')

        ax.plot(train_sizes, test_mean, 'o-', color='g', label='Cross-validation score')
        ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std,
                        alpha=0.1, color='g')

        ax.set_xlabel('Training Set Size', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def plot_error_distribution(self, y_true: np.ndarray, y_pred: np.ndarray,
                               title: str = "Error Distribution Analysis",
                               save_name: Optional[str] = None):
        """
        Create comprehensive error distribution plots.

        Args:
            y_true: True values
            y_pred: Predicted values
            title: Plot title
            save_name: Filename to save
        """
        errors = y_true - y_pred
        abs_errors = np.abs(errors)
        pct_errors = (abs_errors / np.abs(y_true)) * 100

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Error histogram
        axes[0, 0].hist(errors, bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(x=0, color='r', linestyle='--', lw=2)
        axes[0, 0].set_xlabel('Error', fontsize=11)
        axes[0, 0].set_ylabel('Frequency', fontsize=11)
        axes[0, 0].set_title('Error Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Absolute error histogram
        axes[0, 1].hist(abs_errors, bins=50, edgecolor='black', alpha=0.7, color='orange')
        axes[0, 1].set_xlabel('Absolute Error', fontsize=11)
        axes[0, 1].set_ylabel('Frequency', fontsize=11)
        axes[0, 1].set_title('Absolute Error Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Percentage error histogram
        axes[1, 0].hist(pct_errors, bins=50, edgecolor='black', alpha=0.7, color='green')
        axes[1, 0].set_xlabel('Percentage Error (%)', fontsize=11)
        axes[1, 0].set_ylabel('Frequency', fontsize=11)
        axes[1, 0].set_title('Percentage Error Distribution', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. Q-Q plot for normality check
        from scipy import stats
        stats.probplot(errors, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot (Normality Check)', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_name:
            plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot to {self.output_dir / save_name}")

        plt.show()

    def create_full_report(self, y_true: np.ndarray, y_pred: np.ndarray,
                          model_name: str = "Model",
                          feature_importance: Optional[pd.DataFrame] = None):
        """
        Create a full visualization report.

        Args:
            y_true: True values
            y_pred: Predicted values
            model_name: Name of the model
            feature_importance: Feature importance DataFrame
        """
        logger.info(f"Creating full visualization report for {model_name}...")

        # 1. Predictions vs Actual
        self.plot_predictions_vs_actual(
            y_true, y_pred,
            title=f"{model_name} - Predictions vs Actual",
            save_name=f"{model_name}_predictions_vs_actual.png"
        )

        # 2. Residuals
        self.plot_residuals(
            y_true, y_pred,
            title=f"{model_name} - Residual Analysis",
            save_name=f"{model_name}_residuals.png"
        )

        # 3. Error distribution
        self.plot_error_distribution(
            y_true, y_pred,
            title=f"{model_name} - Error Distribution",
            save_name=f"{model_name}_error_distribution.png"
        )

        # 4. Feature importance (if provided)
        if feature_importance is not None and not feature_importance.empty:
            self.plot_feature_importance(
                feature_importance,
                title=f"{model_name} - Feature Importance",
                save_name=f"{model_name}_feature_importance.png"
            )

        logger.info("Full report created successfully!")


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_regression

    # Generate sample data
    X, y = make_regression(n_samples=500, n_features=10, noise=10, random_state=42)
    y_pred = y + np.random.normal(0, 15, size=len(y))

    # Create visualizer
    viz = MIPSVisualizer(output_dir="results/test")

    # Create plots
    viz.plot_predictions_vs_actual(y, y_pred)
    viz.plot_residuals(y, y_pred)
    viz.plot_error_distribution(y, y_pred)

    print("Visualizations created!")
