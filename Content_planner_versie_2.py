import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Keuzeopties
status_opties = ["🔴 Idee", "🟡 In bewerking", "🟢 Klaar"]
media_status_opties = ["🔴 Nog maken", "🟡 Gekozen media", "🟢 Gekoppeld"]
platform_opties = ["Instagram", "TikTok", "Facebook"]

# Pagina-instellingen
st.set_page_config(page_title="Contentplanner", layout="wide")
st.title("📅 Visuele Contentplanner")

# DataFrame initiëren
if "content_df" not in st.session_state:
    st.session_state.content_df = pd.DataFrame(columns=[
        "📝 Titel", "📌 Status", "✍️ Caption", "🖼️ Media-status",
        "⏳ Deadline", "📆 Publicatiedatum", "📱 Platform", "✅ Geplaatst?", "📊 Resultaat"
    ])

# ➕ NIEUWE POST TOEVOEGEN
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

# ✏️ POST BEWERKEN (selectie + formulier in 1)
if not st.session_state.content_df.empty:
    with st.expander("✏️ Post bewerken"):
        titels = st.session_state.content_df["📝 Titel"].tolist()
        geselecteerde_titel = st.selectbox("Selecteer een post om te bewerken", titels)
        geselecteerde_index = st.session_state.content_df[
            st.session_state.content_df["📝 Titel"] == geselecteerde_titel
        ].index[0]
        rij = st.session_state.content_df.loc[geselecteerde_index]

        col1, col2 = st.columns(2)
        with col1:
            nieuwe_titel = st.text_input("Titel", value=rij["📝 Titel"], key="edit_titel")
            nieuwe_status = st.selectbox("Status", status_opties, index=status_opties.index(rij["📌 Status"]), key="edit_status")
            nieuwe_caption = st.text_area("Caption", value=rij["✍️ Caption"], key="edit_caption")
            nieuwe_media_status = st.selectbox("Media-status", media_status_opties, index=media_status_opties.index(rij["🖼️ Media-status"]), key="edit_media")
        with col2:
            nieuwe_deadline = st.date_input("Deadline", value=datetime.strptime(rij["⏳ Deadline"], "%Y-%m-%d"), key="edit_deadline")
            nieuwe_pub_datum = st.date_input("Publicatiedatum", value=datetime.strptime(rij["📆 Publicatiedatum"], "%Y-%m-%d"), key="edit_pubdatum")
            nieuwe_platform = st.selectbox("Platform", platform_opties, index=platform_opties.index(rij["📱 Platform"]), key="edit_platform")
            nieuwe_geplaatst = st.checkbox("Geplaatst?", value=(rij["✅ Geplaatst?"] == "✅ Ja"), key="edit_geplaatst")
            nieuwe_resultaat = st.text_input("Resultaat (optioneel)", value=rij["📊 Resultaat"], key="edit_resultaat")

        if st.button("💾 Update post"):
            st.session_state.content_df.loc[geselecteerde_index] = {
                "📝 Titel": nieuwe_titel,
                "📌 Status": nieuwe_status,
                "✍️ Caption": nieuwe_caption,
                "🖼️ Media-status": nieuwe_media_status,
                "⏳ Deadline": nieuwe_deadline.strftime("%Y-%m-%d"),
                "📆 Publicatiedatum": nieuwe_pub_datum.strftime("%Y-%m-%d"),
                "📱 Platform": nieuwe_platform,
                "✅ Geplaatst?": "✅ Ja" if nieuwe_geplaatst else "❌ Nee",
                "📊 Resultaat": nieuwe_resultaat
            }
            st.success("Post bijgewerkt!")

# 📊 PLANNINGSTABEL
st.dataframe(st.session_state.content_df, use_container_width=True)

# 📥 DOWNLOAD ALS EXCEL
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
