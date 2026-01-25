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
from streamlit_autorefresh import st_autorefresh
#hierfür pip install streamlit-autorefresh

# ---------------------------------------------------
# Basis Page-Klasse (abstrakt)
# ---------------------------------------------------
class Page(ABC):
   @abstractmethod
   def render(self):
       pass

#class Page(ABC):
#    def render(self):
##        self.render_header()
 #       self.render_body()
 #       self.render_footer()

#    def render_header(self):
#        pass

#    @abstractmethod
 #   def render_body(self):
#        pass

 #   def render_footer(self):
 #       pass


class LayoutStrategy(ABC):
    @abstractmethod
    def renderLayout(self, page):
        pass

#----------------------------------------------------
#Konkrete Strategien
#----------------------------------------------------

class OneColumnLayout(LayoutStrategy):
    def renderLayout(self, page):
        st.container()
        page.render_body()

class TwoColumnLayout(LayoutStrategy):
    def renderLayout(self, page):
        col1, col2 = st.columns(2)

        with col1:
            #hasattr = „hat Eigenschaft, aktuelle Seite, Name der Funktion
            if hasattr(page, "render_left"):
                #dann rufe diese Funktion auf
                page.render_left()
            else:
                st.error("render_left() fehlt")

        with col2:
            if hasattr(page, "render_right"):
                page.render_right()
            else:
                st.error("render_right() fehlt")


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


## ---------------------------------------------------
# Startseite
# ---------------------------------------------------
class Startseite(Page):
        def render(self):
        #Konstuktor mit Methode und Parameter self==page
            TwoColumnLayout().renderLayout(self) 
      
        
        def render_left(self):
            
            st.title("🏠 Willkommen zur Analyse-App")

            st.header("Überblick")
            st.write(
                "Diese Anwendung unterstützt die betriebswirtschaftliche Analyse, "
                "die Erstellung von Ergebnisrechnungen sowie die Marktbeobachtung."
            )

            st.header("Module")

            st.subheader("📊 Bilanzanalyse")
            st.write("Bilanzwerte für zwei Jahre, Kennzahlenberechnung und Export als PDF.")
            if st.button("Zur Bilanzanalyse"):
                st.session_state.seite = "📊 Bilanzanalyse"
                st.rerun()

            st.subheader("📑 Ergebnisrechnung")
            st.write("Erstellung der Abgrenzung sowie RKI-, RKII- und Betriebsergebnisrechnung.")
            if st.button("Zur Ergebnisrechnung"):
                st.session_state.seite = "📑 Ergebnisrechnung"
                st.rerun()

            st.subheader("🔗 Linkliste")
            st.write("Sammlung nützlicher externer Fachquellen.")
            if st.button("Zur Linkliste"):
                st.session_state.seite = "🔗 Linkliste"
                st.rerun()

            st.subheader("📈 Indizes")
            st.write("Live-Übersicht ausgewählter Börsenindizes.")
            if st.button("Zu den Indizes"):
                st.session_state.seite = "📈 Indizes"
                st.rerun()

            st.subheader("ⓘ Impressum")
            st.write("Impressum und rechtliche Hinweise.")
            if st.button("Zum Impressum"):
                st.session_state.seite = "ⓘ Impressum"
                st.rerun()
                
        def render_right(self):
            st.image("BildMural1.png", caption="Mural Wuppertal", width ="stretch")

