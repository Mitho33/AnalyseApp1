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
    #Spalte Gesamtvermögen wird initialisiert mit...
    #Pandas arbeitet automatisch vektorisiert,
    #d. h. Rechenoperationen auf Spalten werden auf jede Zeile angewendet, ohne Schleifen schreiben zu müssen.
    df["Gesamtvermögen"] = df["AV"] + df["UV"]
    df["Anlagenintensität (%)"] = round(df["AV"] / df["Gesamtvermögen"] * 100, 2)
    df["Liquidität 3 (%)"] = round(df["UV"] / df["KFK"] * 100, 2)
    df["Working Capital"] = df["UV"] - df["KFK"]
    df["Anlagendeckung 2 (%)"] = round((df["EK"] + df["LFK"]) / df["AV"], 2)
    df["Verschuldungsgrad (%)"] = round((df["LFK"] + df["KFK"]) / df["EK"] * 100, 2)
      #Wiedergabe Tabelle
    return df


# ---------------------------------------------------
# Startseite
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

# ---------------------------------------------------
# Bilanzanalyse
# ---------------------------------------------------
class Bilanzanalyse(Page):
    def render(self):
        st.title("📊 Bilanzanalyse für 2 Jahre")
        st.header("📥 Eingabe der Bilanzwerte")

        jahre = ["Jahr 1", "Jahr 2"]
        felder = ["AV", "UV", "EK", "LFK", "KFK"]

#         # Eingabeformular, Liste für Eingaben


                 # --- Spaltenkopf ---
        header_cols = st.columns(6)
        header_cols[0].write("**Jahr**")
        header_cols[1].write("**AV**")
        header_cols[2].write("**UV**")
        header_cols[3].write("**EK**")
        header_cols[4].write("**LFK**")
        header_cols[5].write("**KFK**")

        eingaben = []

        # --- Zeile 1: Jahr 1 ---
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

        # --- Zeile 2: Jahr 2 ---
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

        # --- DataFrame erzeugen ---
        df = pd.DataFrame(eingaben)
        st.write(df)       
        
        st.subheader("🔢 Berechnete Kennzahlen")
        df = berechne_kennzahlen(df)
        
        st.write(df)
       
 

        # CSV in Speicher erzeugen
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.download_button(
            label="📥 CSV herunterladen",
            data=csv_buffer.getvalue(),  # <-- getvalue() liefert str
            file_name="bilanzanalyse.csv",
            mime="text/csv"
        )

        

  
        
        st.subheader("📊 Balkendiagramm: Jahr 1 vs Jahr 2")
        # Balkenpositionen
        x = np.arange(len(felder))
        breite = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        # Balken für Jahr 1 (rot)
        ax.bar(x - breite/2, df.loc[df["Jahr"] == "Jahr 1", felder].values[0],
               width=breite, color='red', label='Jahr 1')

        # Balken für Jahr 2 (blau)
        ax.bar(x + breite/2, df.loc[df["Jahr"] == "Jahr 2", felder].values[0],
               width=breite, color='blue', label='Jahr 2')

        # Achsen & Titel
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
            # Buffer für PDF im Speicher
            buffer = io.BytesIO()

            with PdfPages(buffer) as pdf:
                # Tabelle
                fig_table, ax = plt.subplots(figsize=(14, 5))
                ax.axis("off")
                table = ax.table(cellText=df.values,
                                 colLabels=df.columns,
                                 loc="center")
                table.scale(1.2, 1.3)
                pdf.savefig(fig_table)
                plt.close(fig_table)

                # Diagramm
                fig.set_size_inches(14, 5)
                pdf.savefig(fig)

            buffer.seek(0)  # zum Anfang des Buffers

    # Download-Button
            st.download_button(
                label="📥 PDF herunterladen",
                data=buffer,
                file_name="Bilanzanalyse.pdf",
                mime="application/pdf"
                )

            st.success("PDF steht nun zum Download bereit!")







        # Sidebar-Formeln
        st.sidebar.title("📘 Kennzahlen Formeln")
        st.sidebar.write("""
        **Gesamtvermögen** = AV + UV  
        **Anlagenintensität (%)** = AV / Gesamtvermögen × 100  
        **Liquidität 3 (%)** = UV / KFK × 100  
        **Working Capital** = UV − KFK  
        **Anlagendeckung 2 (%)** = (EK + LFK) / AV  
        **Verschuldungsgrad (%)** = (LFK + KFK) / EK × 100  
        """)


# ---------------------------------------------------
# Linkliste
# ---------------------------------------------------
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


# ---------------------------------------------------
# Weitere Anwendung
# ---------------------------------------------------
class Indizes(Page):
    def render(self):
        st.title("🧩 Indizes")   
        #st.set_page_config(page_title="Live Börsenindizes", layout="wide")

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
        if "last_update" not in st.session_state:
            st.session_state.last_update = 0


        # --------------------------------------
        # Funktion zum Abrufen der Kursdaten
        # --------------------------------------
        def get_index_value(ticker):
            try:
                return yf.Ticker(ticker).info.get("regularMarketPrice", None)
            except:
                return None


        # --------------------------------------
        # Live Daten aktualisieren (alle 30s)
        # --------------------------------------
        now_ts = time.time()
        if now_ts - st.session_state.last_update > 30:   # alle 30 Sekunden
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



        # --------------------------------------
        # Streamlit Oberfläche
        # --------------------------------------
        st.title("📈 Live-Indizes: DAX, Dow Jones & Shanghai Composite")
        st.write("Automatische Aktualisierung alle 30 Sekunden")

        zeiten = st.session_state.zeiten[-50:]  # nur letzte 50 Werte
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


class Impressum(Page):
    def render(self):
#Zeilenumbruch in MarkDown 2mal Leertaste am Zeilenende
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

            Haftung für Inhalte
            Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen Seiten  
            nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8–10 TMG sind wir jedoch nicht verpflichtet,  
            übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen,  
            die auf eine rechtswidrige Tätigkeit hinweisen.

            Haftung für Links  
            Unsere Website enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben.  
            Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der  
            verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber verantwortlich.  

            Urheberrecht

            Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem  
            deutschen Urheberrecht. Beiträge Dritter sind als solche gekennzeichnet. Eine Vervielfältigung,  
            Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechts  
            bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. 

                    """)


# ---------------------------------------------------
# Factory-Idiom: erzeugt die richtige Seite
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
st.set_page_config(page_title="Bilanzanalyse", layout="wide")

# CSS einfügen, um Hamburger-Menü rot und größer zu färben
st.markdown(
    """
    <style>
    /* Hamburger Menü Icon links oben */
    [data-testid="collapsedControl"] {
        color: red !important;
        font-size: 28px !important;  /* Größe anpassen */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar-Logo
st.sidebar.image(
    "https://raw.githubusercontent.com/Mitho33/AnalyseApp1/main/TB12/LogoMT.png",
    width=120
)

# Sidebar-Auswahl der Seiten
seiten = list(PageFactory._pages.keys())
wahl = st.sidebar.radio("Seite auswählen:", seiten)

# Seite rendern
seite_obj = PageFactory.create(wahl)
seite_obj.render()


