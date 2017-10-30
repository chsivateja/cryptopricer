import requests

class GDAXPublicClient():
    def __init__(self, api_url="https://api.gdax.com"):
        self.url = api_url
        if api_url[-1] == "/":
            self.url = api_url[:-1]


    def get_products(self):
        try:
            r = requests.get(self.url + '/products')
            return r.json()
        except:
            return None

    def get_bid_ask(self, product, currency_mutliplier = lambda: 1.0):
        try:
            ob = self.get_product_order_book(product, 1)
            bid = float(ob["bids"][0][0]) * currency_mutliplier()
            ask = float(ob["asks"][0][0]) * currency_mutliplier()

            return (bid, ask)
        except:
            return None


    def get_product_order_book(self, product, level=2):
        try:
            r = requests.get(self.url + '/products/%s/book?level=%s' % (product, str(level)))
            return r.json()
        except:
            return None

    def get_product_ticker(self, product):
        try:
            r = requests.get(self.url + '/products/%s/ticker' % (product))
            return r.json()
        except:
            return None

    def get_product_trades(self, product):
        try:
            r = requests.get(self.url + '/products/%s/trades' % (product))
            return r.json()
        except:
            return None

    def get_product_historic_rates(self, product, start='', end='', granularity=''):
        try:
            payload = {}
            payload["start"] = start
            payload["end"] = end
            payload["granularity"] = granularity
            r = requests.get(self.url + '/products/%s/candles' % (product), params=payload)
            return r.json()
        except:
            return None

    def get_product_24hr_stats(self, product):
        try:
            r = requests.get(self.url + '/products/%s/stats' % (product))
            return r.json()
        except:
            return None

    def get_currencies(self):
        try:
            r = requests.get(self.url + '/currencies')
            return r.json()
        except:
            return None

    def get_time(self):
        try:
            r = requests.get(self.url + '/time')
            return r.json()
        except:
            return None