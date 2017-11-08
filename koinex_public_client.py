import requests
import json
import time

class KoinexPublicClient:
    def __init__(self, api_url="https://koinex.in"):
        self.url = api_url
        self.last_req_time = 0
        self.bid = 0
        self.ask = 0

    def get_bid_ask(self, product):
        try:
            if(time.time() - self.last_req_time > 30):
                ob = self.get_product_order_book(product)
                self.bid = float(ob["stats"][product]["highest_bid"])
                self.ask = float(ob["stats"][product]["lowest_ask"])
                self.last_req_time = time.time()

            return (self.bid, self.ask)
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



