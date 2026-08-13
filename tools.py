import pandas as pd
from langchain_core.tools import tool




@tool
def load_csv(file_path: str) -> str:
    """
    Load a CSV file and return basic information about it.
    """

    try:
        df = pd.read_csv(file_path)

        result = f"""
Dataset loaded successfully.

Rows: {df.shape[0]}
Columns: {df.shape[1]}

Columns:
{list(df.columns)}

Data types:
{df.dtypes.to_string()}

Missing values:
{df.isnull().sum().to_string()}
"""

        return result

    except Exception as e:
        return f"Error loading CSV: {str(e)}"


@tool
def dataset_summary(file_path: str) -> str:
    """
    Generate statistical summary of numerical columns.
    """

    try:
        df = pd.read_csv(file_path)

        summary = df.describe(include="all").to_string()

        return summary

    except Exception as e:
        return f"Error generating summary: {str(e)}"


@tool
def get_column_info(file_path: str) -> str:
    """
    Return information about dataset columns.
    """

    try:
        df = pd.read_csv(file_path)

        result = []

        for column in df.columns:
            result.append(
                f"{column}: "
                f"dtype={df[column].dtype}, "
                f"missing={df[column].isnull().sum()}, "
                f"unique={df[column].nunique()}"
            )

        return "\n".join(result)

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def calculate_churn_rate(file_path: str) -> str:
    """
    Calculate churn rate if the dataset contains a churn column.
    """

    try:
        df = pd.read_csv(file_path)

        if "churn" not in df.columns:
            return "The dataset does not contain a 'churn' column."

        churn_column = df["churn"]

        churn_rate = churn_column.mean() * 100

        return f"Customer churn rate is {churn_rate:.2f}%."

    except Exception as e:
        return f"Error calculating churn rate: {str(e)}"


@tool
def get_correlation(file_path: str) -> str:
    """
    Calculate correlation between numerical variables.
    """

    try:
        df = pd.read_csv(file_path)

        numeric_df = df.select_dtypes(include="number")

        if numeric_df.empty:
            return "No numerical columns found."

        correlation = numeric_df.corr()

        return correlation.to_string()

    except Exception as e:
        return f"Error calculating correlation: {str(e)}"