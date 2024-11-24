from typing import List, Dict, Any, TypedDict
import pandas as pd

class Message(TypedDict):
    role: str
    content: str

class ChatItem(TypedDict):
    messages: List[Message]
    source: str
    section: str
    page: str

class PreviewHandler:
    @staticmethod
    def format_for_preview(data: List[Dict[str, Any]], max_rows: int = 10) -> pd.DataFrame:
        """Format data for preview display"""
        formatted_data = []
        
        for item in data:
            if "messages" in item:
                messages = item["messages"]
                # Extract user question and assistant response using type-safe dict access
                user_msg = next((msg.get("content", "") for msg in messages 
                               if msg.get("role") == "user"), "")
                assistant_msg = next((msg.get("content", "") for msg in messages 
                                    if msg.get("role") == "assistant"), "")
                
                formatted_data.append({
                    "prompt": user_msg,
                    "completion": assistant_msg,
                    "source": item.get("source", ""),
                    "section": item.get("section", ""),
                    "page": item.get("page", "")
                })
            else:
                # Handle old format
                formatted_data.append(item)
        
        # Convert to DataFrame with explicit column names
        df = pd.DataFrame(formatted_data, columns=[
            "prompt", "completion", "source", "section", "page"
        ])
        
        # Ensure all required columns exist
        required_cols = ["prompt", "completion", "source", "section", "page"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        
        # Limit rows
        if len(df) > max_rows:
            df = df.head(max_rows)
        
        return df 