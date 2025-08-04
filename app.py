import time
import pandas as pd
from heikin_ashi import heikin_ashi
from doji_detector import is_heikin_ashi_doji
from dhan_client_wrapper import DhanClientWrapper
from alerting import AlertSystem
from position_manager import PositionManager

CLIENT_ID = "your-dhan-client-id"
ACCESS_TOKEN = "your-dhan-access-token"
EXCHANGE = "NSE_EQ"
SECURITY_ID = "1333"  # Example security ID, replace as needed
QUANTITY = 1

client = DhanClientWrapper(CLIENT_ID, ACCESS_TOKEN)

alert_system = AlertSystem(
    email_settings={
        "from_email": "you@example.com",
        "to_email": "alertrecipient@example.com",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 465,
        "username": "you@example.com",
        "password": "your_app_password"
    },
    telegram_settings={
        "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "chat_id": "YOUR_TELEGRAM_CHAT_ID"
    }
)

position_manager = None
position_active = False

ohlc_data = []

while True:
    quote = client.get_ltp(EXCHANGE, SECURITY_ID)
    if quote is None:
        print("Skipping, unable to fetch quote.")
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
    ohlc_data.append(ohlc)

    if len(ohlc_data) < 20:
        time.sleep(60)
        continue

    df = pd.DataFrame(ohlc_data[-20:])
    ha_df = heikin_ashi(df)
    latest_ha = ha_df.iloc[-1]

    if is_heikin_ashi_doji(latest_ha) and not position_active:
        print(f"Doji Detected at {latest_ha['Datetime']}: Attempting to BUY")
        order = client.place_order(
            security_id=SECURITY_ID,
            exchange_segment=EXCHANGE,
            quantity=QUANTITY,
            order_type="MARKET",
            transaction_type="BUY",
            product_type="INTRA"
        )
        # Assuming order executed at last price
        entry_price = quote
        position_manager = PositionManager(entry_price)
        position_active = True
        alert_system.alert("Trade Entry", f"Entered trade at {entry_price}")

    if position_active:
        signal = position_manager.update(quote)
        if signal in ("TAKE_PROFIT", "STOP_LOSS"):
            print(f"Exiting position due to {signal} at price {quote}")
            exit_order = client.place_order(
                security_id=SECURITY_ID,
                exchange_segment=EXCHANGE,
                quantity=QUANTITY,
                order_type="MARKET",
                transaction_type="SELL",
                product_type="INTRA"
            )
            alert_system.alert("Trade Exit", f"Exited trade at {quote} due to {signal}")
            position_active = False
            position_manager = None

    time.sleep(60)
