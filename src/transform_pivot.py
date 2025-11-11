"""
Transform pivot-format z/OS data to long format for ML training.

This module handles the transformation of z/OS performance data from:
- Wide/pivot format (dates as columns)
- European decimal format (comma separator)
- Indicators as rows

To:
- Long format (one row per observation)
- Standard decimal format (period separator)
- Indicators as columns
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PivotTransformer:
    """
    Transform pivot-format z/OS data to long format.

    Expected input format:
        code_application | code_indicateur | 2022-04-01 | 2022-05-01 | ...
        DEV-CICS         | MDIU           | 0,2717     | 0,196      | ...
        DEV-CICS         | MPTE           | 0,3014     | 0,3047     | ...

    Output format:
        application | timestamp  | M24H | MDIU | MPTE | ... | MIPS_consumption
        DEV-CICS    | 2022-04-01 | 1.23 | 0.27 | 0.30 | ... | 1.23
    """

    def __init__(self):
        """Initialize transformer."""
        self.app_col = None
        self.ind_col = None
        self.date_cols = None

    def load_file(self, filepath: str) -> pd.DataFrame:
        """
        Load file with automatic format detection.

        Args:
            filepath: Path to input file (CSV, TSV, or Excel)

        Returns:
            Loaded DataFrame
        """
        filepath = Path(filepath)
        logger.info(f"Loading file: {filepath}")

        # Try Excel first
        if filepath.suffix in ['.xlsx', '.xls']:
            try:
                df = pd.read_excel(filepath)
                logger.info(f"Loaded Excel file: {df.shape}")
                return df
            except Exception as e:
                logger.warning(f"Could not load as Excel: {e}")

        # Try CSV with different separators and encodings
        for sep in ['\t', ',', ';', '|']:
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, sep=sep, encoding=encoding)
                    if len(df.columns) > 2:  # Must have at least 3 columns
                        logger.info(f"Loaded CSV: sep='{sep}', encoding='{encoding}', shape={df.shape}")
                        return df
                except:
                    continue

        raise ValueError(f"Could not load file: {filepath}. Try saving as CSV UTF-8 or Excel.")

    def fix_decimal_separator(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Convert comma decimal separator to period.

        Args:
            df: DataFrame to fix
            columns: Columns to convert

        Returns:
            DataFrame with fixed decimals
        """
        logger.info("Fixing decimal separators...")

        for col in columns:
            if col in df.columns:
                # Convert to string, replace comma with period, convert to numeric
                df[col] = df[col].astype(str).str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def unpivot_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Unpivot dates from columns to rows.

        Args:
            df: Pivot-format DataFrame

        Returns:
            Unpivoted DataFrame
        """
        logger.info("Unpivoting dates...")

        # Identify columns
        self.app_col = df.columns[0]
        self.ind_col = df.columns[1]
        self.date_cols = list(df.columns[2:])

        logger.info(f"Application column: {self.app_col}")
        logger.info(f"Indicator column: {self.ind_col}")
        logger.info(f"Date columns: {len(self.date_cols)} dates")

        # Fix decimals in date columns
        df = self.fix_decimal_separator(df, self.date_cols)

        # Melt from wide to long
        df_melted = df.melt(
            id_vars=[self.app_col, self.ind_col],
            value_vars=self.date_cols,
            var_name='timestamp',
            value_name='value'
        )

        logger.info(f"After unpivot: {len(df_melted):,} rows")

        return df_melted

    def pivot_indicators(self, df_melted: pd.DataFrame) -> pd.DataFrame:
        """
        Pivot indicators from rows to columns.

        Args:
            df_melted: Unpivoted DataFrame

        Returns:
            DataFrame with indicators as columns
        """
        logger.info("Pivoting indicators to columns...")

        # Pivot indicators to columns
        df_long = df_melted.pivot_table(
            index=[self.app_col, 'timestamp'],
            columns=self.ind_col,
            values='value',
            aggfunc='first'
        ).reset_index()

        # Rename application column
        df_long.rename(columns={self.app_col: 'application'}, inplace=True)

        # Remove multi-index from columns
        df_long.columns.name = None

        logger.info(f"After pivot: {df_long.shape}")
        logger.info(f"Columns: {list(df_long.columns)}")

        return df_long

    def create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create MIPS_consumption target variable.

        Args:
            df: DataFrame with indicator columns

        Returns:
            DataFrame with target added
        """
        logger.info("Creating target variable...")

        # Option 1: Use M24H (24-hour MIPS) as target
        if 'M24H' in df.columns:
            df['MIPS_consumption'] = df['M24H']
            logger.info("Using M24H as MIPS_consumption")

        # Option 2: Average of MDIU and MPTE
        elif 'MDIU' in df.columns and 'MPTE' in df.columns:
            df['MIPS_consumption'] = (df['MDIU'] + df['MPTE']) / 2
            logger.info("Calculated MIPS_consumption as average of MDIU and MPTE")

        # Option 3: Use first numeric column
        else:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df['MIPS_consumption'] = df[numeric_cols[0]]
                logger.info(f"Using {numeric_cols[0]} as MIPS_consumption")
            else:
                raise ValueError("No numeric columns found to create target")

        return df

    def ensure_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure all required columns exist.

        Args:
            df: DataFrame to check

        Returns:
            DataFrame with all required columns
        """
        logger.info("Ensuring required columns...")

        required_indicators = ['M24H', 'MDIU', 'MPTE', 'TXDIU', 'EFF', 'TVDIU']

        for col in required_indicators:
            if col not in df.columns:
                logger.warning(f"Missing {col} - filling with zeros")
                df[col] = 0.0

        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean transformed data.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning data...")

        initial_rows = len(df)

        # Remove rows with missing target
        df = df.dropna(subset=['MIPS_consumption'])
        logger.info(f"Removed {initial_rows - len(df)} rows with missing target")

        # Remove rows where all indicators are zero
        indicator_cols = ['M24H', 'MDIU', 'MPTE', 'TXDIU']
        available = [c for c in indicator_cols if c in df.columns]

        if available:
            before = len(df)
            df = df[df[available].sum(axis=1) > 0]
            logger.info(f"Removed {before - len(df)} rows with all zeros")

        # Convert timestamp to datetime
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        except:
            logger.warning("Could not convert timestamp to datetime")

        return df

    def reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reorder columns to standard format.

        Args:
            df: DataFrame to reorder

        Returns:
            DataFrame with reordered columns
        """
        standard_order = [
            'application', 'timestamp', 'M24H', 'MDIU', 'MPTE',
            'TXDIU', 'EFF', 'TVDIU', 'MIPS_consumption'
        ]

        # Keep only available columns in order
        available_cols = [c for c in standard_order if c in df.columns]

        # Add any extra columns not in standard order
        extra_cols = [c for c in df.columns if c not in standard_order]

        final_columns = available_cols + extra_cols

        return df[final_columns]

    def transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Complete transformation pipeline.

        Args:
            df_raw: Raw pivot-format DataFrame

        Returns:
            Transformed long-format DataFrame
        """
        logger.info("="*70)
        logger.info("Starting transformation pipeline")
        logger.info("="*70)

        # Unpivot dates
        df_melted = self.unpivot_dates(df_raw)

        # Pivot indicators
        df_long = self.pivot_indicators(df_melted)

        # Create target
        df_long = self.create_target(df_long)

        # Ensure required columns
        df_long = self.ensure_required_columns(df_long)

        # Clean data
        df_long = self.clean_data(df_long)

        # Reorder columns
        df_long = self.reorder_columns(df_long)

        logger.info("="*70)
        logger.info("Transformation complete!")
        logger.info(f"Final shape: {df_long.shape}")
        logger.info(f"Applications: {df_long['application'].nunique()}")
        logger.info(f"Date range: {df_long['timestamp'].min()} to {df_long['timestamp'].max()}")
        logger.info("="*70)

        return df_long

    def transform_file(self, input_path: str, output_path: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """
        Transform a file from pivot to long format.

        Args:
            input_path: Path to input file
            output_path: Path to save output (optional)

        Returns:
            Tuple of (transformed DataFrame, output path)
        """
        # Load
        df_raw = self.load_file(input_path)

        # Transform
        df_transformed = self.transform(df_raw)

        # Save
        if output_path is None:
            input_path_obj = Path(input_path)
            output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_transformed.csv")

        df_transformed.to_csv(output_path, index=False)
        logger.info(f"Saved transformed data to: {output_path}")

        return df_transformed, output_path


def transform_pivot_data(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convenience function to transform pivot data.

    Args:
        input_path: Path to input file (CSV, TSV, or Excel)
        output_path: Path to save output CSV (optional)

    Returns:
        Path to output file
    """
    transformer = PivotTransformer()
    _, output_path = transformer.transform_file(input_path, output_path)
    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transform_pivot.py <input_file> [output_file]")
        print("\nExample:")
        print("  python transform_pivot.py zos_data.csv")
        print("  python transform_pivot.py zos_data.xlsx transformed.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n🔄 Transforming {input_file}...\n")

    output = transform_pivot_data(input_file, output_file)

    print(f"\n✅ Transformation complete!")
    print(f"📁 Output: {output}")
    print(f"\n🚀 Ready for training with:")
    print(f"   python main.py train --data-path {output} --mode both")
