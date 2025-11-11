"""
Data loading module for z/OS MIPS prediction

This module handles loading of historical z/OS performance data from various sources.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIPSDataLoader:
    """
    Load and manage z/OS MIPS consumption data.

    Expected data format:
    - application: Application name/ID
    - timestamp: Date/time of measurement
    - M24H: MIPS 24 hours
    - MDIU: MIPS Diurne (daytime)
    - MPTE: MIPS Pointe (peak period)
    - TXDIU: Rate DIU (x1000)
    - EFF: Efficiency
    - TVDIU: Time Value DIU
    - MIPS_consumption: Target variable (actual MIPS consumption)
    """

    REQUIRED_COLUMNS = ['application', 'M24H', 'MDIU', 'MPTE', 'TXDIU', 'EFF', 'TVDIU']
    TARGET_COLUMN = 'MIPS_consumption'

    def __init__(self, data_path: str):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the data directory or CSV file
        """
        self.data_path = Path(data_path)
        self.data = None

    def load_csv(self, filename: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Args:
            filename: Name of the CSV file. If None, loads from data_path directly.

        Returns:
            DataFrame containing the loaded data
        """
        if filename:
            filepath = self.data_path / filename
        else:
            filepath = self.data_path

        logger.info(f"Loading data from {filepath}")

        try:
            self.data = pd.read_csv(filepath)
            logger.info(f"Loaded {len(self.data)} records")
            self._validate_columns()
            return self.data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def load_multiple_csvs(self, pattern: str = "*.csv") -> pd.DataFrame:
        """
        Load and concatenate multiple CSV files from a directory.

        Args:
            pattern: Glob pattern to match CSV files

        Returns:
            DataFrame containing all loaded data
        """
        csv_files = list(self.data_path.glob(pattern))

        if not csv_files:
            raise FileNotFoundError(f"No CSV files found matching pattern: {pattern}")

        logger.info(f"Found {len(csv_files)} CSV files to load")

        dataframes = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                dataframes.append(df)
                logger.info(f"Loaded {file.name}: {len(df)} records")
            except Exception as e:
                logger.warning(f"Error loading {file.name}: {str(e)}")

        self.data = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Total records loaded: {len(self.data)}")
        self._validate_columns()

        return self.data

    def _validate_columns(self):
        """Validate that required columns exist in the data."""
        missing_cols = set(self.REQUIRED_COLUMNS) - set(self.data.columns)

        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}")
            logger.info(f"Available columns: {list(self.data.columns)}")

        if self.TARGET_COLUMN not in self.data.columns:
            logger.warning(f"Target column '{self.TARGET_COLUMN}' not found. "
                         f"This is expected for prediction data.")

    def get_data_info(self) -> dict:
        """
        Get summary information about the loaded data.

        Returns:
            Dictionary containing data statistics
        """
        if self.data is None:
            return {"error": "No data loaded"}

        info = {
            "n_records": len(self.data),
            "n_features": len(self.data.columns),
            "columns": list(self.data.columns),
            "n_applications": self.data['application'].nunique() if 'application' in self.data.columns else 0,
            "date_range": None,
            "missing_values": self.data.isnull().sum().to_dict(),
            "memory_usage_mb": self.data.memory_usage(deep=True).sum() / 1024**2
        }

        # Add date range if timestamp column exists
        if 'timestamp' in self.data.columns:
            try:
                self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
                info["date_range"] = {
                    "start": str(self.data['timestamp'].min()),
                    "end": str(self.data['timestamp'].max())
                }
            except:
                pass

        return info

    def split_train_test(self, test_size: float = 0.2,
                        random_state: int = 42,
                        time_based: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into training and testing sets.

        Args:
            test_size: Proportion of data to use for testing
            random_state: Random seed for reproducibility
            time_based: If True, split based on time (most recent data for test)

        Returns:
            Tuple of (train_data, test_data)
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        if time_based and 'timestamp' in self.data.columns:
            # Sort by timestamp and split
            sorted_data = self.data.sort_values('timestamp')
            split_idx = int(len(sorted_data) * (1 - test_size))
            train_data = sorted_data.iloc[:split_idx].copy()
            test_data = sorted_data.iloc[split_idx:].copy()
            logger.info(f"Time-based split: {len(train_data)} train, {len(test_data)} test")
        else:
            # Random split
            from sklearn.model_selection import train_test_split
            train_data, test_data = train_test_split(
                self.data, test_size=test_size, random_state=random_state
            )
            logger.info(f"Random split: {len(train_data)} train, {len(test_data)} test")

        return train_data, test_data

    def get_feature_target_split(self, df: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Split dataframe into features (X) and target (y).

        Args:
            df: DataFrame to split. If None, uses self.data

        Returns:
            Tuple of (X, y) where X contains features and y contains target
        """
        if df is None:
            df = self.data

        if df is None:
            raise ValueError("No data available")

        if self.TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{self.TARGET_COLUMN}' not found")

        # Features are all columns except target
        feature_cols = [col for col in df.columns if col != self.TARGET_COLUMN]

        X = df[feature_cols].copy()
        y = df[self.TARGET_COLUMN].copy()

        return X, y


def create_sample_data(output_path: str, n_samples: int = 1000,
                      n_apps: int = 50, random_state: int = 42) -> pd.DataFrame:
    """
    Create sample z/OS MIPS data for testing and demonstration.

    Args:
        output_path: Path to save the sample data CSV
        n_samples: Number of sample records to generate
        n_apps: Number of unique applications
        random_state: Random seed for reproducibility

    Returns:
        DataFrame containing the sample data
    """
    np.random.seed(random_state)

    # Generate date range (3 years of data)
    start_date = pd.Timestamp('2022-01-01')
    dates = pd.date_range(start=start_date, periods=n_samples, freq='D')

    # Generate application names
    apps = [f"APP_{i:03d}" for i in range(1, n_apps + 1)]

    data = {
        'application': np.random.choice(apps, size=n_samples),
        'timestamp': dates,
        'M24H': np.random.uniform(800, 2000, n_samples),
        'MDIU': np.random.uniform(600, 1500, n_samples),
        'MPTE': np.random.uniform(1000, 2500, n_samples),
        'TXDIU': np.random.uniform(30, 100, n_samples),
        'EFF': np.random.uniform(0.7, 0.99, n_samples),
        'TVDIU': np.random.uniform(50, 200, n_samples),
    }

    df = pd.DataFrame(data)

    # Generate target MIPS_consumption as a function of features (with noise)
    # MIPS consumption is correlated with the indicators
    df['MIPS_consumption'] = (
        0.4 * df['M24H'] +
        0.3 * df['MDIU'] +
        0.2 * df['MPTE'] +
        0.1 * df['TXDIU'] * 10 +
        np.random.normal(0, 50, n_samples)  # Add noise
    )

    # Ensure no negative values
    df['MIPS_consumption'] = df['MIPS_consumption'].clip(lower=0)

    # Save to CSV
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Sample data saved to {output_path}")

    return df


if __name__ == "__main__":
    # Example usage
    sample_path = "data/sample/sample_mips_data.csv"

    # Create sample data
    print("Creating sample data...")
    sample_df = create_sample_data(sample_path, n_samples=1000)

    # Load data
    print("\nLoading data...")
    loader = MIPSDataLoader(sample_path)
    data = loader.load_csv()

    # Get data info
    print("\nData Info:")
    info = loader.get_data_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Split data
    print("\nSplitting data...")
    train_df, test_df = loader.split_train_test(test_size=0.2)
    print(f"Train size: {len(train_df)}, Test size: {len(test_df)}")
