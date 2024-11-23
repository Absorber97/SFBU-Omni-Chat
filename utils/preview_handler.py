from typing import List, Dict
import pandas as pd

class PreviewHandler:
    @staticmethod
    def format_for_preview(data: List[Dict[str, str]], max_rows: int = 10) -> pd.DataFrame:
        """Format data for preview display"""
        if not data:
            return pd.DataFrame(columns=["prompt", "completion", "source", "section", "page"])
        
        # Convert to DataFrame for easy handling
        df = pd.DataFrame(data)
        
        # Ensure all required columns exist
        required_cols = ["prompt", "completion", "source", "section", "page"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        
        # Reorder columns
        df = df[required_cols]
        
        # Limit rows
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        return df 