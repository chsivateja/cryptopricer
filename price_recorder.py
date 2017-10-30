import koinex_public_client
import zebpay_public_client
import gdax_public_client
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
                        price = price_funs[i]()

                        self.write_price_data(sym, ex, price[0], price[1], curr_time)
                except:
                    pass

                time.sleep(Utils.ratio_interval_seconds())
            else:
                print("symbols, exchanges and price_funs length do not match")
                return

if __name__ == "__main__":

    dr = DataRecorder()
    cr = CurrencyConverter()

    gpc = gdax_public_client.GDAXPublicClient()
    zpc = zebpay_public_client.ZebpayPublicClient()
    kpc = koinex_public_client.KoinexPublicClient()

    symbols = ["btc/inr", "bitcoin", "BTC-USD"]
    exchanges = ["zebpay", "koinex", "gdax"]
    price_funs = [lambda: zpc.get_bid_ask(symbols[0]),
                  lambda: kpc.get_bid_ask(symbols[1]),
                  lambda: gpc.get_bid_ask(symbols[2], lambda: cr.convert("USD", "INR"))]

    dr.record(symbols, exchanges, price_funs)
