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

# ---------------------------------------------------
# CSS für Hamburger-Button
# ---------------------------------------------------
st.set_page_config(page_title="Bilanzanalyse", layout="wide")

st.markdown("""
<style>
/* Hamburger-Button größer und rot */
button[data-testid="stSidebarTrigger"] svg {
    width: 40px !important;
    height: 40px !important;
    fill: red !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Basis Page-Klasse (abstrakt)
# ---------------------------------------------------
class Page(ABC):
    @abstractmethod
    def render(self):
        pass

# ---------------------------------------------------
# Hilfsfunktion für Kennzahlen
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
# Seiten
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
        header_cols[1].write("**AV**")
        header_cols[2].write("**UV**")
        header_cols[3].write("**EK**")
        header_cols[4].write("**LFK**")
        header_cols[5].write("**KFK**")

        eingaben = []

        row1 = st.columns(6)
        row1[0].write("Jahr 1")
        werte1 = {
            "Jahr": "Jahr 1",
            "AV":  row1[1].number_input("Jahr1-AV",  value=0.0, label_visibility="collapsed"),
            "UV":  row1[2].number_input("Jahr1-UV",  value=0.0, label_visibility="collapsed"),
            "EK":  row1[3].number_input("Jahr1-EK",  value=0.0, label_visibility="collapsed"),
            "LFK": row1[4].number_input("Jahr1-LFK", value=0.0, label_visibility="collapsed"),
            "KFK": row1[5].number_input("Jahr1-KFK", value=0.0, label_visibility="collapsed"),
        }
        eingaben.append(werte1)

        row2 = st.columns(6)
        row2[0].write("Jahr 2")
        werte2 = {
            "Jahr": "Jahr 2",
            "AV":  row2[1].number_input("Jahr2-AV",  value=0.0, label_visibility="collapsed"),
            "UV":  row2[2].number_input("Jahr2-UV",  value=0.0, label_visibility="collapsed"),
            "EK":  row2[3].number_input("Jahr2-EK",  value=0.0, label_visibility="collapsed"),
            "LFK": row2[4].number_input("Jahr2-LFK", value=0.0, label_visibility="collapsed"),
            "KFK": row2[5].number_input("Jahr2-KFK", value=0.0, label_visibility="collapsed"),
        }
        eingaben.append(werte2)

        df = pd.DataFrame(eingaben)
        st.write(df)       

        st.subheader("🔢 Berechnete Kennzahlen")
        df = berechne_kennzahlen(df)
        st.write(df)

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        st.download_button(
            label="📥 CSV herunterladen",
            data=csv_buffer.getvalue(),
            file_name="bilanzanalyse.csv",
            mime="text/csv"
        )

        st.subheader("📊 Balkendiagramm: Jahr 1 vs Jahr 2")
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

        st.header("📄 Export als PDF")
        if st.button("PDF erzeugen"):
            buffer = io.BytesIO()
            with PdfPages(buffer) as pdf:
                fig_table, ax = plt.subplots(figsize=(14, 5))
                ax.axis("off")
                table = ax.table(cellText=df.values, colLabels=df.columns, loc="center")
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
            st.success("PDF steht nun zum Download bereit!")

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
        st.title("📈 Live-Indizes: DAX, Dow Jones & Shanghai")
        st.write("Automatische Aktualisierung alle 30 Sekunden")

        if "zeiten" not in st.session_state:
            st.session_state.zeiten = []
        if "dax" not in st.session_state:
            st.session_state.dax = []
        if "dow" not in st.session_state:
            st.session_state.dow = []
        if "shanghai" not in st.session_state:
            st.session_state.shanghai = []
        if "last_update" not in st.session_state:
            st.session_state.last_update = 0

        def get_index_value(ticker):
            try:
                return yf.Ticker(ticker).info.get("regularMarketPrice", None)
            except:
                return None

        now_ts = time.time()
        if now_ts - st.session_state.last_update > 30:
            now = datetime.now().strftime("%H:%M:%S")
            dax = get_index_value("^GDAXI")
            dow = get_index_value("^DJI")
            shanghai = get_index_value("000001.SS")
            if dax and dow and shanghai:
                st.session_state.zeiten.append(now)
                st.session_state.dax.append(dax)
                st.session_state.dow.append(dow)
                st.session_state.shanghai.append(shanghai)
            st.session_state.last_update = now_ts
            st.rerun()

        zeiten = st.session_state.zeiten[-50:]
        dax = st.session_state.dax[-50:]
        dow = st.session_state.dow[-50:]
        shanghai = st.session_state.shanghai[-50:]

        col1, col2, col3 = st.columns(3)

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
        ...

        Urheberrecht  
        ...
        """)

# ---------------------------------------------------
# Factory
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
        if page_class is None:
            raise ValueError(f"Seite '{name}' ist nicht bekannt.")
        return page_class()

# ---------------------------------------------------
# Streamlit Hauptprogramm
# ---------------------------------------------------
st.sidebar.image("https://raw.githubusercontent.com/Mitho33/AnalyseApp1/main/TB12/LogoMT.png", width=120)
seiten = list(PageFactory._pages.keys())
wahl = st.sidebar.radio("Seite auswählen:", seiten)
seite_obj = PageFactory.create(wahl)
seite_obj.render()
