"""
Regression models for z/OS MIPS prediction

Implements various linear regression models to predict continuous MIPS values.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    SGDRegressor,
    BayesianRidge
)
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, cross_val_score
from typing import Dict, Any, Optional, Tuple
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSRegressionModel:
    """
    Base class for MIPS regression models.
    """

    def __init__(self, model_type: str = 'linear', **kwargs):
        """
        Initialize regression model.

        Args:
            model_type: Type of model ('linear', 'ridge', 'lasso', 'elasticnet', 'polynomial', 'sgd', 'bayesian')
            **kwargs: Additional parameters for the model
        """
        self.model_type = model_type
        self.model = None
        self.model_params = kwargs
        self.is_fitted = False

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model based on type."""
        if self.model_type == 'linear':
            self.model = LinearRegression(**self.model_params)

        elif self.model_type == 'ridge':
            # Ridge regression with L2 regularization
            alpha = self.model_params.pop('alpha', 1.0)
            self.model = Ridge(alpha=alpha, **self.model_params)

        elif self.model_type == 'lasso':
            # Lasso regression with L1 regularization
            alpha = self.model_params.pop('alpha', 1.0)
            self.model = Lasso(alpha=alpha, max_iter=10000, **self.model_params)

        elif self.model_type == 'elasticnet':
            # ElasticNet with L1 and L2 regularization
            alpha = self.model_params.pop('alpha', 1.0)
            l1_ratio = self.model_params.pop('l1_ratio', 0.5)
            self.model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio,
                                   max_iter=10000, **self.model_params)

        elif self.model_type == 'polynomial':
            # Polynomial regression
            degree = self.model_params.pop('degree', 2)
            base_model = self.model_params.pop('base_model', 'linear')

            if base_model == 'ridge':
                estimator = Ridge(alpha=self.model_params.pop('alpha', 1.0))
            elif base_model == 'lasso':
                estimator = Lasso(alpha=self.model_params.pop('alpha', 1.0), max_iter=10000)
            else:
                estimator = LinearRegression()

            self.model = Pipeline([
                ('poly', PolynomialFeatures(degree=degree)),
                ('regressor', estimator)
            ])

        elif self.model_type == 'sgd':
            # Stochastic Gradient Descent
            self.model = SGDRegressor(max_iter=10000, tol=1e-3, **self.model_params)

        elif self.model_type == 'bayesian':
            # Bayesian Ridge Regression
            self.model = BayesianRidge(**self.model_params)

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        logger.info(f"Initialized {self.model_type} regression model")

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit the model.

        Args:
            X: Training features
            y: Training targets
        """
        logger.info(f"Training {self.model_type} model on {len(X)} samples...")

        self.model.fit(X, y)
        self.is_fitted = True

        logger.info("Model training completed")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Features to predict

        Returns:
            Predicted MIPS values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self.model.predict(X)

    def get_feature_importance(self, feature_names: Optional[list] = None) -> pd.DataFrame:
        """
        Get feature importance (coefficients).

        Args:
            feature_names: Names of features

        Returns:
            DataFrame with feature importance
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        # Get coefficients
        if hasattr(self.model, 'coef_'):
            coefs = self.model.coef_
        elif hasattr(self.model, 'named_steps'):  # Pipeline
            coefs = self.model.named_steps['regressor'].coef_
        else:
            return pd.DataFrame()

        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(coefs))]

        importance_df = pd.DataFrame({
            'feature': feature_names[:len(coefs)],
            'coefficient': coefs,
            'abs_coefficient': np.abs(coefs)
        }).sort_values('abs_coefficient', ascending=False)

        return importance_df

    def save(self, filepath: str):
        """Save model to disk."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump({
            'model_type': self.model_type,
            'model': self.model,
            'model_params': self.model_params,
            'is_fitted': self.is_fitted
        }, filepath)

        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'MIPSRegressionModel':
        """Load model from disk."""
        data = joblib.load(filepath)

        model = cls(model_type=data['model_type'])
        model.model = data['model']
        model.model_params = data['model_params']
        model.is_fitted = data['is_fitted']

        logger.info(f"Model loaded from {filepath}")

        return model


class RegressionModelFactory:
    """
    Factory for creating and managing multiple regression models.
    """

    @staticmethod
    def create_baseline_models() -> Dict[str, MIPSRegressionModel]:
        """
        Create baseline regression models for comparison.

        Returns:
            Dictionary of baseline models
        """
        models = {
            'linear': MIPSRegressionModel('linear'),
            'ridge_weak': MIPSRegressionModel('ridge', alpha=0.1),
            'ridge_moderate': MIPSRegressionModel('ridge', alpha=1.0),
            'ridge_strong': MIPSRegressionModel('ridge', alpha=10.0),
            'lasso_weak': MIPSRegressionModel('lasso', alpha=0.1),
            'lasso_moderate': MIPSRegressionModel('lasso', alpha=1.0),
            'lasso_strong': MIPSRegressionModel('lasso', alpha=10.0),
            'elasticnet': MIPSRegressionModel('elasticnet', alpha=1.0, l1_ratio=0.5),
        }

        logger.info(f"Created {len(models)} baseline models")

        return models

    @staticmethod
    def create_all_linear_models() -> Dict[str, MIPSRegressionModel]:
        """
        Create comprehensive set of linear models.

        Returns:
            Dictionary of all linear models
        """
        models = {
            # Basic linear regression
            'linear': MIPSRegressionModel('linear'),

            # Ridge regression with various alphas
            'ridge_0.01': MIPSRegressionModel('ridge', alpha=0.01),
            'ridge_0.1': MIPSRegressionModel('ridge', alpha=0.1),
            'ridge_1.0': MIPSRegressionModel('ridge', alpha=1.0),
            'ridge_10.0': MIPSRegressionModel('ridge', alpha=10.0),
            'ridge_100.0': MIPSRegressionModel('ridge', alpha=100.0),

            # Lasso regression with various alphas
            'lasso_0.01': MIPSRegressionModel('lasso', alpha=0.01),
            'lasso_0.1': MIPSRegressionModel('lasso', alpha=0.1),
            'lasso_1.0': MIPSRegressionModel('lasso', alpha=1.0),
            'lasso_10.0': MIPSRegressionModel('lasso', alpha=10.0),

            # ElasticNet with various combinations
            'elasticnet_l1_0.3': MIPSRegressionModel('elasticnet', alpha=1.0, l1_ratio=0.3),
            'elasticnet_l1_0.5': MIPSRegressionModel('elasticnet', alpha=1.0, l1_ratio=0.5),
            'elasticnet_l1_0.7': MIPSRegressionModel('elasticnet', alpha=1.0, l1_ratio=0.7),

            # SGD-based
            'sgd': MIPSRegressionModel('sgd', random_state=42),

            # Bayesian Ridge
            'bayesian_ridge': MIPSRegressionModel('bayesian'),
        }

        logger.info(f"Created {len(models)} linear models")

        return models

    @staticmethod
    def hyperparameter_search(model_type: str, X_train: np.ndarray, y_train: np.ndarray,
                             cv: int = 5) -> Tuple[MIPSRegressionModel, Dict[str, Any]]:
        """
        Perform hyperparameter search for a given model type.

        Args:
            model_type: Type of model to tune
            X_train: Training features
            y_train: Training targets
            cv: Number of cross-validation folds

        Returns:
            Tuple of (best model, best parameters)
        """
        logger.info(f"Performing hyperparameter search for {model_type}...")

        if model_type == 'ridge':
            param_grid = {'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]}
            base_model = Ridge()

        elif model_type == 'lasso':
            param_grid = {'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]}
            base_model = Lasso(max_iter=10000)

        elif model_type == 'elasticnet':
            param_grid = {
                'alpha': [0.001, 0.01, 0.1, 1.0, 10.0],
                'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
            }
            base_model = ElasticNet(max_iter=10000)

        else:
            raise ValueError(f"Hyperparameter search not implemented for {model_type}")

        # Perform grid search
        grid_search = GridSearchCV(
            base_model, param_grid, cv=cv, scoring='neg_mean_squared_error',
            n_jobs=-1, verbose=1
        )

        grid_search.fit(X_train, y_train)

        best_params = grid_search.best_params_
        logger.info(f"Best parameters: {best_params}")

        # Create model with best parameters
        best_model = MIPSRegressionModel(model_type, **best_params)
        best_model.fit(X_train, y_train)

        return best_model, best_params


class BaselinePredictor:
    """
    Simple baseline predictors for comparison.
    """

    def __init__(self, strategy: str = 'mean'):
        """
        Initialize baseline predictor.

        Args:
            strategy: 'mean' or 'median'
        """
        self.strategy = strategy
        self.value = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the baseline."""
        if self.strategy == 'mean':
            self.value = np.mean(y)
        elif self.strategy == 'median':
            self.value = np.median(y)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using baseline value."""
        return np.full(len(X), self.value)


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_regression
    from sklearn.model_selection import train_test_split

    # Generate sample data
    X, y = make_regression(n_samples=1000, n_features=20, noise=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train models
    print("Creating baseline models...")
    models = RegressionModelFactory.create_baseline_models()

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate MSE
        mse = np.mean((y_test - y_pred) ** 2)
        print(f"MSE: {mse:.2f}")
