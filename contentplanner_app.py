import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Vooraf gedefinieerde keuzes
status_opties = ["🔴 Idee", "🟡 In bewerking", "🟢 Klaar"]
media_status_opties = ["🔴 Nog maken", "🟡 Gekozen media", "🟢 Gekoppeld"]
platform_opties = ["Instagram", "TikTok", "Facebook"]

st.set_page_config(page_title="Contentplanner", layout="wide")
st.title("📅 Visuele Contentplanner")

# ⏱️ DataFrame initiëren
if "content_df" not in st.session_state:
    st.session_state.content_df = pd.DataFrame(columns=[
        "📝 Titel", "📌 Status", "✍️ Caption", "🖼️ Media-status",
        "⏳ Deadline", "📆 Publicatiedatum", "📱 Platform", "✅ Geplaatst?", "📊 Resultaat"
    ])

# 🆕 Nieuwe rij toevoegen
with st.expander("➕ Nieuwe post toevoegen"):
    col1, col2 = st.columns(2)
    with col1:
        titel = st.text_input("Titel")
        status = st.selectbox("Status", status_opties)
        caption = st.text_area("Caption")
        media_status = st.selectbox("Media-status", media_status_opties)
    with col2:
        deadline = st.date_input("Deadline", value=datetime.today())
        pub_datum = st.date_input("Publicatiedatum", value=datetime.today())
        platform = st.selectbox("Platform", platform_opties)
        geplaatst = st.checkbox("Geplaatst?")
        resultaat = st.text_input("Resultaat (optioneel)")

    if st.button("✅ Voeg toe aan planning"):
        nieuwe_rij = {
            "📝 Titel": titel,
            "📌 Status": status,
            "✍️ Caption": caption,
            "🖼️ Media-status": media_status,
            "⏳ Deadline": deadline.strftime("%Y-%m-%d"),
            "📆 Publicatiedatum": pub_datum.strftime("%Y-%m-%d"),
            "📱 Platform": platform,
            "✅ Geplaatst?": "✅ Ja" if geplaatst else "❌ Nee",
            "📊 Resultaat": resultaat
        }
        st.session_state.content_df = pd.concat([
            st.session_state.content_df,
            pd.DataFrame([nieuwe_rij])
        ], ignore_index=True)
        st.success("Post toegevoegd!")

# 📋 Toon contentplanning
st.subheader("📋 Jouw contentplanning")
st.dataframe(st.session_state.content_df, use_container_width=True)

# 📥 Download als Excel
def create_excel_file(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Contentplanning")
    return output.getvalue()

excel_bytes = create_excel_file(st.session_state.content_df)
st.download_button(
    label="📥 Download als Excel",
    data=excel_bytes,
    file_name="contentplanner.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)