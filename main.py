import streamlit as st
import pandas as pd
from processor import process_files
from io import BytesIO

# -------- SAFE CSS - Only title and buttons --------
st.markdown("""
<style>
/* Title styling only */
h1 {
    color: #1F4E79 !important;
    text-align: center !important;
    font-size: 2.5rem !important;
}

/* Button styling only */
.stButton > button {
    background-color: #1F4E79 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #163A5F !important;
}

/* Download button */
.stDownloadButton > button {
    background-color: #1F4E79 !important;
    color: white !important;
    border-radius: 8px !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: white !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Excel Score Aggregator")
st.markdown("*Upload up to 20 Excel files with phone and score columns*")

# File uploader
uploaded_files = st.file_uploader(
    "Choose Excel files (.xlsx, .xls)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    help="Phone and Score columns are required"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    if st.button("🚀 Process Files", use_container_width=True):
        with st.spinner("Processing files..."):
            try:
                result = process_files(uploaded_files)
                st.success(f"✅ Processed {len(result)} unique records!")

                # Prepare display
                display_df = result.copy()
                if "name" not in display_df.columns:
                    display_df["name"] = "N/A"
                
                display_df = display_df[["phone", "name", "score"]]
                display_df.insert(0, "rank", range(1, len(display_df) + 1))
                display_df.columns = ["🏆 Rank", "📱 Phone", "👤 Name", "⭐ Total Score"]

                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(display_df))
                with col2:
                    st.metric("Highest Score", f"{display_df['⭐ Total Score'].max():.0f}")
                with col3:
                    st.metric("Total Points", f"{display_df['⭐ Total Score'].sum():.0f}")

                # Top results
                st.subheader("🏅 Top Results")
                st.table(display_df.head(10))

                # Full table
                st.subheader("📋 All Results")
                st.dataframe(display_df, use_container_width=True)

                # Download
                buffer = BytesIO()
                display_df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                
                st.download_button(
                    label=f"⬇️ Download {len(display_df)} Records (Excel)",
                    data=buffer,
                    file_name=f"scores_{len(display_df)}_records.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
else:
    st.info("👆 Upload Excel files above")
