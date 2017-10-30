from selenium import webdriver
import requests
import json
import time

class KoinexPublicClient:
    def __init__(self, api_url="https://koinex.in"):
        self.url = api_url
        self.driver = webdriver.Ch
        self.driver.get("https://koinex.in/exchange/bitcoin")
        time.sleep(10)
        self.cookies = self.to_cookies_str(self.driver.get_cookies())

        self.headers = {'frontendv': 33,
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.8,en-GB;q=0.6',
                        'accept': 'application/json',
                        'referer': 'https://koinex.in/exchange/ether',
                        'authority': 'koinex.in',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                        'secret-token': 'e4daf3f603e7899ae17afa2b869e8b2feead34db918b0be53e68b65f49a6c2f8de5677502d46100cca7759efa378d0faf89040aa5b75d732f18a2c5f54c07be5',
                        'cookie': self.cookies}


    def to_cookies_str(self, cookies):
        st = ""

        for cookie in cookies:
            name = cookie["name"]
            value = cookie["value"]
            st += name + "=" + value + "; "

        st += "exchange_type=ETHEREUM; target_currency=ether; chatRole=standard;"


        print(st)

        return st

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
            r = requests.get(self.url + "/api/dashboards/order_history?target_currency=" + product, headers = self.headers)
            print(r.text)
            return json.loads(r.text)
        except:
            return None






