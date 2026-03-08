# 


import streamlit as st
import pandas as pd
from processor import process_files
import tempfile
from io import BytesIO


# -------- Clean Blue UI Styling --------
st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #F2F6FC;
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1 {
    color: #1F4E79;
    text-align: center;
    font-size: 44px;
    font-weight: 700;
}

/* Description text */
.stMarkdown p {
    font-size: 18px;
    color: #2C3E50;
    text-align: center;
}

/* Upload box */
[data-testid="stFileUploader"] {
    border: 2px dashed #1F4E79;
    padding: 20px;
    border-radius: 12px;
    background-color: #FFFFFF;
}

/* Process button */
.stButton > button {
    background-color: #1F4E79;
    color: white;
    font-size: 18px;
    border-radius: 8px;
    padding: 10px 25px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #163A5F;
}

/* Download button */
.stDownloadButton > button {
    background-color: #1F4E79;
    color: white;
    font-size: 17px;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
}

.stDownloadButton > button:hover {
    background-color: #163A5F;
}

/* Table styling */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)
# -------- End UI Styling --------


st.title("Excel Score Aggregator")

st.write("Upload up to 20 Excel files containing phone and score columns. Phone and Score are Mandatory Fields")

# Upload files
uploaded_files = st.file_uploader(
    "Upload Excel files",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:

    if len(uploaded_files) > 20:
        st.error("Maximum 20 files allowed")

    else:

        if st.button("Process Files"):

            file_paths = []

            # Save uploaded files temporarily
            for file in uploaded_files:
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(file.read())
                file_paths.append(temp.name)

            try:
                result = process_files(file_paths)

                st.success("Processing completed!")

                # Ensure name column exists
                if "name" not in result.columns:
                    result["name"] = None

                # Reorder columns
                result = result[["phone", "name", "score"]]

                # Sort by score (highest first)
                result = result.sort_values(by="score", ascending=False)

                # Add ranking column
                result.insert(0, "rank", range(1, len(result) + 1))

                # Dashboard metrics
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Records", len(result))

                with col2:
                    st.metric("Highest Score", result["score"].max())

                # Top 3 scorers
                st.subheader("Top 3 Scorers")
                top3 = result.head(3)
                st.table(top3[["rank", "name", "phone", "score"]])

                # Full result table
                st.subheader("All Results")
                st.dataframe(result, use_container_width=True)

                # Create Excel file in memory
                buffer = BytesIO()
                result.to_excel(buffer, index=False)
                buffer.seek(0)

                # Download button
                st.download_button(
                    label="Download Result as Excel",
                    data=buffer,
                    file_name="aggregated_scores.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(str(e))