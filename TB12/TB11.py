import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from abc import ABC, abstractmethod
import numpy as np
import yfinance as yf
from datetime import datetime
import time
from streamlit.experimental_rerun import st_autorefresh

# ---------------------------------------------------
# Page-Basis-Klasse
# ---------------------------------------------------
class Page(ABC):
    @abstractmethod
    def render(self):
        pass

# ---------------------------------------------------
# Kennzahlen berechnen
# ---------------------------------------------------
def berechne_kennzahlen(df):
    df["Gesamtvermögen"] = df["AV"] + df["UV"]
    df["Anlagenintensität (%)"] = round(df["AV"] / df["Gesamtvermögen"] * 100, 2)
    df["Liquidität 3 (%)"] = round(df["UV"] / df["KFK"] * 100, 2)
    df["Working Capital"] = df["UV"] - df["KFK"]
    df["Anlagendeckung 2 (%)"] = round((df["EK"] + df["LFK"]) / df["AV"], 2)
    df["Verschuldungsgrad (%)"] = round((df["LFK"] + df["KFK"]) / df["EK"] * 100, 2)
    return df

# ---------------------------------------------------
# Seiten-Klassen
# ---------------------------------------------------
class Startseite(Page):
    def render(self):
        st.title("🏠 Willkommen zur Analyse-App")
        st.write("""
        Diese Anwendung besteht aus mehreren Modulen:

        ### 📊 Bilanzanalyse  
        Bilanzwerte für zwei Jahre, Kennzahlenberechnung und Export als PDF.

        ### 🔗 Linkliste  
        Eine Sammlung nützlicher Links.

        ### 📈 Indizes  
        Übersicht ausgewählter Indizes.
        
        ### ⓘ Impressum 
        Impressum und Haftungsausschluss
        """)

class Bilanzanalyse(Page):
    def render(self):
        st.title("📊 Bilanzanalyse für 2 Jahre")
        st.header("📥 Eingabe der Bilanzwerte")

        jahre = ["Jahr 1", "Jahr 2"]
        felder = ["AV", "UV", "EK", "LFK", "KFK"]

        header_cols = st.columns(6)
        header_cols[0].write("**Jahr**")
        for i, feld in enumerate(felder, 1):
            header_cols[i].write(f"**{feld}**")

        eingaben = []

        for i, jahr in enumerate(jahre, 1):
            row = st.columns(6)
            row[0].write(jahr)
            werte = {"Jahr": jahr}
            for j, feld in enumerate(felder, 1):
                werte[feld] = row[j].number_input(f"{jahr}-{feld}", value=0.0, label_visibility="collapsed")
            eingaben.append(werte)

        df = pd.DataFrame(eingaben)
        st.subheader("📋 Eingabedaten")
        st.write(df)

        st.subheader("🔢 Berechnete Kennzahlen")
        df = berechne_kennzahlen(df)
        st.write(df)

        # CSV Export
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.download_button(
            label="📥 CSV herunterladen",
            data=csv_buffer.getvalue(),
            file_name="bilanzanalyse.csv",
            mime="text/csv"
        )

        # Balkendiagramm
        x = np.arange(len(felder))
        breite = 0.35
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - breite/2, df.loc[df["Jahr"] == "Jahr 1", felder].values[0], width=breite, color='red', label='Jahr 1')
        ax.bar(x + breite/2, df.loc[df["Jahr"] == "Jahr 2", felder].values[0], width=breite, color='blue', label='Jahr 2')
        ax.set_xticks(x)
        ax.set_xticklabels(felder)
        ax.set_ylabel("Wert")
        ax.set_title("Bilanzpositionen Jahr 1 vs Jahr 2")
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

        # PDF Export
        st.header("📄 Export als PDF")
        if st.button("PDF erzeugen"):
            buffer = io.BytesIO()
            with PdfPages(buffer) as pdf:
                # Tabelle
                fig_table, ax_table = plt.subplots(figsize=(14,5))
                ax_table.axis("off")
                table = ax_table.table(cellText=df.values, colLabels=df.columns, loc="center")
                table.scale(1.2, 1.3)
                pdf.savefig(fig_table)
                plt.close(fig_table)

                # Diagramm
                fig.set_size_inches(14,5)
                pdf.savefig(fig)

            buffer.seek(0)
            st.download_button(
                label="📥 PDF herunterladen",
                data=buffer,
                file_name="Bilanzanalyse.pdf",
                mime="application/pdf"
            )
            st.success("PDF steht nun zum Download bereit!")

        # Sidebar Formeln
        st.sidebar.title("📘 Kennzahlen Formeln")
        st.sidebar.write("""
        **Gesamtvermögen** = AV + UV  
        **Anlagenintensität (%)** = AV / Gesamtvermögen × 100  
        **Liquidität 3 (%)** = UV / KFK × 100  
        **Working Capital** = UV − KFK  
        **Anlagendeckung 2 (%)** = (EK + LFK) / AV  
        **Verschuldungsgrad (%)** = (LFK + KFK) / EK × 100  
        """)

