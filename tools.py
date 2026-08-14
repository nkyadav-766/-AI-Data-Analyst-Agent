import os
import uuid

import pandas as pd
import matplotlib.pyplot as plt

from langchain_core.tools import tool


# ============================================================
# LOAD CSV
# ============================================================

@tool
def load_csv(file_path: str) -> str:
    """
    Load a CSV file and return a clean dataset overview.
    """

    try:
        df = pd.read_csv(file_path)

        missing = int(df.isnull().sum().sum())

        return (
            f"Dataset loaded successfully.\n"
            f"Rows: {len(df)}\n"
            f"Columns: {len(df.columns)}\n"
            f"Total missing values: {missing}"
        )

    except Exception as e:
        return f"Error loading CSV: {e}"


# ============================================================
# DATASET SUMMARY
# ============================================================

@tool
def dataset_summary(file_path: str) -> str:
    """
    Return a clean statistical summary of the CSV.
    """

    try:
        df = pd.read_csv(file_path)

        summary = df.describe(include="all").transpose()

        summary = summary.reset_index()

        summary = summary.rename(
            columns={"index": "Column"}
        )

        return summary.to_json(
            orient="records"
        )

    except Exception as e:
        return f"Error generating summary: {e}"


# ============================================================
# COLUMN INFORMATION
# ============================================================

@tool
def get_column_info(file_path: str) -> str:
    """
    Return column names, data types, missing values and unique values.
    """

    try:

        df = pd.read_csv(file_path)

        data = []

        for column in df.columns:

            data.append(
                {
                    "Column": column,
                    "Data Type": str(df[column].dtype),
                    "Missing Values": int(
                        df[column].isnull().sum()
                    ),
                    "Unique Values": int(
                        df[column].nunique()
                    )
                }
            )

        return pd.DataFrame(data).to_json(
            orient="records"
        )

    except Exception as e:

        return f"Error getting column information: {e}"


# ============================================================
# MISSING VALUES
# ============================================================

@tool
def get_missing_values(file_path: str) -> str:
    """
    Return missing value information for every column.
    """

    try:

        df = pd.read_csv(file_path)

        data = []

        for column in df.columns:

            missing = int(
                df[column].isnull().sum()
            )

            percentage = (
                missing / len(df) * 100
            )

            data.append(
                {
                    "Column": column,
                    "Missing Values": missing,
                    "Missing %": round(
                        percentage,
                        2
                    )
                }
            )

        return pd.DataFrame(data).to_json(
            orient="records"
        )

    except Exception as e:

        return f"Error getting missing values: {e}"


# ============================================================
# CHURN RATE
# ============================================================

@tool
def calculate_churn_rate(file_path: str) -> str:
    """
    Calculate customer churn rate if a churn column exists.
    """

    try:

        df = pd.read_csv(file_path)

        churn_column = None

        for column in df.columns:

            if column.lower() == "churn":

                churn_column = column

                break

        if churn_column is None:

            return (
                "No churn column was found "
                "in this dataset."
            )

        churn_rate = (
            df[churn_column].mean() * 100
        )

        return (
            f"Customer churn rate: "
            f"{churn_rate:.2f}%"
        )

    except Exception as e:

        return f"Error calculating churn rate: {e}"


# ============================================================
# CORRELATION
# ============================================================

@tool
def get_correlation(file_path: str) -> str:
    """
    Calculate correlation between numerical variables.
    """

    try:

        df = pd.read_csv(file_path)

        numeric_df = df.select_dtypes(
            include="number"
        )

        if numeric_df.empty:

            return (
                "No numerical columns found."
            )

        correlation = numeric_df.corr()

        return correlation.to_json()

    except Exception as e:

        return f"Error calculating correlation: {e}"


# ============================================================
# CHART DIRECTORY
# ============================================================

def create_chart_directory():

    os.makedirs(
        "charts",
        exist_ok=True
    )


# ============================================================
# GENERATE CHART
# ============================================================

@tool
def generate_chart(
    csv_path: str,
    chart_type: str,
    x_column: str,
    y_column: str = ""
) -> str:
    """
    Generate a PNG chart from a CSV file.

    chart_type:
    histogram
    bar
    line
    scatter
    pie

    Returns:
    CHART_PATH:<path>
    """

    if not os.path.exists(csv_path):

        return (
            f"ERROR: CSV file not found: "
            f"{csv_path}"
        )

    try:

        df = pd.read_csv(csv_path)

    except Exception as e:

        return f"ERROR: {e}"

    if x_column not in df.columns:

        return (
            f"ERROR: Column '{x_column}' "
            f"not found."
        )

    if y_column and y_column not in df.columns:

        return (
            f"ERROR: Column '{y_column}' "
            f"not found."
        )

    create_chart_directory()

    chart_id = uuid.uuid4().hex[:10]

    chart_path = os.path.join(
        "charts",
        f"chart_{chart_id}.png"
    )

    chart_type = chart_type.lower().strip()

    plt.figure(
        figsize=(10, 6)
    )

    # ========================================================
    # HISTOGRAM
    # ========================================================

    if chart_type == "histogram":

        plt.hist(
            df[x_column].dropna(),
            bins=20
        )

        plt.xlabel(x_column)
        plt.ylabel("Frequency")

        title = (
            f"Distribution of {x_column}"
        )

    # ========================================================
    # BAR
    # ========================================================

    elif chart_type == "bar":

        if y_column:

            # Aggregate numeric values
            grouped = (
                df.groupby(x_column)[y_column]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(15)
            )

            plt.bar(
                grouped.index.astype(str),
                grouped.values
            )

            plt.ylabel(
                f"Average {y_column}"
            )

        else:

            counts = (
                df[x_column]
                .value_counts()
                .head(15)
            )

            plt.bar(
                counts.index.astype(str),
                counts.values
            )

            plt.ylabel("Count")

        plt.xlabel(x_column)

        title = (
            f"{x_column} - Bar Chart"
        )

    # ========================================================
    # LINE
    # ========================================================

    elif chart_type == "line":

        if not y_column:

            plt.close()

            return (
                "ERROR: Line chart requires "
                "x_column and y_column."
            )

        plt.plot(
            df[x_column],
            df[y_column],
            marker="o"
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)

        title = (
            f"{y_column} vs {x_column}"
        )

    # ========================================================
    # SCATTER
    # ========================================================

    elif chart_type == "scatter":

        if not y_column:

            plt.close()

            return (
                "ERROR: Scatter chart requires "
                "x_column and y_column."
            )

        plt.scatter(
            df[x_column],
            df[y_column]
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)

        title = (
            f"{y_column} vs {x_column}"
        )

    # ========================================================
    # PIE
    # ========================================================

    elif chart_type == "pie":

        values = (
            df[x_column]
            .value_counts()
            .head(10)
        )

        plt.pie(
            values.values,
            labels=values.index,
            autopct="%1.1f%%"
        )

        title = (
            f"{x_column} Distribution"
        )

    else:

        plt.close()

        return (
            "ERROR: Unsupported chart type. "
            "Use histogram, bar, line, "
            "scatter or pie."
        )

    plt.title(title)

    if chart_type != "pie":

        plt.xticks(
            rotation=45,
            ha="right"
        )

    plt.tight_layout()

    plt.savefig(
        chart_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return f"CHART_PATH:{chart_path}"