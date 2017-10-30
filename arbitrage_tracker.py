import koinex_public_client
import zebpay_public_client

import time
from utils import Utils

import smtplib
from email.mime.text import MIMEText
import argparse

EMAILS = ["siddharth.garg85@gmail.com", "jackson.garg@gmail.com"]

class ArbitrageTracker:

    def __init__(self):
        self.last_email_time = 0

    def track(self, symbols, exchanges, price_funs, threshold):

        while(True):
            try:
                bid0, ask0 = price_funs[0]()
                bid1, ask1 = price_funs[1]()

                if((bid0 - ask1) / ask1 * 100.0 > threshold):
                    st = "Arbitrage\n"
                    st += "Buy " + symbols[1] + ":" + exchanges[1] + "@" + str(ask1) + "\n"
                    st += "Sell " + symbols[0] + ":" + exchanges[0] + "@" + str(bid0)

                    self.email(st, "Arbitrage Strategy Opportunity", EMAILS)

                elif((bid1 - ask0) / ask0 * 100.0 > threshold):
                    st = "Arbitrage\n"
                    st += "Buy " + symbols[0] + ":" + exchanges[0] + "@" + str(ask0) + "\n"
                    st += "Sell " + symbols[1] + ":" + exchanges[1] + "@" + str(bid1)

                    self.email(st, "Arbitrage Strategy Opportunity", EMAILS)

            except:
                pass

            time.sleep(Utils.arb_interval_seconds())


    def email(self, message, sub, emails):
        curr_time = time.time()

        if (curr_time - self.last_email_time > Utils.ratio_tracker_email_interval_seconds()):
            print(message)

            msg = MIMEText(message)
            msg["Subject"] = sub
            msg["From"] = "siddharth.garg85@gmail.com"
            msg["To"] = ",".join(emails)

            s = smtplib.SMTP('localhost')
            s.send_message(msg)
            s.quit()

            self.last_email_time = curr_time


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Arbitrage Tracker")
    arg_parser.add_argument('threshold', help="Arbitrage Threshold (%)")

    args = arg_parser.parse_args()

    arb_tracker = ArbitrageTracker()
    zpc = zebpay_public_client.ZebpayPublicClient()
    kpc = koinex_public_client.KoinexPublicClient()

    symbols = ["btc/inr", "bitcoin"]
    exchanges = ["zebpay", "koinex"]
    price_funs = [lambda : zpc.get_bid_ask(symbols[0]), lambda : kpc.get_bid_ask(symbols[1])]

    arb_tracker.track(symbols, exchanges, price_funs, float(args.threshold))