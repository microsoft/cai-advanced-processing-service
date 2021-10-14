""" MYLA Demo - Digital Lab Assistant """
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime
import sys

# Import custom packages
sys.path.append('./')
import blob_request as blob
import helper

# Page config
st.set_page_config(
    page_title="Table Storage Dashboard",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo
logo = Image.open('Microsoft-Logo.png')

# Environment Variables
connection_data = helper.get_connection_data()

### SIDE BAR
HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""

st.sidebar.image(logo, use_column_width=True, output_format='JPG')
st.sidebar.subheader("Justus Dashboard")
st.sidebar.markdown(
"""
Dashboard für Erstattungsanträge und Zeugentermine

\n\n
""")

# Authentication
st.sidebar.subheader("Authentifizierung")
user = st.sidebar.text_input("Nutzername", value="user")
password = st.sidebar.text_input("Passwort", type="password", value="test123")

with st.beta_expander("Erstattungsanträge"):
    tasks = blob.get_data_from_table({'table_name': 'ndsjustizdemozeugenabrechnung', 'connection_string': "DefaultEndpointsProtocol=https;AccountName=jagotestingfunctions;AccountKey=/ED2eAurl0DIZIedulyj9JYCTbvpQqSm5KSfmi8g/NVDEGNLO36YG7jRKZK4Juxwcst2GpNzQ4UmPZg+fsiPxw==;EndpointSuffix=core.windows.net"})
    st.dataframe(pd.DataFrame(tasks)[['Timestamp', 'Adresse', 'Bankinstitut', 'BehoerdeOrt', 'Geschaeftsnummer', 'Kontoinhaber', 'TerminDatum']])

with st.beta_expander("Zeugentermine"):
    tasks = blob.get_data_from_table({'table_name': 'ndsjustizdemozeugentermine', 'connection_string': "DefaultEndpointsProtocol=https;AccountName=jagotestingfunctions;AccountKey=/ED2eAurl0DIZIedulyj9JYCTbvpQqSm5KSfmi8g/NVDEGNLO36YG7jRKZK4Juxwcst2GpNzQ4UmPZg+fsiPxw==;EndpointSuffix=core.windows.net"})
    st.dataframe(pd.DataFrame(tasks)[['Timestamp', 'BehoerdeOrt', 'GerichtsArt', 'Geschaeftsnummer', 'Nachname', 'Termin_Datum', 'Termin_Uhrzeit']])