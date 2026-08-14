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


# ============================================================
# DATASET SUMMARY
# ============================================================

@tool
def dataset_summary(file_path: str) -> str:
    """
    Generate statistical summary of the dataset.
    """

    try:

        df = pd.read_csv(file_path)

        summary = df.describe(
            include="all"
        ).to_string()

        return summary

    except Exception as e:

        return (
            f"Error generating summary: {str(e)}"
        )


# ============================================================
# COLUMN INFORMATION
# ============================================================

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


# ============================================================
# CHURN RATE
# ============================================================

@tool
def calculate_churn_rate(file_path: str) -> str:
    """
    Calculate churn rate if the dataset contains a churn column.
    Supports 0/1 and True/False churn values.
    """

    try:

        df = pd.read_csv(file_path)

        if "churn" not in df.columns:

            return (
                "The dataset does not contain "
                "a 'churn' column."
            )

        churn_column = df["churn"]


        # ----------------------------------------------------
        # Numeric 0/1
        # ----------------------------------------------------

        if pd.api.types.is_numeric_dtype(
            churn_column
        ):

            churn_rate = (
                churn_column.mean()
                * 100
            )

            return (
                f"Customer churn rate is "
                f"{churn_rate:.2f}%."
            )


        # ----------------------------------------------------
        # Boolean
        # ----------------------------------------------------

        if churn_column.dtype == bool:

            churn_rate = (
                churn_column.mean()
                * 100
            )

            return (
                f"Customer churn rate is "
                f"{churn_rate:.2f}%."
            )


        # ----------------------------------------------------
        # Text values
        # ----------------------------------------------------

        values = (
            churn_column
            .astype(str)
            .str.lower()
            .str.strip()
        )

        positive_values = [
            "1",
            "true",
            "yes",
            "y",
            "churn",
            "churned"
        ]

        churned = values.isin(
            positive_values
        ).sum()

        total = len(values)

        if total == 0:

            return "The dataset is empty."

        churn_rate = (
            churned / total
        ) * 100

        return (
            f"Customer churn rate is "
            f"{churn_rate:.2f}%."
        )

    except Exception as e:

        return (
            f"Error calculating churn rate: {str(e)}"
        )


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

        return correlation.to_string()

    except Exception as e:

        return (
            f"Error calculating correlation: {str(e)}"
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
    Generate a visualization from a CSV dataset.

    Supported chart types:

    - bar
    - line
    - scatter
    - histogram
    - pie

    Returns a path to the generated PNG image.
    """

    try:

        # ====================================================
        # CHECK FILE
        # ====================================================

        if not os.path.exists(csv_path):

            return (
                f"CSV file not found: {csv_path}"
            )


        # ====================================================
        # LOAD DATA
        # ====================================================

        df = pd.read_csv(
            csv_path
        )


        # ====================================================
        # CHECK EMPTY DATASET
        # ====================================================

        if df.empty:

            return (
                "The CSV dataset is empty."
            )


        # ====================================================
        # CHECK X COLUMN
        # ====================================================

        if x_column not in df.columns:

            return (
                f"Column '{x_column}' "
                f"not found.\n\n"
                f"Available columns:\n"
                f"{list(df.columns)}"
            )


        # ====================================================
        # CHECK Y COLUMN
        # ====================================================

        if y_column:

            if y_column not in df.columns:

                return (
                    f"Column '{y_column}' "
                    f"not found.\n\n"
                    f"Available columns:\n"
                    f"{list(df.columns)}"
                )


        # ====================================================
        # CREATE CHART DIRECTORY
        # ====================================================

        os.makedirs(
            "charts",
            exist_ok=True
        )


        # ====================================================
        # UNIQUE CHART NAME
        # ====================================================

        chart_id = str(
            uuid.uuid4()
        )[:8]

        chart_path = os.path.join(
            "charts",
            f"chart_{chart_id}.png"
        )


        # ====================================================
        # NORMALIZE CHART TYPE
        # ====================================================

        chart_type = (
            chart_type
            .lower()
            .strip()
        )


        # ====================================================
        # CREATE FIGURE
        # ====================================================

        plt.figure(
            figsize=(10, 6)
        )


        # ====================================================
        # BAR CHART
        # ====================================================

        if chart_type == "bar":

            if not y_column:

                plt.close()

                return (
                    "Bar chart requires "
                    "x_column and y_column."
                )

            plt.bar(
                df[x_column].astype(str),
                df[y_column]
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                y_column
            )

            plt.title(
                f"{y_column} by {x_column}"
            )


        # ====================================================
        # LINE CHART
        # ====================================================

        elif chart_type == "line":

            if not y_column:

                plt.close()

                return (
                    "Line chart requires "
                    "x_column and y_column."
                )

            plt.plot(
                df[x_column],
                df[y_column],
                marker="o"
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                y_column
            )

            plt.title(
                f"{y_column} vs {x_column}"
            )


        # ====================================================
        # SCATTER PLOT
        # ====================================================

        elif chart_type == "scatter":

            if not y_column:

                plt.close()

                return (
                    "Scatter plot requires "
                    "x_column and y_column."
                )

            plt.scatter(
                df[x_column],
                df[y_column]
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                y_column
            )

            plt.title(
                f"{x_column} vs {y_column}"
            )


        # ====================================================
        # HISTOGRAM
        # ====================================================

        elif chart_type == "histogram":

            plt.hist(
                df[x_column].dropna(),
                bins=20
            )

            plt.xlabel(
                x_column
            )

            plt.ylabel(
                "Frequency"
            )

            plt.title(
                f"Distribution of {x_column}"
            )


        # ====================================================
        # PIE CHART
        # ====================================================

        elif chart_type == "pie":

            values = (
                df[x_column]
                .value_counts()
            )

            if values.empty:

                plt.close()

                return (
                    f"No data available "
                    f"for '{x_column}'."
                )

            plt.pie(
                values.values,
                labels=values.index,
                autopct="%1.1f%%"
            )

            plt.title(
                f"Distribution of {x_column}"
            )


        # ====================================================
        # INVALID CHART TYPE
        # ====================================================

        else:

            plt.close()

            return (
                "Unsupported chart type.\n\n"
                "Supported types:\n"
                "- bar\n"
                "- line\n"
                "- scatter\n"
                "- histogram\n"
                "- pie"
            )


        # ====================================================
        # FORMAT CHART
        # ====================================================

        if chart_type != "pie":

            plt.xticks(
                rotation=45,
                ha="right"
            )

        plt.tight_layout()


        # ====================================================
        # SAVE CHART
        # ====================================================

        plt.savefig(
            chart_path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()


        # ====================================================
        # RETURN SPECIAL MARKER
        # ====================================================

        return (
            f"CHART_GENERATED: {chart_path}"
        )


    except Exception as e:

        plt.close()

        return (
            f"Error generating chart: {str(e)}"
        )