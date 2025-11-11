"""
Feature engineering module for z/OS MIPS prediction

Creates derived features from raw z/OS performance indicators.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSFeatureEngineering:
    """
    Feature engineering for z/OS MIPS prediction.

    Creates derived features from raw indicators to improve model performance.
    """

    def __init__(self):
        """Initialize feature engineer."""
        self.created_features = []

    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all feature engineering transformations.

        Args:
            df: DataFrame with raw features

        Returns:
            DataFrame with additional engineered features
        """
        df = df.copy()

        logger.info("Creating engineered features...")

        # Ratio features
        df = self.create_ratio_features(df)

        # Interaction features
        df = self.create_interaction_features(df)

        # Statistical features
        df = self.create_statistical_features(df)

        # Polynomial features for key indicators
        df = self.create_polynomial_features(df, degree=2)

        # Time-based features (if timestamp available)
        if 'timestamp' in df.columns:
            df = self.create_time_features(df)

        logger.info(f"Created {len(self.created_features)} new features")
        logger.info(f"Total features: {len(df.columns)}")

        return df

    def create_ratio_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create ratio features between MIPS indicators.

        Ratios can capture relative relationships between different time periods.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with ratio features added
        """
        df = df.copy()

        # Peak to 24H ratio (how much more during peak vs average)
        if 'MPTE' in df.columns and 'M24H' in df.columns:
            df['MPTE_to_M24H_ratio'] = df['MPTE'] / (df['M24H'] + 1e-8)
            self.created_features.append('MPTE_to_M24H_ratio')

        # Daytime to 24H ratio
        if 'MDIU' in df.columns and 'M24H' in df.columns:
            df['MDIU_to_M24H_ratio'] = df['MDIU'] / (df['M24H'] + 1e-8)
            self.created_features.append('MDIU_to_M24H_ratio')

        # Peak to Daytime ratio
        if 'MPTE' in df.columns and 'MDIU' in df.columns:
            df['MPTE_to_MDIU_ratio'] = df['MPTE'] / (df['MDIU'] + 1e-8)
            self.created_features.append('MPTE_to_MDIU_ratio')

        # Efficiency-weighted MIPS
        if 'EFF' in df.columns and 'M24H' in df.columns:
            df['M24H_weighted_by_EFF'] = df['M24H'] * df['EFF']
            self.created_features.append('M24H_weighted_by_EFF')

        if 'EFF' in df.columns and 'MDIU' in df.columns:
            df['MDIU_weighted_by_EFF'] = df['MDIU'] * df['EFF']
            self.created_features.append('MDIU_weighted_by_EFF')

        # Transaction rate efficiency
        if 'TXDIU' in df.columns and 'EFF' in df.columns:
            df['TXDIU_per_EFF'] = df['TXDIU'] / (df['EFF'] + 1e-8)
            self.created_features.append('TXDIU_per_EFF')

        return df

    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between key indicators.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with interaction features added
        """
        df = df.copy()

        # MIPS * Efficiency interactions
        if 'M24H' in df.columns and 'EFF' in df.columns:
            df['M24H_x_EFF'] = df['M24H'] * df['EFF']
            self.created_features.append('M24H_x_EFF')

        # MIPS * Transaction interactions
        if 'MDIU' in df.columns and 'TXDIU' in df.columns:
            df['MDIU_x_TXDIU'] = df['MDIU'] * df['TXDIU']
            self.created_features.append('MDIU_x_TXDIU')

        # Transaction * Time Value
        if 'TXDIU' in df.columns and 'TVDIU' in df.columns:
            df['TXDIU_x_TVDIU'] = df['TXDIU'] * df['TVDIU']
            self.created_features.append('TXDIU_x_TVDIU')

        # Three-way interaction: MIPS * Transaction * Efficiency
        if all(col in df.columns for col in ['MDIU', 'TXDIU', 'EFF']):
            df['MDIU_x_TXDIU_x_EFF'] = df['MDIU'] * df['TXDIU'] * df['EFF']
            self.created_features.append('MDIU_x_TXDIU_x_EFF')

        return df

    def create_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create statistical aggregate features across MIPS indicators.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with statistical features added
        """
        df = df.copy()

        mips_cols = [col for col in ['M24H', 'MDIU', 'MPTE'] if col in df.columns]

        if len(mips_cols) >= 2:
            # Mean MIPS across different time periods
            df['MIPS_mean'] = df[mips_cols].mean(axis=1)
            self.created_features.append('MIPS_mean')

            # Standard deviation of MIPS (variability)
            df['MIPS_std'] = df[mips_cols].std(axis=1)
            self.created_features.append('MIPS_std')

            # Max MIPS
            df['MIPS_max'] = df[mips_cols].max(axis=1)
            self.created_features.append('MIPS_max')

            # Min MIPS
            df['MIPS_min'] = df[mips_cols].min(axis=1)
            self.created_features.append('MIPS_min')

            # Range (max - min)
            df['MIPS_range'] = df['MIPS_max'] - df['MIPS_min']
            self.created_features.append('MIPS_range')

            # Coefficient of variation
            df['MIPS_cv'] = df['MIPS_std'] / (df['MIPS_mean'] + 1e-8)
            self.created_features.append('MIPS_cv')

        return df

    def create_polynomial_features(self, df: pd.DataFrame,
                                   degree: int = 2,
                                   columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create polynomial features for specified columns.

        Args:
            df: Input DataFrame
            degree: Polynomial degree
            columns: Columns to create polynomials for. If None, uses key MIPS indicators

        Returns:
            DataFrame with polynomial features added
        """
        df = df.copy()

        if columns is None:
            # Default to key indicators
            columns = [col for col in ['M24H', 'MDIU', 'MPTE', 'EFF'] if col in df.columns]

        for col in columns:
            if col in df.columns:
                for d in range(2, degree + 1):
                    new_col = f'{col}_pow{d}'
                    df[new_col] = df[col] ** d
                    self.created_features.append(new_col)

        return df

    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features from timestamp.

        Args:
            df: Input DataFrame with timestamp column

        Returns:
            DataFrame with time features added
        """
        if 'timestamp' not in df.columns:
            return df

        df = df.copy()

        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Cyclical time features (using sin/cos for periodicity)
        df['month_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.month / 12)
        self.created_features.extend(['month_sin', 'month_cos'])

        df['day_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.day / 31)
        df['day_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.day / 31)
        self.created_features.extend(['day_sin', 'day_cos'])

        df['dayofweek_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.dayofweek / 7)
        df['dayofweek_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.dayofweek / 7)
        self.created_features.extend(['dayofweek_sin', 'dayofweek_cos'])

        # Is end/start of month
        df['is_month_start'] = df['timestamp'].dt.is_month_start.astype(int)
        df['is_month_end'] = df['timestamp'].dt.is_month_end.astype(int)
        self.created_features.extend(['is_month_start', 'is_month_end'])

        return df

    def create_application_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features based on application characteristics.

        This includes aggregate statistics per application (if multiple records per app).

        Args:
            df: Input DataFrame with 'application' column

        Returns:
            DataFrame with application-based features
        """
        if 'application' not in df.columns:
            return df

        df = df.copy()

        # Calculate per-application statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Mean per application
            app_mean = df.groupby('application')[col].transform('mean')
            df[f'{col}_app_mean'] = app_mean
            self.created_features.append(f'{col}_app_mean')

            # Deviation from application mean
            df[f'{col}_dev_from_app_mean'] = df[col] - app_mean
            self.created_features.append(f'{col}_dev_from_app_mean')

        return df

    def select_top_features(self, df: pd.DataFrame, target: pd.Series,
                          n_features: int = 20, method: str = 'correlation') -> List[str]:
        """
        Select top N most important features.

        Args:
            df: DataFrame with features
            target: Target variable
            n_features: Number of features to select
            method: Selection method ('correlation', 'mutual_info')

        Returns:
            List of selected feature names
        """
        from sklearn.feature_selection import mutual_info_regression

        numeric_df = df.select_dtypes(include=[np.number])

        if method == 'correlation':
            # Calculate correlation with target
            correlations = numeric_df.corrwith(target).abs().sort_values(ascending=False)
            top_features = correlations.head(n_features).index.tolist()

        elif method == 'mutual_info':
            # Calculate mutual information
            mi_scores = mutual_info_regression(numeric_df, target)
            mi_series = pd.Series(mi_scores, index=numeric_df.columns).sort_values(ascending=False)
            top_features = mi_series.head(n_features).index.tolist()

        else:
            raise ValueError(f"Unknown method: {method}")

        logger.info(f"Selected top {n_features} features using {method}")

        return top_features


