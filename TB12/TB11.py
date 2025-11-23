import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io

# -----------------------------
# Seiten-Konfiguration
# -----------------------------
st.set_page_config(page_title="Bilanzanalyse", layout="wide")

# -----------------------------
# Navigation
# -----------------------------
st.sidebar.title("📌 Navigation")
seite = st.sidebar.radio(
    "Seite auswählen:",
    ["🏠 Startseite", "📊 Bilanzanalyse", "🔗 Linkliste", "🧩 Weitere Anwendung"]
)

# ---------------------------------------------------------------------------------
# FUNKTIONEN
# ---------------------------------------------------------------------------------

CSV_DATEI = "bilanzanalyse.csv"
PDF_DATEI = "bilanzanalyse.pdf"

jahre = ["Jahr 1", "Jahr 2"]
felder = ["AV", "UV", "EK", "LFK", "KFK"]

def berechne_kennzahlen(df):
    #spalte Gesamtvermögen wird initialisiert mit...
    df["Gesamtvermögen"] = df["AV"] + df["UV"]
    df["Anlagenintensität (%)"] = round(df["AV"] / df["Gesamtvermögen"] * 100, 2)
    df["Liquidität 3 (%)"] = round(df["UV"] / df["KFK"] * 100, 2)
    df["Working Capital"] = df["UV"] - df["KFK"]
    df["Anlagendeckung 2 (%)"] = round((df["EK"] + df["LFK"]) / df["AV"], 2)
    df["Verschuldungsgrad (%)"] = round((df["LFK"] + df["KFK"]) / df["EK"] * 100, 2)
    #wiedergabe Tabelle
    return df


# ---------------------------------------------------------------------------------
# 🏠 1) STARTSEITE
# ---------------------------------------------------------------------------------
if seite == "🏠 Startseite":
    st.title("🏠 Willkommen zur Analyse-App")
    st.write("""
    Diese Anwendung besteht aus mehreren Modulen:

    ### 📊 Bilanzanalyse  
    Erfasse Bilanzwerte für zwei Jahre, berechne Kennzahlen und exportiere alles als PDF.

    ### 🔗 Linkliste  
    Eine Sammlung nützlicher Links

    ### 🧩 Weitere Anwendung  
    Platzhalter, um später ein neues Tool zu integrieren.

    Nutze links die Navigation, um eine Seite auszuwählen.
    """)

# ---------------------------------------------------------------------------------
# 📊 2) BILANZANALYSE (dein bestehender Code)
# ---------------------------------------------------------------------------------
elif seite == "📊 Bilanzanalyse":

    st.title("📊 Bilanzanalyse für 2 Jahre")
    st.header("📥 Eingabe der Bilanzwerte")

    eingaben = []
    cols_header = st.columns(len(felder) + 1)
    cols_header[0].write("**Jahr**")

    for i, feld in enumerate(felder):
        cols_header[i + 1].write(f"**{feld}**")

    for jahr in jahre:
        cols = st.columns(len(felder) + 1)
        cols[0].write(jahr)

        werte = {}
        for i, feld in enumerate(felder):
            werte[feld] = cols[i+1].number_input(
                f"{jahr} - {feld}",
                label_visibility="collapsed",
                value=0.0
            )
        werte["Jahr"] = jahr
        eingaben.append(werte)

    df = pd.DataFrame(eingaben)

    st.subheader("🔢 Berechnete Kennzahlen")
    df = berechne_kennzahlen(df)

    if st.button("💾 CSV speichern"):
        df.to_csv(CSV_DATEI, index=False)
        st.success("CSV gespeichert!")

    st.write(df)

    # Diagramme
    st.header("📈 Diagramme anzeigen")
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    farben = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    for i, jahr in enumerate(jahre):
        werte = df.loc[df["Jahr"] == jahr, felder].iloc[0]
        axs[i].pie(werte, labels=felder, autopct='%1.1f%%',
                   startangle=90, colors=farben)
        axs[i].set_title(f"Bilanzstruktur {jahr}")

    st.pyplot(fig)

    # PDF Export
    st.header("📄 Export als PDF")
    if st.button("PDF erzeugen"):

        buffer = io.BytesIO()

        with PdfPages(buffer) as pdf:
            fig_table, ax = plt.subplots(figsize=(14, 5))
            ax.axis("off")
            table = ax.table(cellText=df.values,
                             colLabels=df.columns,
                             loc="center")
            table.scale(1.2, 1.3)
            pdf.savefig(fig_table)
            plt.close(fig_table)

            fig.set_size_inches(14, 5)
            pdf.savefig(fig)

        buffer.seek(0)

        st.download_button(
            label="📥 PDF herunterladen",
            data=buffer,
            file_name="Bilanzanalyse.pdf",
            mime="application/pdf"
        )

        st.success("PDF wurde erstellt!")

    # Sidebar-Formeln
    st.sidebar.title("📘 Kennzahlen Formeln")
    st.sidebar.write("""
    **Gesamtvermögen** = AV + UV  
    **Anlagenintensität (%)** = AV / Gesamtvermögen × 100  
    **Liquidität 3 (%)** = UV / KFK × 100  
    **Working Capital** = UV − KFK  
    **Anlagendeckung 2 (%)** = (EK + LFK) / AV  
    **Verschuldungsgrad (%)** = FK / EK × 100  
    """)

# ---------------------------------------------------------------------------------
# 🔗 3) LINKLISTE
# ---------------------------------------------------------------------------------
elif seite == "🔗 Linkliste":
    st.title("🔗 Nützliche Links")

    st.write("""
    Hier kannst du eine Liste hilfreicher Webseiten pflegen:
    """)

    links = {
        "Bundesanzeiger": "https://www.bundesanzeiger.de",
        "Statistisches Bundesamt": "https://www.destatis.de",
        "IFRS Standards": "https://www.ifrs.org",
        "Finanzlexikon": "https://www.finance-magazin.de"
    }
    
    #links.items() liefert ("Bundesanzeiger", "https://www.bundesanzeiger.de")
    #st.markdown() versteht Markdown-Syntax.,[Text](URL) ist gültiges Markdown für einen Hyperlink,
    #Streamlit rendert das im Browser → klickbarer Link.

    for name, url in links.items():
        #st.markdown(f"🔹 **[{name}]({url})**")
        #Ein f-String ist ein String, der mit einem f davor beginnt:
        #f"Text {variable}"
        #Alles, was du in geschweiften Klammern {} schreibst, wird durch den jeweiligen Wert ersetzt.
        # MarkDown:(URL)Die Adresse, zu der der Link führt,Die eckigen Klammern alleine definieren nur den Anzeigetext [Bundesanzeiger]  
        #c# string text = $"Hier ist ein Link: {name} ({url})";
        st.markdown(f"{name}: ,{url}")

# ---------------------------------------------------------------------------------
# 🧩 4) WEITERE ANWENDUNG (Platzhalter)
# ---------------------------------------------------------------------------------
elif seite == "🧩 Weitere Anwendung":
    st.title("🧩 Weitere Anwendung")
    st.write("""
    Hier kannst du später ein zusätzliches Tool integrieren.

    Beispiele:
    - Investitionsrechner  
    - Risikoanalyse  
    - Kennzahlensimulation  
    - Branchenvergleich  
    """)

    st.info("Dieser Bereich ist aktuell ein Platzhalter.")


