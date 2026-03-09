# 


import streamlit as st
import pandas as pd
from processor import process_files
import tempfile
from io import BytesIO


# -------- Clean Blue UI Styling --------
st.markdown("""
<style>
/* Header transparent */
header[data-testid="stHeader"] { background-color: transparent !important; }

/* App background */
.stApp { 
    background: linear-gradient(160deg, #e0f0ff 0%, #ffffff 100%); 
    font-family: 'Segoe UI', sans-serif; 
}

/* All main titles/headers - FORCE visible */
div.block-container h1, div.block-container h2, div.block-container h3 { 
    color: #0B3D91 !important; 
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4) !important;
}

/* Description */
div.block-container p { color: #1A1A1A !important; }

/* File uploader */
[data-testid="stFileUploader"] { 
    border: 3px dashed #0B3D91 !important; 
    background-color: rgba(255,255,255,0.95) !important; /* White bg */
}

/* UPLOADED FILE NAMES - Key fix */
.stFileUploaderFile, 
[data-testid="stFileUploader"] .file-name, 
[data-testid="stFileUploader"] span, 
[data-testid="stFileUploader"] div[title] {
    color: #1A1A1A !important; 
    font-weight: 600 !important;
    background-color: #F5F9FF !important;
    padding: 4px 8px !important;
    border-radius: 4px !important;
}

/* File delete buttons */
[data-testid="stFileUploaderDeleteBtn"], [data-testid="stbaseButton-secondary"] {
    color: #FF4444 !important;
    background: #FFF !important;
}

/* BUTTONS - EMERALD GREEN THEME */
.stButton > button, .stDownloadButton > button {
    background: #10B981 !important; /* Emerald green */
    color: #FFFFFF !important;
    font-size: 18px;
    font-weight: 700;
    border-radius: 10px;
    padding: 12px 28px;
    border: none;
    box-shadow: 1px 3px 6px rgba(16, 185, 129, 0.3);
    transition: 0.3s;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background: #059669 !important; /* Darker emerald */
    transform: translateY(-2px);
    box-shadow: 1px 4px 8px rgba(16, 185, 129, 0.4);
}

/* METRICS (Top 3 Scorers) */
[data-testid="stMetric"] { 
    background: #D9EBFF !important; 
    border-radius: 12px; 
    padding: 15px; 
}
[data-testid="stMetric"] * { 
    color: #0B3D91 !important; 
    font-weight: 700 !important; 
}

/* TABLES (All results, Top scorers table) */
.element-container [data-testid="stDataFrame"],
.stTable, [data-testid="stDataFrame"] {
    background: #FFFFFF !important; 
    border-radius: 12px; 
    padding: 15px; 
    box-shadow: 1px 2px 8px rgba(0,0,0,0.1);
}

.element-container th, .element-container td,
[data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td,
.stTable th, .stTable td {
    color: #0B3D91 !important; 
    background: #F5F9FF !important; 
    font-weight: 600 !important;
}

/* Safety net: ALL text in main app */
div.block-container, div.element-container {
    color: #1A1A1A !important;
}
div.block-container * { text-shadow: none !important; }
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