# ---------------------------------------------------
# Bilanzanalyse
# ---------------------------------------------------
class Bilanzanalyse(Page):
    def render(self):
        OneColumnLayout().renderLayout(self)
    
    def render_body(self):
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
# Ergebnisrechnung (RKI / RKII / Betriebsergebnis)
# ---------------------------------------------------
class Ergebnisrechnung(Page):
    def render(self):
        OneColumnLayout().renderLayout(self)
    
    def render_body(self):
        st.title("📑 Ergebnisrechnung (RKI / RKII / Betriebsergebnis)")

        # -----------------------------------
        # Initialisierung DataFrame
        # -----------------------------------
        if "ergebnis_df" not in st.session_state:
            st.session_state.ergebnis_df = pd.DataFrame({
                "Kontoname": ["" for _ in range(20)],

                # RKI
                "Aufwand": [0.0]*20,
                "Ertrag": [0.0]*20,

                # RKII – Unternehmensbezogene Abgrenzung
                "Neutrale Aufwendungen": [0.0]*20,
                "Neutrale Erträge": [0.0]*20,

                # RKII – Kostenrechnerische Korrekturen
                "Betriebliche Aufwendungen": [0.0]*20,
                "Verrechnete Kosten": [0.0]*20,

                # Betriebsergebnisrechnung
                "Kosten": [0.0]*20,
                "Leistung": [0.0]*20,
            })

        # -----------------------------------
        # Mehrzeiliger Tabellenkopf
        # -----------------------------------
        #h1 = st.columns([2, 2, 2, 4, 4, 4])
        #erzeugt 9 Spalten mit der gleichen Länge
        h1 = st.columns([2, 2, 2, 2, 2, 2, 2, 2, 2])
        #h1[0].markdown("**Kontoname**")
        h1[1].markdown("**RKI**")
        h1[3].markdown("**RKII**")
        h1[5].markdown("**RKII**")
        h1[7].markdown("**RKII**")
    

        h2 = st.columns([2, 2, 2, 2, 2, 2, 2, 2, 2])
        h2[1].markdown("**Gesamtergebnisrechnung**")
        h2[3].markdown("**Unternehmensbezogene Abgrenzung**")
        h2[5].markdown("**Kostenrechnerische Korrekturen**")
        h2[8].markdown("**Betriebsergebnisrechnung**")

        #h3 = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])
        #h3[0].markdown("**Kontoname**")
        #h3[1].markdown("**Aufwand**")
        #h3[2].markdown("**Ertrag**")
        #h3[3].markdown("**Neutr. Aufw.**")
        #h3[4].markdown("**Neutr. Ertr.**")
        #h3[5].markdown("**Betr. Aufw.**")
        #h3[6].markdown("**Verrechn. Kosten**")
        #h3[7].markdown("**Kosten**")
        #h3[8].markdown("**Leistung**")

        st.divider()

        # -----------------------------------
        # Eingabetabelle
        # -----------------------------------
        df = st.data_editor(
            st.session_state.ergebnis_df,
            num_rows="fixed",
            width="stretch",                     #ersetzt use_container_width=True, For `use_container_width=False`, use `width='content'
            hide_index=True
        )

        # -----------------------------------
        # Summen je Spalte
        # -----------------------------------
        sums = df.sum(numeric_only=True)

        # -----------------------------------
        # Salden / Ergebnisse
        # -----------------------------------
        saldo_rki = sums["Ertrag"] - sums["Aufwand"]
        saldo_neutral = sums["Neutrale Erträge"] - sums["Neutrale Aufwendungen"]
        saldo_korrektur = sums["Verrechnete Kosten"] - sums["Betriebliche Aufwendungen"]
        betriebsergebnis = sums["Leistung"] - sums["Kosten"]

        produktivitaet = sums["Leistung"] / sums["Kosten"] if sums["Kosten"] != 0 else 0
        ebit = betriebsergebnis

        # -----------------------------------
        # Summen & Salden Tabelle
        # -----------------------------------
        st.subheader("🔢 Summen & Salden")

        summary_df = pd.DataFrame({
            "": ["Summe", "Saldo / Ergebnis"],
            "Aufwand": [sums["Aufwand"], -saldo_rki],
            "Ertrag": [sums["Ertrag"], saldo_rki],
            "Neutrale Aufwendungen": [sums["Neutrale Aufwendungen"], -saldo_neutral],
            "Neutrale Erträge": [sums["Neutrale Erträge"], saldo_neutral],
            "Betriebliche Aufwendungen": [sums["Betriebliche Aufwendungen"], -saldo_korrektur],
            "Verrechnete Kosten": [sums["Verrechnete Kosten"], saldo_korrektur],
            "Kosten": [sums["Kosten"], -betriebsergebnis],
            "Leistung": [sums["Leistung"], betriebsergebnis],
        })

        st.dataframe(summary_df, use_container_width=True)

        # -----------------------------------
        # Dashboard
        # -----------------------------------
        st.subheader("📊 Kennzahlen")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jahresüberschuss (RKI)", f"{saldo_rki:,.2f}")
        c2.metric("Betriebsergebnis", f"{betriebsergebnis:,.2f}")
        c3.metric("Produktivität", f"{produktivitaet:.2f}")
        c4.metric("EBIT", f"{ebit:,.2f}")

        # -----------------------------------
        # CSV Export
        # -----------------------------------
        csv_buffer = io.StringIO()
        export_df = pd.concat([df, summary_df], ignore_index=True)
        export_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.download_button(
            "📥 CSV herunterladen",
            data=csv_buffer.getvalue(),
            file_name="Ergebnisrechnung_mit_Summen_und_Salden.csv",
            mime="text/csv"
        )

        # -----------------------------------
        # PDF Export
        # -----------------------------------
        if st.button("📄 PDF erzeugen"):
            buffer = io.BytesIO()

            with PdfPages(buffer) as pdf:
                fig, ax = plt.subplots(figsize=(18, 6))
                ax.axis("off")
                table = ax.table(
                    cellText=export_df.fillna("").values,
                    colLabels=export_df.columns,
                    loc="center"
                )
                table.scale(1, 1.2)
                pdf.savefig(fig)
                plt.close(fig)

            buffer.seek(0)

            st.download_button(
                "📥 PDF herunterladen",
                data=buffer,
                file_name="Ergebnisrechnung_mit_Summen_und_Salden.pdf",
                mime="application/pdf"
            )


