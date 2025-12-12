import pandas as pd
import numpy as np
from typing import Dict, Any

def analyze_dataset(file_path: str) -> Dict[str, Any]:
    """
    Reads a CSV file and returns a profile including:
    - schema: column names and types
    - summary: basic stats
    - correlation: correlation matrix
    - distributions: histograms and value counts for visualization
    """
    try:
        # file_view is file://... for local
        if file_path.startswith("file://"):
            actual_path = file_path.replace("file://", "")
            df = pd.read_csv(actual_path)
        else:
            raise ValueError("Only local file paths supported in this mode")

        # 1. Schema
        schema = {}
        for col in df.columns:
            schema[col] = str(df[col].dtype)

        # 2. Summary & Distributions
        summary = df.describe(include='all').to_dict()
        missing_counts = df.isnull().sum().to_dict()
        
        distributions = {}

        for col in df.columns:
            # Ensure missing count is in summary
            if col not in summary: summary[col] = {}
            summary[col]['missing_count'] = missing_counts.get(col, 0)

            # Distributions
            if pd.api.types.is_numeric_dtype(df[col]):
                # Histogram for numeric
                # Drop NaNs for histogram calculation
                series = df[col].dropna()
                if not series.empty:
                    hist, bin_edges = np.histogram(series, bins=10)
                    distributions[col] = {
                        "type": "numeric",
                        "bins": [
                            {"range": f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}", "count": int(hist[i])}
                            for i in range(len(hist))
                        ]
                    }
                else:
                    distributions[col] = {"type": "numeric", "bins": []}
            else:
                # Value Counts for categorical (Top 10)
                counts = df[col].value_counts().head(10).to_dict()
                distributions[col] = {
                    "type": "categorical",
                    "counts": [{"name": str(k), "value": int(v)} for k, v in counts.items()]
                }

        # Clean NaNs
        def clean_nans(d):
            new_d = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    new_d[k] = clean_nans(v)
                elif isinstance(v, list):
                    new_d[k] = [clean_nans(i) if isinstance(i, dict) else i for i in v]
                elif isinstance(v, (float, np.floating)) and np.isnan(v):
                    new_d[k] = None
                else:
                    new_d[k] = v
            return new_d
            
        summary = clean_nans(summary)
        distributions = clean_nans(distributions)

        # 3. Correlation (Numeric only)
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            corr = numeric_df.corr().replace({np.nan: None}).to_dict()
        else:
            corr = {}

        return {
            "schema": schema,
            "summary": summary,
            "correlation": corr,
            "distributions": distributions,
            "row_count": len(df),
            "column_count": len(df.columns)
        }

    except Exception as e:
        print(f"Error analyzing dataset: {e}")
        return {"error": str(e)}
