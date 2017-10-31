import requests
import json

class KoinexPublicClient:
    def __init__(self, api_url="https://koinex.in"):
        self.url = api_url

    def get_bid_ask(self, product):
        try:
            ob = self.get_product_order_book(product)
            bid = float(ob["stats"][product]["highest_bid"])
            ask = float(ob["stats"][product]["lowest_ask"])

            return (bid, ask)
        except:
            return None

    def get_product_order_book(self, product):
        try:
            r = requests.get(self.url + "/api/ticker")
            return json.loads(r.text)
        except Exception as e:
            print(e)
            return None


    def get_symbol(self, symbol):
        symbol = symbol.upper()
        if(symbol == "BTCINR"):
            return "BTC"
        elif(symbol == "ETHINR"):
            return "ETH"
        elif(symbol == "LTCINR"):
            return "LTC"



