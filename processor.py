import pandas as pd

MAX_FILES = 20


def process_files(file_paths):

    # limit number of files
    if len(file_paths) > MAX_FILES:
        raise ValueError(f"Maximum {MAX_FILES} files allowed.")

    dataframes = []

    for file in file_paths:
        try:
            df = pd.read_excel(file)

            # skip empty sheets
            if df.empty:
                print(f"Skipping {file} (empty file)")
                continue

            # normalize column names
            df.columns = df.columns.str.lower().str.strip()

            # check required columns
            if "phone" not in df.columns or "score" not in df.columns:
                print(f"Skipping {file} (missing phone or score column)")
                continue

            # keep only required columns
            clean_df = df[["phone", "score"]].copy()

            # add name if exists
            if "name" in df.columns:
                clean_df["name"] = df["name"]
            else:
                clean_df["name"] = None

            # normalize phone
            clean_df["phone"] = clean_df["phone"].astype(str).str.strip()

            # normalize name
            clean_df["name"] = (
                clean_df["name"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            dataframes.append(clean_df)

        except Exception as e:
            print(f"Error reading {file}: {e}")

    # if no valid data found
    if not dataframes:
        raise ValueError("No valid data found in uploaded files.")

    # combine all sheets
    combined_df = pd.concat(dataframes, ignore_index=True)

    # aggregate scores by phone
    result = (
        combined_df
        .groupby("phone", as_index=False)
        .agg({
            "name": "first",
            "score": "sum"
        })
    )

    # sort by highest score
    result = result.sort_values(by="score", ascending=False)

    return result