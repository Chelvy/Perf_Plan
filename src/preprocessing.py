"""
Data preprocessing module for z/OS MIPS prediction

Handles data cleaning, normalization, encoding, and preparation for ML models.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, RobustScaler
from sklearn.impute import SimpleImputer
from typing import Tuple, Optional, Dict, Any
import logging
import joblib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSPreprocessor:
    """
    Preprocessor for z/OS MIPS data.

    Handles:
    - Missing value imputation
    - Feature scaling/normalization
    - Categorical encoding
    - Outlier detection and handling
    """

    def __init__(self, scaler_type: str = 'standard'):
        """
        Initialize the preprocessor.

        Args:
            scaler_type: Type of scaler to use ('standard', 'minmax', 'robust')
        """
        self.scaler_type = scaler_type
        self.scaler = None
        self.label_encoders = {}
        self.imputer = None
        self.feature_names = None
        self.fitted = False

        # Initialize scaler based on type
        if scaler_type == 'standard':
            self.scaler = StandardScaler()
        elif scaler_type == 'minmax':
            self.scaler = MinMaxScaler()
        elif scaler_type == 'robust':
            self.scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaler type: {scaler_type}")

    def fit(self, X: pd.DataFrame) -> 'MIPSPreprocessor':
        """
        Fit the preprocessor on training data.

        Args:
            X: Training features

        Returns:
            Self
        """
        logger.info("Fitting preprocessor...")
        self.feature_names = X.columns.tolist()

        # Create a copy to avoid modifying original
        X_copy = X.copy()

        # Handle timestamp column if present
        if 'timestamp' in X_copy.columns:
            X_copy = self._extract_time_features(X_copy)

        # Encode categorical features
        categorical_cols = X_copy.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in X_copy.columns:
                self.label_encoders[col] = LabelEncoder()
                X_copy[col] = self.label_encoders[col].fit_transform(X_copy[col].astype(str))

        # Fit imputer for missing values
        self.imputer = SimpleImputer(strategy='median')
        X_imputed = self.imputer.fit_transform(X_copy)

        # Fit scaler
        self.scaler.fit(X_imputed)

        self.fitted = True
        logger.info(f"Preprocessor fitted on {len(X)} samples")

        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform data using the fitted preprocessor.

        Args:
            X: Features to transform

        Returns:
            Transformed feature array
        """
        if not self.fitted:
            raise ValueError("Preprocessor must be fitted before transform. Call fit() first.")

        X_copy = X.copy()

        # Handle timestamp column if present
        if 'timestamp' in X_copy.columns:
            X_copy = self._extract_time_features(X_copy)

        # Encode categorical features
        for col, encoder in self.label_encoders.items():
            if col in X_copy.columns:
                # Handle unseen categories
                X_copy[col] = X_copy[col].astype(str).map(
                    lambda x: x if x in encoder.classes_ else encoder.classes_[0]
                )
                X_copy[col] = encoder.transform(X_copy[col])

        # Impute missing values
        X_imputed = self.imputer.transform(X_copy)

        # Scale features
        X_scaled = self.scaler.transform(X_imputed)

        return X_scaled

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit and transform in one step.

        Args:
            X: Features to fit and transform

        Returns:
            Transformed feature array
        """
        return self.fit(X).transform(X)

    def _extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract useful features from timestamp column.

        Args:
            df: DataFrame with timestamp column

        Returns:
            DataFrame with time features extracted
        """
        if 'timestamp' not in df.columns:
            return df

        df = df.copy()

        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Extract time features
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['day'] = df['timestamp'].dt.day
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        df['quarter'] = df['timestamp'].dt.quarter
        df['is_weekend'] = (df['timestamp'].dt.dayofweek >= 5).astype(int)

        # Drop original timestamp
        df = df.drop('timestamp', axis=1)

        return df

    def inverse_transform_features(self, X: np.ndarray) -> np.ndarray:
        """
        Inverse transform scaled features back to original scale.

        Args:
            X: Scaled features

        Returns:
            Features in original scale
        """
        return self.scaler.inverse_transform(X)

    def save(self, filepath: str):
        """
        Save preprocessor to disk.

        Args:
            filepath: Path to save the preprocessor
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump({
            'scaler_type': self.scaler_type,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'imputer': self.imputer,
            'feature_names': self.feature_names,
            'fitted': self.fitted
        }, filepath)

        logger.info(f"Preprocessor saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'MIPSPreprocessor':
        """
        Load preprocessor from disk.

        Args:
            filepath: Path to load the preprocessor from

        Returns:
            Loaded preprocessor
        """
        data = joblib.load(filepath)

        preprocessor = cls(scaler_type=data['scaler_type'])
        preprocessor.scaler = data['scaler']
        preprocessor.label_encoders = data['label_encoders']
        preprocessor.imputer = data['imputer']
        preprocessor.feature_names = data['feature_names']
        preprocessor.fitted = data['fitted']

        logger.info(f"Preprocessor loaded from {filepath}")

        return preprocessor


class OutlierDetector:
    """
    Detect and handle outliers in MIPS data.
    """

    @staticmethod
    def detect_iqr(data: pd.Series, multiplier: float = 1.5) -> pd.Series:
        """
        Detect outliers using IQR (Interquartile Range) method.

        Args:
            data: Series to check for outliers
            multiplier: IQR multiplier (typically 1.5 or 3.0)

        Returns:
            Boolean series indicating outliers
        """
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outliers = (data < lower_bound) | (data > upper_bound)

        logger.info(f"Detected {outliers.sum()} outliers using IQR method")

        return outliers

    @staticmethod
    def detect_zscore(data: pd.Series, threshold: float = 3.0) -> pd.Series:
        """
        Detect outliers using Z-score method.

        Args:
            data: Series to check for outliers
            threshold: Z-score threshold (typically 3.0)

        Returns:
            Boolean series indicating outliers
        """
        z_scores = np.abs((data - data.mean()) / data.std())
        outliers = z_scores > threshold

        logger.info(f"Detected {outliers.sum()} outliers using Z-score method")

        return outliers

    @staticmethod
    def handle_outliers(df: pd.DataFrame, columns: list,
                       method: str = 'clip', detection: str = 'iqr') -> pd.DataFrame:
        """
        Handle outliers in specified columns.

        Args:
            df: DataFrame containing data
            columns: List of column names to check for outliers
            method: How to handle outliers ('clip', 'remove', 'cap')
            detection: Detection method ('iqr' or 'zscore')

        Returns:
            DataFrame with outliers handled
        """
        df_copy = df.copy()

        for col in columns:
            if col not in df_copy.columns:
                continue

            if detection == 'iqr':
                outliers = OutlierDetector.detect_iqr(df_copy[col])
            else:
                outliers = OutlierDetector.detect_zscore(df_copy[col])

            if method == 'remove':
                df_copy = df_copy[~outliers]
            elif method == 'clip':
                # Clip to percentiles
                lower = df_copy[col].quantile(0.01)
                upper = df_copy[col].quantile(0.99)
                df_copy[col] = df_copy[col].clip(lower, upper)
            elif method == 'cap':
                # Cap at mean +/- 3*std
                mean = df_copy[col].mean()
                std = df_copy[col].std()
                lower = mean - 3 * std
                upper = mean + 3 * std
                df_copy[col] = df_copy[col].clip(lower, upper)

        return df_copy


def create_mips_categories(mips_values: pd.Series,
                          method: str = 'quantile',
                          n_bins: int = 3) -> Tuple[pd.Series, Dict]:
    """
    Create categorical labels from continuous MIPS values for classification.

    Args:
        mips_values: Series of MIPS consumption values
        method: Binning method ('quantile', 'uniform', 'custom')
        n_bins: Number of bins/categories

    Returns:
        Tuple of (categorical labels, bin information dict)
    """
    if method == 'quantile':
        # Equal-frequency binning
        labels = ['LOW', 'MEDIUM', 'HIGH'][:n_bins]
        categories = pd.qcut(mips_values, q=n_bins, labels=labels, duplicates='drop')
        bins_info = {
            'method': 'quantile',
            'n_bins': n_bins,
            'quantiles': mips_values.quantile([i/n_bins for i in range(n_bins+1)]).to_dict()
        }

    elif method == 'uniform':
        # Equal-width binning
        labels = ['LOW', 'MEDIUM', 'HIGH'][:n_bins]
        categories = pd.cut(mips_values, bins=n_bins, labels=labels)
        bins_info = {
            'method': 'uniform',
            'n_bins': n_bins,
            'min': float(mips_values.min()),
            'max': float(mips_values.max())
        }

    else:
        raise ValueError(f"Unknown method: {method}")

    logger.info(f"Created {n_bins} MIPS categories using {method} method")
    logger.info(f"Distribution: {categories.value_counts().to_dict()}")

    return categories, bins_info


if __name__ == "__main__":
    # Example usage
    from data_loader import MIPSDataLoader

    # Load sample data
    loader = MIPSDataLoader("data/sample/sample_mips_data.csv")
    data = loader.load_csv()

    # Split features and target
    X, y = loader.get_feature_target_split()

    # Create preprocessor
    print("\nPreprocessing data...")
    preprocessor = MIPSPreprocessor(scaler_type='standard')

    # Fit and transform
    X_train, X_test = loader.split_train_test(X, test_size=0.2)
    X_train_scaled = preprocessor.fit_transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    print(f"Original shape: {X_train.shape}")
    print(f"Scaled shape: {X_train_scaled.shape}")

    # Create categories for classification
    print("\nCreating MIPS categories...")
    y_categories, bins_info = create_mips_categories(y, method='quantile', n_bins=3)
    print(f"Categories: {y_categories.value_counts()}")
