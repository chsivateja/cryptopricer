import requests

class BitfinexPublicClient():
    def __init__(self, api_url="https://api.bitfinex.com"):
        self.url = api_url
        if api_url[-1] == "/":
            self.url = api_url[:-1]

    def get_bid_ask(self, product, currency_mutliplier = lambda: 1.0):
        try:
            ob = self.get_ticker(product)
            bid = float(ob["bid"]) * currency_mutliplier()
            ask = float(ob["ask"]) * currency_mutliplier()

            return (bid, ask)
        except:
            return None


    def get_ticker(self, ticker):
        try:
            r = requests.get(self.url + '/v1/pubticker/' + ticker)
            return r.json()
        except:
            return None

    def get_symbol(self, symbol):
        return symbol.upper()