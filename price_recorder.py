from public_client_factor import PublicClientFactor
from utils import Utils
from currency_converter import CurrencyConverter

import time
import os
import datetime

class DataRecorder:
    def __init__(self, cache_dir="./cache/"):
        self.cache_dir = cache_dir

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def write_price_data(self, symbol, exchange, bid, ask, curr_time):

        curr_date = datetime.datetime.fromtimestamp(curr_time).strftime("%Y%m%d")

        filename = Utils.get_data_filename(self.cache_dir, symbol, exchange, curr_date)
        with open(filename, 'a') as f:
            f.write(str(curr_time) + "," + str(bid) + "," + str(ask) + "\n")


    def record(self, symbols, exchanges, price_funs):
        while (True):

            count = len(symbols)
            curr_time = time.time()

            if(count == len(exchanges) and count == len(price_funs)):

                try:
                    for i in range(count):
                        sym = symbols[i]
                        ex = exchanges[i]
                        p_fun = price_funs[i]
                        price = p_fun()
                        self.write_price_data(sym, ex, price[0], price[1], curr_time)
                except Exception as e:
                    print(e)
                    pass

                time.sleep(Utils.ratio_interval_seconds())
            else:
                print("symbols, exchanges and price_funs length do not match")
                return

def convert_to_inr(exchange, symbol):
    if(exchange != "zebpay" and exchange != "koinex"):
        return True
    else:
        return False

if __name__ == "__main__":

    dr = DataRecorder()
    cr = CurrencyConverter()

    exchanges_l = ["koinex","zebpay", "gdax", "bitfinex", "cex"]

    pc = {}

    for e in exchanges_l:
        pc[e] = PublicClientFactor.get_public_client(e)

    symbols_d = {"zebpay" : ["btcinr"], "gdax": ["btcusd", "ethusd", "ltcusd"], "bitfinex": ["btcusd", "ethusd", "ltcusd"], "cex": ["btcusd", "ethusd"], "koinex" : ["btcinr", "ethinr", "ltcinr"]}

    exchanges = []
    symbols = []
    price_funs = []

    for e,sl in symbols_d.items():
        for s in sl:
            exchanges.append(e)
            symbols.append(s)
            sym = pc[e].get_symbol(s)
            if(convert_to_inr(e, s)):
                price_funs.append(lambda ss = sym, p = pc[e]: p.get_bid_ask(ss, lambda: cr.convert("USD", "INR")))
            else:
                price_funs.append(lambda ss = sym, p = pc[e]: p.get_bid_ask(ss))


    print(symbols)
    print(exchanges)
    dr.record(symbols, exchanges, price_funs)
