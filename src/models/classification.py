"""
Classification models for z/OS MIPS prediction

Implements classification models to predict MIPS consumption categories.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import (
    LogisticRegression,
    RidgeClassifier,
    SGDClassifier
)
from sklearn.model_selection import GridSearchCV, cross_val_score
from typing import Dict, Any, Optional, Tuple
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSClassificationModel:
    """
    Classification model for predicting MIPS consumption categories.
    """

    def __init__(self, model_type: str = 'logistic', **kwargs):
        """
        Initialize classification model.

        Args:
            model_type: Type of model ('logistic', 'ridge', 'sgd')
            **kwargs: Additional parameters for the model
        """
        self.model_type = model_type
        self.model = None
        self.model_params = kwargs
        self.is_fitted = False
        self.classes_ = None

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the model based on type."""
        if self.model_type == 'logistic':
            # Logistic Regression
            penalty = self.model_params.pop('penalty', 'l2')
            C = self.model_params.pop('C', 1.0)
            solver = self.model_params.pop('solver', 'lbfgs')
            max_iter = self.model_params.pop('max_iter', 10000)
            multi_class = self.model_params.pop('multi_class', 'multinomial')
            self.model = LogisticRegression(
                penalty=penalty,
                C=C,
                max_iter=max_iter,
                multi_class=multi_class,
                solver=solver,
                **self.model_params
            )

        elif self.model_type == 'ridge':
            # Ridge Classifier
            alpha = self.model_params.pop('alpha', 1.0)
            self.model = RidgeClassifier(alpha=alpha, **self.model_params)

        elif self.model_type == 'sgd':
            # SGD Classifier
            loss = self.model_params.pop('loss', 'log_loss')
            penalty = self.model_params.pop('penalty', 'l2')
            alpha = self.model_params.pop('alpha', 0.0001)
            max_iter = self.model_params.pop('max_iter', 10000)
            tol = self.model_params.pop('tol', 1e-3)
            self.model = SGDClassifier(
                loss=loss,
                penalty=penalty,
                alpha=alpha,
                max_iter=max_iter,
                tol=tol,
                **self.model_params
            )

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        logger.info(f"Initialized {self.model_type} classification model")

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit the model.

        Args:
            X: Training features
            y: Training targets (class labels)
        """
        logger.info(f"Training {self.model_type} classifier on {len(X)} samples...")

        self.model.fit(X, y)
        self.is_fitted = True
        self.classes_ = self.model.classes_

        logger.info(f"Model training completed. Classes: {self.classes_}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Features to predict

        Returns:
            Predicted class labels
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Features to predict

        Returns:
            Class probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            # Ridge classifier doesn't have predict_proba
            logger.warning(f"{self.model_type} doesn't support probability predictions")
            return None

    def get_feature_importance(self, feature_names: Optional[list] = None) -> pd.DataFrame:
        """
        Get feature importance (coefficients).

        Args:
            feature_names: Names of features

        Returns:
            DataFrame with feature importance per class
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        if not hasattr(self.model, 'coef_'):
            return pd.DataFrame()

        coefs = self.model.coef_

        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(coefs.shape[1])]

        # For multi-class, we have coefficients for each class
        if len(coefs.shape) == 1:
            # Binary classification
            importance_df = pd.DataFrame({
                'feature': feature_names[:len(coefs)],
                'coefficient': coefs,
                'abs_coefficient': np.abs(coefs)
            }).sort_values('abs_coefficient', ascending=False)
        else:
            # Multi-class classification
            importance_data = []
            for i, class_label in enumerate(self.classes_):
                for j, feature in enumerate(feature_names[:coefs.shape[1]]):
                    importance_data.append({
                        'feature': feature,
                        'class': class_label,
                        'coefficient': coefs[i, j],
                        'abs_coefficient': np.abs(coefs[i, j])
                    })

            importance_df = pd.DataFrame(importance_data)

        return importance_df

    def save(self, filepath: str):
        """Save model to disk."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump({
            'model_type': self.model_type,
            'model': self.model,
            'model_params': self.model_params,
            'is_fitted': self.is_fitted,
            'classes_': self.classes_
        }, filepath)

        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'MIPSClassificationModel':
        """Load model from disk."""
        data = joblib.load(filepath)

        model = cls(model_type=data['model_type'])
        model.model = data['model']
        model.model_params = data['model_params']
        model.is_fitted = data['is_fitted']
        model.classes_ = data['classes_']

        logger.info(f"Model loaded from {filepath}")

        return model


class ClassificationModelFactory:
    """
    Factory for creating and managing multiple classification models.
    """

    @staticmethod
    def create_baseline_models() -> Dict[str, MIPSClassificationModel]:
        """
        Create baseline classification models.

        Returns:
            Dictionary of baseline models
        """
        models = {
            'logistic': MIPSClassificationModel('logistic', C=1.0),
            'logistic_weak_reg': MIPSClassificationModel('logistic', C=10.0),
            'logistic_strong_reg': MIPSClassificationModel('logistic', C=0.1),
            'ridge': MIPSClassificationModel('ridge', alpha=1.0),
            'sgd': MIPSClassificationModel('sgd', random_state=42),
        }

        logger.info(f"Created {len(models)} baseline classification models")

        return models

    @staticmethod
    def create_all_linear_classifiers() -> Dict[str, MIPSClassificationModel]:
        """
        Create comprehensive set of linear classifiers.

        Returns:
            Dictionary of all linear classifiers
        """
        models = {
            # Logistic Regression with L2 penalty
            'logistic_l2_C0.01': MIPSClassificationModel('logistic', penalty='l2', C=0.01),
            'logistic_l2_C0.1': MIPSClassificationModel('logistic', penalty='l2', C=0.1),
            'logistic_l2_C1.0': MIPSClassificationModel('logistic', penalty='l2', C=1.0),
            'logistic_l2_C10.0': MIPSClassificationModel('logistic', penalty='l2', C=10.0),
            'logistic_l2_C100.0': MIPSClassificationModel('logistic', penalty='l2', C=100.0),

            # Logistic Regression with L1 penalty
            'logistic_l1_C0.1': MIPSClassificationModel('logistic', penalty='l1', C=0.1, solver='saga'),
            'logistic_l1_C1.0': MIPSClassificationModel('logistic', penalty='l1', C=1.0, solver='saga'),
            'logistic_l1_C10.0': MIPSClassificationModel('logistic', penalty='l1', C=10.0, solver='saga'),

            # Ridge Classifier with various alphas
            'ridge_0.01': MIPSClassificationModel('ridge', alpha=0.01),
            'ridge_0.1': MIPSClassificationModel('ridge', alpha=0.1),
            'ridge_1.0': MIPSClassificationModel('ridge', alpha=1.0),
            'ridge_10.0': MIPSClassificationModel('ridge', alpha=10.0),
            'ridge_100.0': MIPSClassificationModel('ridge', alpha=100.0),

            # SGD Classifier with various settings
            'sgd_hinge': MIPSClassificationModel('sgd', loss='hinge', random_state=42),
            'sgd_log': MIPSClassificationModel('sgd', loss='log_loss', random_state=42),
            'sgd_modified_huber': MIPSClassificationModel('sgd', loss='modified_huber', random_state=42),
        }

        logger.info(f"Created {len(models)} linear classifiers")

        return models

    @staticmethod
    def hyperparameter_search(model_type: str, X_train: np.ndarray, y_train: np.ndarray,
                             cv: int = 5) -> Tuple[MIPSClassificationModel, Dict[str, Any]]:
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

        if model_type == 'logistic':
            param_grid = {
                'C': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
                'penalty': ['l2']
            }
            base_model = LogisticRegression(max_iter=10000, multi_class='multinomial')

        elif model_type == 'ridge':
            param_grid = {'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]}
            base_model = RidgeClassifier()

        elif model_type == 'sgd':
            param_grid = {
                'alpha': [0.0001, 0.001, 0.01, 0.1],
                'loss': ['log_loss', 'modified_huber'],
                'penalty': ['l2', 'l1', 'elasticnet']
            }
            base_model = SGDClassifier(max_iter=10000, random_state=42)

        else:
            raise ValueError(f"Hyperparameter search not implemented for {model_type}")

        # Perform grid search
        grid_search = GridSearchCV(
            base_model, param_grid, cv=cv, scoring='accuracy',
            n_jobs=-1, verbose=1
        )

        grid_search.fit(X_train, y_train)

        best_params = grid_search.best_params_
        logger.info(f"Best parameters: {best_params}")

        # Create model with best parameters
        best_model = MIPSClassificationModel(model_type, **best_params)
        best_model.fit(X_train, y_train)

        return best_model, best_params


class MajorityClassBaseline:
    """
    Baseline classifier that always predicts the majority class.
    """

    def __init__(self):
        """Initialize baseline."""
        self.majority_class = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit the baseline by finding majority class."""
        unique, counts = np.unique(y, return_counts=True)
        self.majority_class = unique[np.argmax(counts)]
        logger.info(f"Majority class: {self.majority_class}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using majority class."""
        return np.full(len(X), self.majority_class)


if __name__ == "__main__":
    # Example usage
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    # Generate sample data
    X, y = make_classification(
        n_samples=1000, n_features=20, n_informative=15,
        n_classes=3, random_state=42
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create and train models
    print("Creating baseline classifiers...")
    models = ClassificationModelFactory.create_baseline_models()

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy:.4f}")

    # Test majority class baseline
    print("\nTesting majority class baseline...")
    baseline = MajorityClassBaseline()
    baseline.fit(X_train, y_train)
    y_pred_baseline = baseline.predict(X_test)
    baseline_accuracy = accuracy_score(y_test, y_pred_baseline)
    print(f"Baseline accuracy: {baseline_accuracy:.4f}")
