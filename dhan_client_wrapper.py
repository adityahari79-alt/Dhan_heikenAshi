from dhanhq import dhanhq

class DhanClientWrapper:
    def __init__(self, client_id, access_token):
        self.client = dhanhq(client_id, access_token)

    def get_ltp(self, exchange, security_id):
        # Get last traded price from Dhan's OHLC API
        print("get_ltp called with:", exchange, security_id)
        resp = self.client.ohlc_data({exchange: [security_id]})
        print(f"Raw LTP response: {resp}")  # Log raw response
        if exchange in resp and security_id in resp[exchange]:
            return resp[exchange][security_id]['last_traded_price']
        else:
            return None

    def place_order(self, security_id, exchange_segment, quantity,
                    order_type="MARKET", transaction_type="BUY",
                    product_type="INTRA", price=0):
        return self.client.place_order(
            security_id=security_id,
            exchange_segment=exchange_segment,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product_type=product_type,
            price=price
        )


