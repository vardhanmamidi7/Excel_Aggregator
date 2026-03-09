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
    background: linear-gradient(160deg, #e0f0ff 0%, #ffffff 100%);
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1 {
    color: #0B3D91;
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    margin-bottom: 10px;
}

/* Description text */
.stMarkdown p {
    font-size: 18px;
    color: #1A1A1A;
    text-align: center;
}

/* Upload box */
[data-testid="stFileUploader"] {
    border: 3px dashed #0B3D91;
    padding: 25px;
    border-radius: 15px;
    background-color: #F0F8FF;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}

/* Process button */
.stButton > button {
    background: #0B3D91;
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    border-radius: 10px;
    padding: 12px 28px;
    border: none;
    box-shadow: 1px 3px 6px rgba(0,0,0,0.2);
    transition: 0.3s;
}

.stButton > button:hover {
    background: #082B66;
    transform: translateY(-2px);
}

/* Download button */
.stDownloadButton > button {
    background: #0B3D91;
    color: #FFFFFF;
    font-size: 17px;
    border-radius: 10px;
    padding: 10px 22px;
    border: none;
    box-shadow: 1px 2px 5px rgba(0,0,0,0.2);
    transition: 0.3s;
}

.stDownloadButton > button:hover {
    background: #082B66;
    transform: translateY(-1px);
}

/* Dashboard metrics */
.stMetric > div:first-child {
    background-color: #D9EBFF !important;
    color: #0B3D91 !important;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    font-weight: 700;
    box-shadow: 1px 2px 5px rgba(0,0,0,0.1);
}

/* Top scorers table */
.stTable {
    background-color: #F5F9FF !important;
    color: #0B3D91;
    border-radius: 10px !important;
    padding: 10px;
}

/* Full data table */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
}

/* Adjust text color in table */
[data-testid="stDataFrame"] th, 
[data-testid="stDataFrame"] td {
    color: #0B3D91;
    font-weight: 600;
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