class Linkliste(Page):
    def render(self):
        st.title("🔗 Nützliche Links")
        links = {
            "YoutubeKanal Michael Thomas": "https://m.youtube.com/channel/UC11vJSbmGWmNe0qJhtTu9hA",
            "GitHub Michael Thomas":"https://github.com/Mitho33",
            "Unternehmensregister": "https://www.unternehmensregister.de/de",
            "Bundesanzeiger": "https://www.bundesanzeiger.de",
            "Statistisches Bundesamt": "https://www.destatis.de",            
            "Finanzlexikon": "https://www.finance-magazin.de"
        }
        for name, url in links.items():
            st.markdown(f"🔹 **[{name}]({url})**")

class Indizes(Page):
    def render(self):
        st.title("🧩 Indizes")   
        st.write("Automatische Aktualisierung alle 30 Sekunden")

        # -----------------------------
        # Session State initialisieren
        # -----------------------------
        if "zeiten" not in st.session_state:
            st.session_state.zeiten = []
        if "dax" not in st.session_state:
            st.session_state.dax = []
        if "dow" not in st.session_state:
            st.session_state.dow = []
        if "shanghai" not in st.session_state:
            st.session_state.shanghai = []

        # --------------------------------------
        # Funktion zum Abrufen der Kursdaten
        # --------------------------------------
        def get_index_value(ticker):
            try:
                return yf.Ticker(ticker).info.get("regularMarketPrice", None)
            except:
                return None

        # --------------------------------------
        # Neue Werte abrufen
        # --------------------------------------
        now = datetime.now().strftime("%H:%M:%S")
        dax = get_index_value("^GDAXI")
        dow = get_index_value("^DJI")
        shanghai = get_index_value("000001.SS")

        if dax and dow and shanghai:
            st.session_state.zeiten.append(now)
            st.session_state.dax.append(dax)
            st.session_state.dow.append(dow)
            st.session_state.shanghai.append(shanghai)

        # nur die letzten 50 Werte behalten
        zeiten = st.session_state.zeiten[-50:]
        dax = st.session_state.dax[-50:]
        dow = st.session_state.dow[-50:]
        shanghai = st.session_state.shanghai[-50:]

        # -----------------------------
        # Layout: 1 Zeile, 3 Spalten
        # -----------------------------
        col1, col2, col3 = st.columns(3)

        # -----------------------------
        # Diagramme
        # -----------------------------
        def plot_line(x, y, title, color):
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(x, y, marker="o", color=color)
            ax.set_title(title)
            ax.set_xlabel("Zeit")
            ax.set_ylabel("Indexstand")
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col1:
            plot_line(zeiten, dax, "DAX", "blue")
        with col2:
            plot_line(zeiten, dow, "Dow Jones", "green")
        with col3:
            plot_line(zeiten, shanghai, "Shanghai Composite", "red")

        # -----------------------------
        # Automatisches Refresh alle 30 Sekunden
        # -----------------------------
        st_autorefresh(interval=30 * 1000, key="refresh")  # 30 Sekunden

class Impressum(Page):
    def render(self):
        st.title("ⓘ Impressum")
        st.write("""
        Angaben gemäß § 5 TMG:  

        Michael Thomas  
        In der Beek 87  
        D-42113 Wuppertal  

        E-Mail: mt.com@web.de  

        Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:

        Michael Thomas  
        In der Beek 87  
        D-42113 Wuppertal    

        Haftungsausschluss
        """)

# ---------------------------------------------------
# Page Factory
# ---------------------------------------------------
class PageFactory:
    _pages = {
        "🏠 Startseite": Startseite,
        "📊 Bilanzanalyse": Bilanzanalyse,
        "🔗 Linkliste": Linkliste,
        "📈 Indizes": Indizes,
        "ⓘ Impressum": Impressum
    }
    @classmethod
    def create(cls, name: str) -> Page:
        page_class = cls._pages.get(name)
        if page_class is None: raise ValueError(f"Seite '{name}' ist nicht bekannt.")
        return page_class()

# ---------------------------------------------------
# Streamlit Hauptprogramm
# ---------------------------------------------------
st.set_page_config(page_title="Bilanzanalyse", layout="wide")

# Hamburger-Icon dauerhaft rot und größer
st.markdown("""
<style>
button[data-testid="stSidebarTrigger"] svg {
    width: 40px !important;
    height: 40px !important;
    fill: red !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://raw.githubusercontent.com/Mitho33/AnalyseApp1/main/TB12/LogoMT.png", width=120)
seiten = list(PageFactory._pages.keys())
wahl = st.sidebar.radio("Seite auswählen:", seiten)

seite_obj = PageFactory.create(wahl)
seite_obj.render()


