from pathlib import Path
from typing import Any

import pandas as pd


def read_excel_file(file_path: str | Path) -> list[dict[str, Any]]:
    """
    Read the input Excel file and return each row as a dictionary.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Input Excel file not found: {path}"
        )

    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(
            f"Input file must be an Excel file (.xlsx or .xls), got: {path}"
        )

    dataframe = pd.read_excel(path)

    # Convert NaN/NaT values to None
    dataframe = dataframe.where(
        pd.notna(dataframe),
        None,
    )

    return dataframe.to_dict(orient="records")