from bitfinex_trade_client import BitfinexClient,BitfinexTradeClient
import time

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
        return str(self.amount) + "|" + str(self.price) + "|" + str(self.side)

class BitfinexTrader:
    def __init__(self, symbol, koinex_symbol,  amount, interval, duration, threshold):
        self.symbol = symbol

        self.sym1 = symbol[:3]
        self.sym2 = symbol[3:]

        self.koinex_symbol = koinex_symbol
        self.trade_client = BitfinexTradeClient(KEY,SECRET)
        self.client = BitfinexClient()
        self.amount = amount
        self.interval = interval
        self.duration = duration
        self.threshold = threshold
        self.ema = EMA(self.duration)

        self.buy_order = None
        self.sell_order = None

        self.buy_position = 0
        self.buy_px = 0
        self.sell_position = 0
        self.sell_px = 0

        self.run = True

    def buy_sell_px(self):
        buy_px = round(self.ema.value * (1 - self.threshold / 100.0))
        sell_px = round(self.ema.value * (1 + self.threshold / 100.0))

        return (buy_px, sell_px)

    def can_buy(self, buy_px, bid):
        return (bid <= buy_px and self.net_position() < self.amount)

    def can_sell(self, sell_px, ask):
        return (ask >= sell_px and self.net_position() > 0 and -self.net_position() < self.amount)

    def net_position(self):
        return (self.buy_position - self.sell_position)

    def update_order_status(self):
        if(self.buy_order != None):
            status = self.trade_client.status_order(self.buy_order.id)
            executed_amount = status["executed_amount"]
            executed_px = status["avg_execution_price"]

            new_executed_amount = executed_amount - self.buy_order.traded_amount
            new_executed_px = (executed_amount * executed_px - self.buy_order.traded_amount * self.buy_order.traded_px) / new_executed_amount

            self.buy_order.traded_amount = executed_amount
            self.buy_order.traded_px = executed_px

            self.buy_px = (self.buy_px * self.buy_position + new_executed_amount * new_executed_px)/(self.buy_position + new_executed_amount)
            self.buy_position += new_executed_amount

            if(not status["is_live"]):
                self.buy_order = None

        if (self.sell_order != None):
            status = self.trade_client.status_order(self.sell_order.id)
            executed_amount = status["executed_amount"]
            executed_px = status["avg_execution_price"]

            new_executed_amount = executed_amount - self.sell_order.traded_amount
            new_executed_px = (executed_amount * executed_px - self.sell_order.traded_amount * self.sell_order.traded_px) / new_executed_amount

            self.sell_order.traded_amount = executed_amount
            self.sell_order.traded_px = executed_px

            self.sell_px = (self.sell_px * self.sell_position + new_executed_amount * new_executed_px) / (self.sell_position + new_executed_amount)
            self.sell_position += new_executed_amount

            if (not status["is_live"]):
                self.sell_order = None

    def trade(self):
        while(self.run):

            ticker = None

            try:
                ticker = self.client.ticker(self.symbol)
            except:
                continue

            print(ticker)
            self.ema.update(ticker['mid'])
            self.update_order_status()

            if(self.ema.ready()):
                buy_px, sell_px = self.buy_sell_px()
                bid = ticker['bid']
                ask = ticker['ask']

                print(str(buy_px) + "|" + str(sell_px) + " " + str(bid) + "|" + str(ask))

                if(self.can_buy(buy_px, bid)):
                    if(self.buy_order == None):
                        amount = self.amount - max(0, self.net_position())
                        self.buy_order = Order(amount, bid, "buy", "exchange limit", self.symbol)
                        print(self.buy_order)
                        status = {} #self.trade_client.place_order(amount, bid, "buy", "exchange limit", True, self.symbol)

                        if ("order_id" in status):
                            self.buy_order.id = status["order_id"]
                        else:
                            self.buy_order = None
                    else:
                        if(abs(self.buy_order.price - bid)/bid > self.threshold / 10.0 ):
                            self.trade_client.delete_order(self.buy_order.id)

                if (self.can_sell(sell_px, ask)):
                    amount = self.net_position()
                    if (self.sell_order == None):
                        self.sell_order = Order(amount, ask, "sell", "exchange limit", self.symbol)

                        print(self.sell_order)

                        status = {}#self.trade_client.place_order(amount, ask, "sell", "exchange limit", True, self.symbol)

                        if("order_id" in status):
                            self.sell_order.id = status["order_id"]
                        else:
                            self.sell_order = None

                    else:
                        if (abs(self.sell_order.price - ask) / ask > self.threshold / 10.0 or self.sell_order.amount < amount):
                            self.trade_client.delete_order(self.sell_order.id)

            time.sleep(self.interval)

