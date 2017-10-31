import requests

class GDAXPublicClient():
    def __init__(self, api_url="https://api.gdax.com"):
        self.url = api_url
        if api_url[-1] == "/":
            self.url = api_url[:-1]

    def get_bid_ask(self, product, currency_mutliplier = lambda: 1.0):
        try:
            ob = self.get_product_ticker(product)
            bid = float(ob["bid"]) * currency_mutliplier()
            ask = float(ob["ask"]) * currency_mutliplier()

            return (bid, ask)
        except:
            return None

    def get_product_ticker(self, product):
        try:
            r = requests.get(self.url + '/products/%s/ticker' % (product))
            return r.json()
        except:
            return None

    def get_product_order_book(self, product, level=2):
        try:
            r = requests.get(self.url + '/products/%s/book?level=%s' % (product, str(level)))
            return r.json()
        except:
            return None

    def get_symbol(self, symbol):
        part1 = symbol[:3]
        part2 = symbol[3:]

        return part1.upper() + "-" + part2.upper()