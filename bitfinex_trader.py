import time

from bitfinex_trade_client import BitfinexClient,BitfinexTradeClient
from koinex_public_client import KoinexPublicClient
from currency_converter import CurrencyConverter

KEY = "nBi8YyJZZ9ZhSOf2jEpMAoBpzKt2Shh6IoLdTjFRYvb"
SECRET = "XO6FUYbhFYqBflXYSaKMiu1hGHLhGf63xsOK0Pf7osA"

class EMA:
    def __init__(self, duration):
        self.value = 0

        self.duration = duration
        self.count = 0
        self.multiplier = 2.0 / (self.duration + 1)

    def update(self, px):
        if(self.count < self.duration):
            self.count += 1
            multiplier = 2.0/(self.count + 1)
            self.value = multiplier * px + (1 - multiplier) * self.value
        else:
            self.value = self.multiplier * px + (1 - self.multiplier) * self.value

    def ready(self):
        return (self.count >= self.duration * 0.05)

class Order:
    def __init__(self, amount, price, side, ord_type, symbol):
        self.amount = amount
        self.price = price
        self.side = side
        self.ord_type = ord_type
        self.symbol = symbol
        self.traded_amount = 0
        self.traded_px = 0
        self.id = -1

    def __str__(self):
        return "Order => Amount:" + str(self.amount) + "|Price:" + str(self.price) + "|Side:" + str(self.side)

