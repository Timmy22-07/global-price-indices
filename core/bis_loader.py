# core/bis_loader.py

import pandas as pd
from pathlib import Path

def load_bis_data(data_dir: Path = Path("data/raw/bis")) -> pd.DataFrame:
    """
    Loads and processes all BIS REER Excel files from the given directory.
    Returns a long-format DataFrame with clean structure.
    """
    # List all Excel files in the directory
    files = sorted(data_dir.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No Excel files found in {data_dir}")

    df_list = []
    for file in files:
        df = pd.read_excel(file)

        # Find date columns dynamically (typically start at col 8)
        non_date_cols = [col for col in df.columns if not isinstance(col, pd.Timestamp)]
        date_cols = [col for col in df.columns if isinstance(col, pd.Timestamp)]

        # Melt into long format
        df_melted = df.melt(
            id_vars=non_date_cols,
            value_vars=date_cols,
            var_name="Date",
            value_name="Value"
        )

        df_list.append(df_melted)

    # Combine all years
    full_df = pd.concat(df_list, ignore_index=True)

    # Clean column names for consistency
    full_df.columns = [col.strip().replace(" ", "_").lower() for col in full_df.columns]

    # Optional: convert date to string or keep as datetime depending on usage
    full_df["date"] = pd.to_datetime(full_df["date"], errors="coerce")

    return full_df


def get_unique_filter_values(df: pd.DataFrame, cols: list[str]) -> dict:
    """
    Returns a dictionary mapping column names to unique sorted values (including 'All').
    """
    options = {}
    for col in cols:
        unique_vals = df[col].dropna().unique().tolist()
        unique_vals = sorted(unique_vals)
        options[col] = ["All"] + unique_vals
    return options


# Exemple d'utilisation (test local uniquement)
if __name__ == "__main__":
    df = load_bis_data()
    filters = get_unique_filter_values(df, [
        "reference_area", "frequency", "type", "basket", "unit"
    ])
    print(df.head())
    print(filters)
