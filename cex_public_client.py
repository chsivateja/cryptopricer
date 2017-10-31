import requests

class CexPublicClient():
    def __init__(self, api_url="https://cex.io/api/"):
        if(api_url.endswith("/")):
            self.url = api_url[0:-1]
        else:
            self.url = api_url

    def get_bid_ask(self, product, currency_mutliplier = lambda: 1.0):
        try:
            ob = self.get_ticker(product)
            bid = float(ob["bid"]) * currency_mutliplier()
            ask = float(ob["ask"]) * currency_mutliplier()

            return (bid, ask)
        except:
            return None

    def get_ticker(self, symbol):
        try:
            r = requests.get(self.url + '/ticker/' + symbol)
            return r.json()
        except:
            return None

    def get_symbol(self, symbol):
        part1 = symbol[:3]
        part2 = symbol[3:]

        return part1.upper() + "/" + part2.upper()