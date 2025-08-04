import time
import pandas as pd
import streamlit as st
from heikin_ashi import heikin_ashi
from doji_detector import is_heikin_ashi_doji
from dhan_client_wrapper import DhanClientWrapper
from alerting import AlertSystem
from position_manager import PositionManager

st.title("Dhan Algo Trading Bot Dashboard")

# Sidebar inputs for credentials and settings
client_id = st.sidebar.text_input("Dhan Client ID")
access_token = st.sidebar.text_input("Dhan Access Token", type="password")
exchange = st.sidebar.text_input("Exchange", value="NSE_EQ")
security_id = st.sidebar.text_input("Security ID (e.g. 1333)")
quantity = st.sidebar.number_input("Quantity", min_value=1, value=1)
start_trading = st.sidebar.button("Start Trading")

# Initialize global variables in session_state
if 'ohlc_data' not in st.session_state:
    st.session_state.ohlc_data = []

if 'position_manager' not in st.session_state:
    st.session_state.position_manager = None
if 'position_active' not in st.session_state:
    st.session_state.position_active = False

alert_system = AlertSystem(
    email_settings=None,  # configure or leave None
    telegram_settings=None
)

if start_trading:
    if not client_id or not access_token or not exchange or not security_id:
        st.error("Please enter all credentials and settings!")
    else:
        client = DhanClientWrapper(client_id, access_token)
        st.success("Trading Started!")

        for _ in range(1000):  # Run for some iterations or replace with appropriate logic
            quote = client.get_ltp(exchange, security_id)
            if quote is None:
                st.warning("Skipping, unable to fetch quote.")
                time.sleep(5)
                continue

            now = pd.Timestamp.now()
            ohlc = {
                "Open": quote,
                "High": quote,
                "Low": quote,
                "Close": quote,
                "Volume": 0,
                "Datetime": now,
            }
            st.session_state.ohlc_data.append(ohlc)
            st.write(f"Latest LTP: {quote} at {now}")

            if len(st.session_state.ohlc_data) < 20:
