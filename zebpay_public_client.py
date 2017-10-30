import requests
import json

class ZebpayPublicClient:
    def __init__(self, api_url="https://www.zebapi.com"):
         self.url = api_url


    def get_bid_ask(self, product):
        try:
            ob = self.get_product_ticker(product)
            bid = float(ob["sell"])
            ask = float(ob["buy"])

            return (bid, ask)
        except:
            return None

    def get_product_ticker(self, product):
        try:
            r = requests.get(self.url + "/api/v1/market/ticker/" + product)
            return json.loads(r.text)
        except:
            return None