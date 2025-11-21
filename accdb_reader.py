#!/usr/bin/env python3
"""
Standalone .accdb (Microsoft Access) Database Reader
Extracts specified tables and exports them as CSV files using pandas DataFrames
Uses only Anaconda 3 Python libraries
"""

import pandas as pd
import pyodbc
from pathlib import Path
import os
import sys
import warnings


def read_accdb_tables(accdb_file_path, output_dir='.'):
    """
    Read Microsoft Access (.accdb) database and export specified tables as CSV files.
    
    Args:
        accdb_file_path (str): Path to the .accdb file
        output_dir (str): Directory to save CSV files (default: current directory)
        
    Returns:
        dict: Dictionary of pandas DataFrames with table names as keys
    """

    # List of tables to export - easily configurable
    tables_to_export = ['airport', 'rwy_end']

    # Validate input file
    accdb_path = Path(accdb_file_path)
    if not accdb_path.exists():
        raise FileNotFoundError(
            f"Access database file not found: {accdb_file_path}")

    if not accdb_path.suffix.lower() == '.accdb':
        raise ValueError(
            f"File must be a .accdb file, got: {accdb_path.suffix}")

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Dictionary to store DataFrames
    dataframes = {}

    try:
        # Suppress pandas UserWarning about pyodbc connections
        # This is expected behavior for Access databases
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="pandas only supports SQLAlchemy connectable.*",
                category=UserWarning)

            # Create connection string for Microsoft Access
            db_path = str(accdb_path.absolute())
            connection_string = (
                f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                f"DBQ={db_path};"
                f"ExtendedAnsiSQL=1;")

            print(f">>>Connecting to Access database: {accdb_path.name}")

            # Establish connection
            with pyodbc.connect(connection_string) as conn:
                print(">>>Connection established successfully")

                # Get list of all tables in the database
                cursor = conn.cursor()
                all_tables = [
                    row.table_name for row in cursor.tables(tableType='TABLE')
                ]
                # print(f"Available tables in database: {all_tables}")

                # Process each specified table
                for table_name in tables_to_export:
                    try:
                        
                        # disable printing every table name
                        # print(f"\nProcessing table: {table_name}")

                        # # Check if table exists
                        # if table_name not in all_tables:
                        #     print(
                        #         f"Warning: Table '{table_name}' not found in database"
                        #     )
                        #     continue

                        # Read table into pandas DataFrame (warning suppressed)
                        query = f"SELECT * FROM [{table_name}]"
                        df = pd.read_sql(query, conn)

                        # Store DataFrame with table name as key
                        dataframes[table_name] = df

                        # print(
                        #     f"  - Loaded {len(df)} rows, {len(df.columns)} columns"
                        # )
                        # print(f"  - Columns: {list(df.columns)}")

                        # Export to CSV
                        csv_filename = f"{table_name}.csv"
                        csv_path = output_path / csv_filename
                        df.to_csv(csv_path, index=False)
                        # print(f"  - db table '{table_name}' exported to: {csv_path}")

                    except Exception as e:
                        print(
                            f"Error processing table '{table_name}': {str(e)}")
                        continue

                # print(f"\nSuccessfully processed {len(dataframes)} tables")

                # Create master_list by merging airport and rwy_end on 'wac_innr'
                if 'airport' in dataframes and 'rwy_end' in dataframes:
                    # print("\nCreating master ICAO list...")  #" and rwy_end on 'wac_innr'..."
                    

                    airport_df = dataframes['airport']
                    rwy_end_df = dataframes['rwy_end']

                    # Check if 'wac_innr' column exists in both DataFrames
                    if 'wac_innr' in airport_df.columns and 'wac_innr' in rwy_end_df.columns:
                        # Merge DataFrames on 'wac_innr' column
                        master_list = pd.merge(airport_df,
                                               rwy_end_df,
                                               on='wac_innr',
                                               how='inner')

                        # Store master_list DataFrame
                        dataframes['master_list'] = master_list

                        # print(
                        #     f"  - Merged {len(master_list)} rows from {len(airport_df)} airports and {len(rwy_end_df)} runway ends"
                        # )
                        print(f">>>{len(master_list):,} runways available")
                        # print(
                        #     f"  - Master list columns: {len(master_list.columns)}"
                        # )

                        # Export master_list to CSV
                        master_csv_path = output_path / "master_list.csv"
                        master_list.to_csv(master_csv_path, index=False)
                        # print(f"  - Exported to: {master_csv_path}")
                    else:
                        missing_cols = []
                        if 'wac_innr' not in airport_df.columns:
                            missing_cols.append(
                                f"airport (has: {list(airport_df.columns)})")
                        if 'wac_innr' not in rwy_end_df.columns:
                            missing_cols.append(
                                f"rwy_end (has: {list(rwy_end_df.columns)})")
                        print(
                            f"  - Warning: 'wac_innr' column not found in: {', '.join(missing_cols)}"
                        )
                        print(f"  - Skipping master_list creation")
                else:
                    missing_tables = []
                    if 'airport' not in dataframes:
                        missing_tables.append('airport')
                    if 'rwy_end' not in dataframes:
                        missing_tables.append('rwy_end')
                    print(
                        f"  - Warning: Cannot create master_list - missing tables: {', '.join(missing_tables)}"
                    )

    except pyodbc.Error as e:
        print(f"Database connection error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Microsoft Access Database Engine is installed")
        print(
            "2. Check that the .accdb file is not open in another application")
        print("3. Verify file permissions")
        raise

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

    return dataframes


def main():
    """
    Main function for standalone execution
    """
    print("Microsoft Access (.accdb) Database Reader")
    print("=" * 50)

    # Example usage
    if len(sys.argv) > 1:
        accdb_file = sys.argv[1]
    else:
        # Look for .accdb files in current directory
        accdb_files = list(Path('.').glob('*.accdb'))

        if not accdb_files:
            print("No .accdb files found in current directory")
            print("Usage: python accdb_reader.py <path_to_accdb_file>")
            return

        accdb_file = accdb_files[0]
        print(f"Using found .accdb file: {accdb_file}")

    try:
        # Read tables and get DataFrames
        dataframes = read_accdb_tables(accdb_file)

        # Display summary
        print("\n" + "=" * 50)
        print("EXPORT SUMMARY")
        print("=" * 50)

        for table_name, df in dataframes.items():
            print(f"\nTable: {table_name}")
            print(f"  Shape: {df.shape}")
            print(f"  CSV: {table_name}.csv")

            # Show sample data
            if len(df) > 0:
                print(f"  Sample data:")
                print(
                    f"    {df.head(2).to_string().replace(chr(10), chr(10) + '    ')}"
                )

        print(f"\nAll CSV files saved to current directory")

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