class BitfinexTrader:
    def __init__(self, key, secret, symbol, koinex_symbol,  amount, interval, duration, threshold):
        self.symbol = symbol

        self.sym1 = symbol[:3]
        self.sym2 = symbol[3:]

        self.koinex_symbol = koinex_symbol

        self.trade_client = BitfinexTradeClient(key, secret)
        self.client = BitfinexClient()
        self.koinex_client = KoinexPublicClient()
        self.currency_client = CurrencyConverter()

        self.amount = amount
        self.interval = interval
        self.duration = int(duration / interval)
        self.threshold = threshold
        self.fees_per = self.get_fees()

        self.ema = EMA(self.duration)

        self.buy_order = None
        self.sell_order = None

        self.buy_position = 0
        self.buy_px = 0
        self.sell_position = 0
        self.sell_px = 0

        self.last_email_time = 0

        self.run = True

    def get_fees(self):
        account_info = self.trade_client.account_info()
        return float(account_info[0]["maker_fees"])

    def get_pnl(self, ticker):
        pos = max(self.buy_position, self.sell_position)

        bid = float(ticker['bid'])
        ask = float(ticker['ask'])

        buy_avg_px = ((pos - self.buy_position) * ask + self.buy_position * self.buy_px) / pos
        sell_avg_px = ((pos - self.sell_position) * bid + self.sell_position * self.sell_px) / pos

        cost = (buy_avg_px + sell_avg_px) * pos * self.fees_per / 100.0

        return pos * (sell_avg_px - buy_avg_px) - cost

    def get_pnl_koinex(self):
        pos = max(self.buy_position, self.sell_position)

        bid, ask = self.koinex_client.get_bid_ask(self.koinex_symbol)

        px_base = self.currency_client.convert("INR", self.sym2.upper())

        bid = px_base * bid
        ask = px_base * ask

        buy_avg_px = ((pos - self.buy_position) * ask + self.buy_position * self.buy_px) / pos
        sell_avg_px = ((pos - self.sell_position) * bid + self.sell_position * self.sell_px) / pos

        cost = (buy_avg_px + sell_avg_px) * pos * self.fees_per / 100.0

        return pos * (sell_avg_px - buy_avg_px) - cost

    def buy_sell_px(self):
        buy_px = round(self.ema.value * (1 - self.threshold / 100.0))
        sell_px = round(self.ema.value * (1 + self.threshold / 100.0))

        return (buy_px, sell_px)

    def can_buy(self, buy_px, bid):
        return (buy_px >= bid and self.net_position() < self.amount)

    def can_sell(self, sell_px, ask):
        return (self.net_position() > 0)

    def net_position(self):
        return (self.buy_position - self.sell_position)

    def update_order_status(self):
        try:
            if(self.buy_order != None):
                status = self.trade_client.status_order(self.buy_order.id)
                print(status)

                executed_amount = float(status["executed_amount"])
                executed_px = float(status["avg_execution_price"])

                new_executed_amount = executed_amount - self.buy_order.traded_amount

                if (new_executed_amount > 0):
                    new_executed_px = (executed_amount * executed_px - self.buy_order.traded_amount * self.buy_order.traded_px) / new_executed_amount

                    self.buy_order.traded_amount = executed_amount
                    self.buy_order.traded_px = executed_px

                    self.buy_px = (self.buy_px * self.buy_position + new_executed_amount * new_executed_px) / (self.buy_position + new_executed_amount)
                    self.buy_position += new_executed_amount

                if(not status["is_live"]):
                    self.buy_order = None

            if (self.sell_order != None):
                status = self.trade_client.status_order(self.sell_order.id)
                print(status)

                executed_amount = float(status["executed_amount"])
                executed_px = float(status["avg_execution_price"])

                new_executed_amount = executed_amount - self.sell_order.traded_amount

                if(new_executed_amount > 0):
                    new_executed_px = (executed_amount * executed_px - self.sell_order.traded_amount * self.sell_order.traded_px) / new_executed_amount

                    self.sell_order.traded_amount = executed_amount
                    self.sell_order.traded_px = executed_px

                    self.sell_px = (self.sell_px * self.sell_position + new_executed_amount * new_executed_px) / (self.sell_position + new_executed_amount)
                    self.sell_position += new_executed_amount

                if (not status["is_live"]):
                    self.sell_order = None

            print("Position => BuyPos:" + str(self.buy_position) + "|BuyPx:" + str(self.buy_px) + "|SellPos:" + str(self.sell_position) + "|SellPx:" + str(self.sell_px))

        except Exception as e:
            print("Update Order Status Exception: " + str(e))
            pass

    def sqoff(self, ticker):
        if(self.net_position() > 0):
            try:
                koinex_pnl = self.get_pnl_koinex()
                pnl = self.get_pnl(ticker)

                print("PNL => Bitfinex:" + str(pnl) + "|Koinex:" + str(koinex_pnl))

                if((koinex_pnl - pnl) / (koinex_pnl + pnl) * 2 * 100.0 < 2.0):
                    self.email("Bitfinex Trader Alert: Sqoff in koinex", "Bitfinex Trader Alert: Sqoff in koinex", ["siddharth.garg85@gmail.com"])
                    return True
            except Exception as e:
                print("Sqoff Exception: " + str(e))
                return False

        return False


    def email(self, message, sub, emails):

        curr_time = time.time()

        if (curr_time - self.last_email_time > 1800):
            print(message)

    def trade(self):
        while (self.run):
            time.sleep(self.interval)

            ticker = None

            try:
                    ticker = self.client.ticker(self.symbol)
            except Exception as e:
                print("Trade Exception: " + str(e))
                continue

            self.update_order_status()
            self.ema.update(ticker['mid'])

            if(self.ema.ready()):
                if (not self.sqoff(ticker)):
                    buy_px, sell_px = self.buy_sell_px()

                    bid = ticker['bid']
                    ask = ticker['ask']

                    buy_px = min(bid, buy_px)
                    sell_px = max(ask , sell_px)

                    print("Market => BuyPx:" + str(buy_px) + "|SellPx:" + str(sell_px) + "|Bid:" + str(bid) + "|Ask:" + str(ask))

                    if(self.can_buy(buy_px, bid)):
                        if(self.buy_order == None):
                            amount = self.amount - max(0, self.net_position())
                            self.buy_order = Order(amount, buy_px, "buy", "exchange limit", self.symbol)

                            print(self.buy_order)

                            status = self.trade_client.place_order(str(amount), str(buy_px), "buy", "exchange limit", True, self.symbol)
                            print(status)

                            if ("order_id" in status):
                                self.buy_order.id = status["order_id"]
                            else:
                                self.buy_order = None
                        else:
                            if(abs(self.buy_order.price - buy_px) / buy_px * 100.0 > self.threshold / 10.0 ):
                                self.trade_client.delete_order(self.buy_order.id)

                    if (self.can_sell(sell_px, ask)):
                        if (self.sell_order == None):
                            amount = self.net_position()
                            self.sell_order = Order(amount, sell_px, "sell", "exchange limit", self.symbol)

                            print(self.sell_order)

                            status = self.trade_client.place_order(str(amount), str(sell_px), "sell", "exchange limit", True, self.symbol)
                            print(status)

                            if("order_id" in status):
                                self.sell_order.id = status["order_id"]
                            else:
                                self.sell_order = None

                        else:
                            if (abs(self.sell_order.price - sell_px) / sell_px * 100.0 > self.threshold / 10.0 or self.sell_order.amount < amount):
                                self.trade_client.delete_order(self.sell_order.id)


