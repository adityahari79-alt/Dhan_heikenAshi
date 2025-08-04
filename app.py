import time
import pandas as pd
import streamlit as st
from heikin_ashi import heikin_ashi
from doji_detector import is_heikin_ashi_doji
from dhan_client_wrapper import DhanClientWrapper
from alerting import AlertSystem
from position_manager import PositionManager

st.title("Dhan Heikin Ashi Algo Trading Bot")

# Sidebar inputs
client_id = st.sidebar.text_input("Dhan Client ID")
access_token = st.sidebar.text_input("Dhan Access Token", type="password")
exchange = st.sidebar.text_input("Exchange", value="NSE_EQ")
security_id = st.sidebar.text_input("Security ID (e.g. 1333)")
quantity = st.sidebar.number_input("Quantity", min_value=1, value=1)
start = st.sidebar.button("Start Trading")

# Initialize session state variables
if 'ohlc_data' not in st.session_state:
    st.session_state.ohlc_data = []

if 'position_manager' not in st.session_state:
    st.session_state.position_manager = None

if 'position_active' not in st.session_state:
    st.session_state.position_active = False

# Alerting system config (empty or fill in your settings)
alert_system = AlertSystem(
    email_settings=None,
    telegram_settings=None
)

if start:
    if not all([client_id, access_token, exchange, security_id]):
        st.error("Please fill all credentials and settings in sidebar!")
    else:
        client = DhanClientWrapper(client_id, access_token)
        st.success("Trading started!")

        for _ in range(1000):  # Run max 1000 iterations - adjust or use while True
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
                st.info(f"Waiting for 20 candles: currently have {len(st.session_state.ohlc_data)}")
                time.sleep(60)
                continue

            df = pd.DataFrame(st.session_state.ohlc_data[-20:])
            ha_df = heikin_ashi(df)
            latest_ha = ha_df.iloc[-1]

            if is_heikin_ashi_doji(latest_ha) and not st.session_state.position_active:
                st.write(f"Doji Detected at {latest_ha['Datetime']}: Attempting to BUY")
                order = client.place_order(
                    security_id=security_id,
                    exchange_segment=exchange,
                    quantity=quantity,
                    order_type="MARKET",
                    transaction_type="BUY",
                    product_type="INTRA"
                )
                entry_price = quote
                st.session_state.position_manager = PositionManager(entry_price)
                st.session_state.position_active = True
                alert_system.alert("Trade Entry", f"Entered trade at {entry_price}")

            if st.session_state.position_active:
                signal = st.session_state.position_manager.update(quote)
                if signal in ("TAKE_PROFIT", "STOP_LOSS"):
                    st.write(f"Exiting position due to {signal} at price {quote}")
                    exit_order = client.place_order(
                        security_id=security_id,
                        exchange_segment=exchange,
                        quantity=quantity,
                        order_type="MARKET",
                        transaction_type="SELL",
                        product_type="INTRA"
                    )
                    alert_system.alert("Trade Exit", f"Exited trade at {quote} due to {signal}")
                    st.session_state.position_active = False
                    st.session_state.position_manager = None

            time.sleep(60)

