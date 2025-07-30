import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- Pagina-instellingen ---
st.set_page_config(page_title="Visuele Contentplanner", layout="wide")
st.title("📅 Visuele Contentplanner")

# --- Google Sheets verbinden via secrets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Herstel private_key-format (\n)
raw_secrets = st.secrets["gspread"]
secrets = dict(raw_secrets)
secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")

# Authoriseren
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
client = gspread.authorize(creds)
sheet = client.open("Contentplanner").sheet1

# Data ophalen
records = sheet.get_all_records()
df = pd.DataFrame(records)

# Session state setup
if "geselecteerde_titel" not in st.session_state:
    st.session_state.geselecteerde_titel = None

# Nieuwe post toevoegen
with st.expander("➕ Nieuwe post toevoegen"):
    with st.form("nieuwe_post"):
        titel = st.text_input("Titel")
        status = st.selectbox("Status", ["Idee", "In bewerking", "Klaar"])
        caption = st.text_area("Caption")
        media_status = st.selectbox("Media-status", ["Nog maken", "Gekozen media", "Gekoppeld"])
        deadline = st.date_input("Deadline")
        publicatie = st.date_input("Publicatiedatum")
        platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn"])
        geplaatst = st.checkbox("Geplaatst?")
        resultaat = st.text_input("Resultaat (optioneel)")

        submitted = st.form_submit_button("✅ Voeg toe aan planning")
        if submitted and titel.strip():
            sheet.append_row([
                titel, status, caption, media_status,
                deadline.strftime("%Y-%m-%d"), publicatie.strftime("%Y-%m-%d"),
                platform, "Ja" if geplaatst else "Nee", resultaat
            ])
            st.success("Nieuwe post toegevoegd!")
            st.experimental_rerun()

# Post bewerken/verwijderen
with st.expander("✏️ Post bewerken"):
    if df.empty:
        st.info("Er zijn nog geen posts toegevoegd.")
    else:
        titels = df["📝 Titel"].tolist() if "📝 Titel" in df.columns else df["Titel"].tolist()
        selectie = st.selectbox("Selecteer een post om te bewerken", titels)

        if selectie:
            post = df[df["📝 Titel"] == selectie].iloc[0] if "📝 Titel" in df.columns else df[df["Titel"] == selectie].iloc[0]

            nieuwe_titel = st.text_input("Titel", post.get("📝 Titel", post.get("Titel", "")))
            nieuwe_status = st.selectbox("Status", ["Idee", "In bewerking", "Klaar"], index=["Idee", "In bewerking", "Klaar"].index(post.get("📌 Status", post.get("Status"))))
            nieuwe_caption = st.text_area("Caption", post.get("✍️ Caption", post.get("Caption", "")))
            nieuwe_media = st.selectbox("Media-status", ["Nog maken", "Gekozen media", "Gekoppeld"], index=["Nog maken", "Gekozen media", "Gekoppeld"].index(post.get("🖼️ Media-status", post.get("Media-status"))))
            nieuwe_deadline = st.date_input("Deadline", datetime.strptime(post.get("⏳ Deadline", post.get("Deadline")), "%Y-%m-%d"))
            nieuwe_publicatie = st.date_input("Publicatiedatum", datetime.strptime(post.get("📆 Publicatiedatum", post.get("Publicatiedatum")), "%Y-%m-%d"))
            nieuwe_platform = st.selectbox("Platform", ["Instagram", "TikTok", "Facebook", "LinkedIn"], index=["Instagram", "TikTok", "Facebook", "LinkedIn"].index(post.get("📱 Platform", post.get("Platform"))))
            nieuwe_geplaatst = st.checkbox("Geplaatst?", value=(post.get("✅ Geplaatst?", post.get("Geplaatst?")) == "Ja"))
            nieuwe_resultaat = st.text_input("Resultaat (optioneel)", post.get("📊 Resultaat", post.get("Resultaat", "")))

            rij_index = df[df["📝 Titel"] == selectie].index[0] + 2 if "📝 Titel" in df.columns else df[df["Titel"] == selectie].index[0] + 2

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Update post"):
                    sheet.update(f"A{rij_index}:I{rij_index}", [[
                        nieuwe_titel, nieuwe_status, nieuwe_caption, nieuwe_media,
                        nieuwe_deadline.strftime("%Y-%m-%d"), nieuwe_publicatie.strftime("%Y-%m-%d"),
                        nieuwe_platform, "Ja" if nieuwe_geplaatst else "Nee", nieuwe_resultaat
                    ]])
                    st.success("Post bijgewerkt!")
                    st.experimental_rerun()

            with col2:
                if st.button("🗑️ Verwijder post"):
                    sheet.delete_rows(rij_index)
                    st.success("Post verwijderd.")
                    st.experimental_rerun()

# Kalenderoverzicht
st.subheader("📆 Overzicht")
if df.empty:
    st.write("Nog geen posts gepland.")
else:
    df.index = df.index + 1
    st.dataframe(df, use_container_width=True)

# Downloadknop
def convert_df_to_excel(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")

st.download_button("📥 Download als Excel", convert_df_to_excel(df), "contentplanner.csv", "text/csv")
