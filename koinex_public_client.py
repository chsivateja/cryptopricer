import requests
import json

class KoinexPublicClient:
    def __init__(self, api_url="https://koinex.in"):
        self.url = api_url

    def get_bid_ask(self, product):
        try:
            ob = self.get_product_order_book(product)
            bid = float(ob["buy_orders"]["data"][0]["price_per_unit"])
            ask = float(ob["sell_orders"]["data"][0]["price_per_unit"])

            return (bid, ask)
        except:
            return None

    def get_product_order_book(self, product):
        try:
            r = requests.get(self.url + "/api/dashboards/order_history?target_currency=" + product)
            return json.loads(r.text)
        except:
            return None