def create_lag_features(df: pd.DataFrame, columns: List[str],
                       lags: List[int] = [1, 7, 30],
                       group_col: Optional[str] = None) -> pd.DataFrame:
    """
    Create lag features for time series data.

    Args:
        df: Input DataFrame (should be sorted by time)
        columns: Columns to create lags for
        lags: List of lag periods
        group_col: Column to group by (e.g., 'application')

    Returns:
        DataFrame with lag features added
    """
    df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        for lag in lags:
            lag_col = f'{col}_lag{lag}'

            if group_col:
                df[lag_col] = df.groupby(group_col)[col].shift(lag)
            else:
                df[lag_col] = df[col].shift(lag)

    return df


def create_rolling_features(df: pd.DataFrame, columns: List[str],
                           windows: List[int] = [7, 30],
                           group_col: Optional[str] = None) -> pd.DataFrame:
    """
    Create rolling window features for time series data.

    Args:
        df: Input DataFrame (should be sorted by time)
        columns: Columns to create rolling features for
        windows: List of window sizes
        group_col: Column to group by (e.g., 'application')

    Returns:
        DataFrame with rolling features added
    """
    df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        for window in windows:
            if group_col:
                # Rolling mean
                df[f'{col}_rolling_mean_{window}'] = (
                    df.groupby(group_col)[col]
                    .transform(lambda x: x.rolling(window, min_periods=1).mean())
                )
                # Rolling std
                df[f'{col}_rolling_std_{window}'] = (
                    df.groupby(group_col)[col]
                    .transform(lambda x: x.rolling(window, min_periods=1).std())
                )
            else:
                df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window, min_periods=1).mean()
                df[f'{col}_rolling_std_{window}'] = df[col].rolling(window, min_periods=1).std()

    return df


if __name__ == "__main__":
    # Example usage
    from data_loader import MIPSDataLoader

    # Load sample data
    loader = MIPSDataLoader("data/sample/sample_mips_data.csv")
    data = loader.load_csv()

    print(f"Original features: {len(data.columns)}")
    print(data.columns.tolist())

    # Create feature engineer
    feature_eng = MIPSFeatureEngineering()

    # Create all features
    data_with_features = feature_eng.create_all_features(data)

    print(f"\nAfter feature engineering: {len(data_with_features.columns)}")
    print(f"New features created: {len(feature_eng.created_features)}")
    print("\nNew features:")
    for feat in feature_eng.created_features[:10]:
        print(f"  - {feat}")
