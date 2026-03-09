import streamlit as st
import pandas as pd
from processor import process_files
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

st.title("Excel Score Aggregator")
st.markdown("**Upload up to 20 Excel files containing phone and score columns.** *Phone and Score are mandatory fields.*")

# File uploader
uploaded_files = st.file_uploader(
    "Choose Excel files",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    help="Supports .xlsx and .xls files up to 20 files"
)

if uploaded_files:
    st.info(f"📁 Found {len(uploaded_files)} file(s)")
    
    if st.button("🚀 Process Files", type="primary"):
        try:
            # Pass uploaded_files directly to processor
            result = process_files(uploaded_files)

            st.success("✅ Processing completed!")

            # Prepare display data
            display_df = result.copy()
            if "name" not in display_df.columns:
                display_df["name"] = None
            
            # Reorder columns
            display_df = display_df[["phone", "name", "score"]]
            
            # Add ranking
            display_df.insert(0, "rank", range(1, len(display_df) + 1))

            # Dashboard metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Unique Records", len(display_df))
            with col2:
                st.metric("🥇 Highest Score", f"{display_df['score'].max():.0f}")
            with col3:
                st.metric("📈 Total Score Sum", f"{display_df['score'].sum():.0f}")

            # Top scorers
            st.subheader("🏆 Top 10 Scorers")
            top10 = display_df.head(10)
            st.table(top10)

            # Full results
            st.subheader("📋 Complete Results")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Download Excel
            buffer = BytesIO()
            display_df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)

            col1, col2 = st.columns([3,1])
            with col2:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=buffer,
                    file_name=f"aggregated_scores_{len(display_df)}_records.xlsx",
                    mime="application/vnd.openpyxl.xlsx"
                )

        except ValueError as ve:
            st.error(f"❌ {ve}")
        except Exception as e:
            st.error(f"💥 Unexpected error: {str(e)}")
            st.exception(e)
else:
    st.info("👆 Please upload Excel files and click 'Process Files'")