# ---------------------------------------------------
# Linkliste
# ---------------------------------------------------
class Linkliste(Page):
    def render(self):
        
        TwoColumnLayout().renderLayout(self) 
      
        
    def render_left(self):
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
    def render_right(self):
        st.image("Kunst1.jpg", width ="stretch")



# ---------------------------------------------------
# Weitere Anwendung
# ---------------------------------------------------
class Indizes(Page):
    
    def render(self):
        OneColumnLayout().renderLayout(self)

    def render_body(self):
        st.title("📈 Live-Indizes: DAX, Dow Jones & Shanghai Composite")
        st.write("Automatische Aktualisierung alle 30 Sekunden")

        # Autorefresh alle 30 Sekunden
        st_autorefresh(interval=30*1000, key="refresh")

        # -----------------------------
        # Session-State initialisieren
        # -----------------------------
        for key in ["zeiten", "dax", "dow", "shanghai"]:
            if key not in st.session_state:
                st.session_state[key] = []

        # -----------------------------
        # Funktion zum Abrufen der Indexwerte
        # -----------------------------
        def get_index_value(ticker):
            try:
                return yf.Ticker(ticker).info.get("regularMarketPrice")
            except:
                return None

        # -----------------------------
        # Daten updaten
        # -----------------------------
        now = datetime.now().strftime("%H:%M:%S")
        dax = get_index_value("^GDAXI")
        dow = get_index_value("^DJI")
        shanghai = get_index_value("000001.SS")

        if all(val is not None for val in [dax, dow, shanghai]):
            st.session_state.zeiten.append(now)
            st.session_state.dax.append(dax)
            st.session_state.dow.append(dow)
            st.session_state.shanghai.append(shanghai)

            # Nur letzte 50 Werte behalten
            for key in ["zeiten", "dax", "dow", "shanghai"]:
                st.session_state[key] = st.session_state[key][-50:]

        # -----------------------------
        # Diagramm-Funktion
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

        # -----------------------------
        # Diagramme in 3 Spalten
        # -----------------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            plot_line(st.session_state.zeiten, st.session_state.dax, "DAX", "blue")
        with col2:
            plot_line(st.session_state.zeiten, st.session_state.dow, "Dow Jones", "green")
        with col3:
            plot_line(st.session_state.zeiten, st.session_state.shanghai, "Shanghai Composite", "red")


class Impressum(Page):
    def render(self):       
        TwoColumnLayout().renderLayout(self) 
      
        
    def render_left(self):     
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

    def render_right(self):
        st.image("TOM26.png", width ="stretch")


# ---------------------------------------------------
# Factory-Idiom: erzeugt die richtige Seite
# ---------------------------------------------------
class PageFactory:
    _pages = {
        "🏠 Startseite": Startseite,
        "📊 Bilanzanalyse": Bilanzanalyse,
        "📑 Ergebnisrechnung": Ergebnisrechnung, 
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
    /* Material-Icon für Sidebar Collapse */
    [data-testid="stIconMaterial"] {
        color: red !important;   /* Textfarbe des Icons */
        font-size: 48px !important; /* Größe */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Sidebar-Logo
st.sidebar.image(
  #  für Git "https://raw.githubusercontent.com/Mitho33/AnalyseApp1/main/TB12/LogoMT.png",
    "LogoMT.png", width=120
)

# -----------------------------------
# Session State für Navigation
# -----------------------------------
#if "seite" not in st.session_state:
#    st.session_state.seite = "🏠 Startseite"


# Sidebar-Auswahl der Seiten
#seiten = list(PageFactory._pages.keys())
#wahl = st.sidebar.radio(
 #   "Seite auswählen:",
 #   seiten,
  #  index=seiten.index(st.session_state.seite)
#)
#st.session_state.seite = wahl

#seiten = list(PageFactory._pages.keys())
#tabs = st.tabs(seiten)

#for tab, seite in zip(tabs, seiten):
#    with tab:
#        PageFactory._pages[seite]()

# Seite rendern
#seite_obj = PageFactory.create(wahl)
#seite_obj.render()


st.set_page_config(page_title="Bilanzanalyse", layout="wide")

# Top-Navigation
seiten = list(PageFactory._pages.keys())

if "seite" not in st.session_state or st.session_state.seite not in seiten:
    st.session_state.seite = "🏠 Startseite"

cols = st.columns(len(seiten))

for col, seite in zip(cols, seiten):
    aktiv = seite == st.session_state.seite
    label = f"➡️ {seite}" if aktiv else seite

    if col.button(label, use_container_width=True):
        st.session_state.seite = seite
        st.rerun()

st.divider()

# Seite laden & anzeigen
page = PageFactory.create(st.session_state.seite)
page.render()




