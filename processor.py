import pandas as pd
import io

def process_files(uploaded_files):
    MAX_FILES = 20
    if len(uploaded_files) > MAX_FILES:
        raise ValueError(f"Maximum {MAX_FILES} files allowed.")
    
    dataframes = []
    for file in uploaded_files:
        file.seek(0)  # Reset pointer
        df = pd.read_excel(io.BytesIO(file.read()))
        
        if df.empty:
            continue
            
        df.columns = df.columns.str.lower().str.strip()
        if "phone" not in df.columns or "score" not in df.columns:
            continue
        
        clean_df = df[["phone", "score"]].copy()
        if "name" in df:
            clean_df["name"] = df["name"].astype(str).str.strip().str.upper()
        clean_df["phone"] = clean_df["phone"].astype(str).str.strip()
        dataframes.append(clean_df)
    
    if not dataframes:
        raise ValueError("No valid data found.")
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    if "name" not in combined_df:
        combined_df["name"] = None
    
    result = combined_df.groupby("phone", as_index=False).agg({
        "name": "first",
        "score": "sum"
    }).sort_values("score", ascending=False)
    
    return result
