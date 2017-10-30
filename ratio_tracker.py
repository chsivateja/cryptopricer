import koinex_public_client
import gdax_public_client

from utils import Utils

import time
import math
from queue import Queue
from currency_converter import CurrencyConverter
import argparse

import smtplib
from email.mime.text import MIMEText

EMAILS = ["siddharth.garg85@gmail.com", "jackson.garg@gmail.com"]

class RatioTracker:
    def __init__(self, cache_dir = "./cache/"):
        self.cache_dir = cache_dir
        self.last_email_time = 0

    def read_data(self, symbol, exchange, duration_seconds):
        days = math.ceil(duration_seconds / 3600.0 / 24.0)

        curr_time = time.time()
        start_time = curr_time - duration_seconds

        data = {}

        for i in range(days):
            d_date = Utils.get_date(days - i - 1)
            filename = Utils.get_data_filename(self.cache_dir, symbol, exchange, d_date)
            try:
                with open(filename, 'r') as file:
                    for l in file:
                        l = l.strip()
                        rec_time, bid, ask = l.split(",")

                        if (float(rec_time) > start_time):
                            data[rec_time] = (float(bid), float(ask))
            except:
                pass

        return data

    def average(self, price1, price2):
        ratio = 0
        ratio_q = Queue()

        for k in sorted(price1.keys()):
            if (k in price2):
                v1 = price1[k]
                v2 = price2[k]
                r =  Utils.mid(v1[0], v1[1]) / Utils.mid(v2[0], v2[1])
                ratio = (ratio * ratio_q.qsize() + r) / (ratio_q.qsize() + 1)
                ratio_q.put(r)

        return (ratio, ratio_q)

    def process(self, avg_ratio, curr_ratio, threshold):
        signal = (1 - curr_ratio / avg_ratio) * 100.0

        if(signal > threshold):
            st = "Buy Signal: \n"
            st += "Average Ratio = " + str(round(avg_ratio, 2)) + "\n"
            st += "Current Ratio = " + str(round(curr_ratio, 2)) + "\n"
            st += "Threshold = " + str(threshold)
            self.email(st, "Trade Signal", EMAILS)

        elif(signal < -threshold):
            st = "Sell Signal: \n"
            st += "Average Ratio = " + str(round(avg_ratio, 2)) + "\n"
            st += "Current Ratio = " + str(round(curr_ratio, 2)) + "\n"
            st += "Threshold = " + str(threshold)
            self.email(st, "Trade Signal", EMAILS)

    def email(self, message, sub, emails):

        curr_time = time.time()

        if(curr_time  - self.last_email_time > Utils.ratio_tracker_email_interval_seconds()):
            print(message)

            # msg = MIMEText(message)
            # msg["Subject"] = sub
            # msg["From"] = "siddharth.garg85@gmail.com"
            # msg["To"] = ",".join(emails)
            #
            # s = smtplib.SMTP('localhost')
            # s.send_message(msg)
            # s.quit()

            self.last_email_time  = curr_time

    def track(self, symbols, exchanges, price_funs, ratio_duration_seconds, threshold):

        hist_data1 = self.read_data(symbols[0], exchanges[0], ratio_duration_seconds)
        hist_data2 = self.read_data(symbols[1], exchanges[1], ratio_duration_seconds)

        avg_ratio, ratio_q  = self.average(hist_data1, hist_data2)

        print("Historic Average Ratio = " + str(round(avg_ratio, 2)))

        while(True):
            try:
                bid0, ask0 = price_funs[0]()
                bid1, ask1 = price_funs[1]()

                mid0 = Utils.mid(bid0, ask0)
                mid1 = Utils.mid(bid1, ask1)

                ratio = mid0 / mid1

                self.process(avg_ratio, ratio, threshold)

                r = ratio_q.get()
                ratio_q.put(ratio)
                avg_ratio = (avg_ratio * ratio_q.qsize() - r + ratio) / ratio_q.qsize()

            except:
                pass

            time.sleep(Utils.ratio_interval_seconds())

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description = "Ratio Tracker")
    arg_parser.add_argument('duration', help="Ratio Average Duration Seconds")
    arg_parser.add_argument('threshold', help = "Signal Threshold (%)")

    args = arg_parser.parse_args()

    ratio_tracker = RatioTracker()
    cr = CurrencyConverter()

    gpc = gdax_public_client.GDAXPublicClient()
    kpc = koinex_public_client.KoinexPublicClient()

    symbols = ["bitcoin", "BTC-USD"]
    exchanges = ["koinex", "gdax"]
    price_funs = [lambda: kpc.get_bid_ask(symbols[0]),
                  lambda: gpc.get_bid_ask(symbols[1], lambda: cr.convert("USD", "INR"))]

    ratio_tracker.track(symbols, exchanges, price_funs, int(args.duration), float(args.threshold))