import argparse
import logging
import sys

from bitfinex_ws_reader import  BitfinexWSReader
from basic_types import OrderSide, BookSide

LOGGER = logging.getLogger(__name__)


class MD:


    # Listeners need to have a method named on_market_update(security_id) which gets called on each update
    def __init__(self, orderbooks, listeners = []):
        self.symbols = orderbooks.keys()
        self.listeners = listeners;
        self.books = {}
        self.channel_to_symbol = {}

        for symbol in self.symbols:
            self.books[symbol] = MDBook(symbol, orderbooks[symbol])

    def connect(self, ws_address):
        self.reader = BitfinexWSReader()
        self.reader.init(ws_address, self.books.keys(), [self])


    def open(self):
        return

    def close(self):
        for book in self.books.values():
            book.close()
        return

    def start(self):
        self.reader.start()

    def stop(self):
        self.reader.stop()

    def on_message(self, **kwargs):
        m_json = kwargs["message"]

        if type(m_json) is dict:
            if "event" in m_json:
                if m_json["event"] == "subscribed":
                    self.__on_subscribe(m_json)

        elif type(m_json) is list:

            if(type(m_json[1]) == str and m_json[1] == "hb"):
                return

            len_message = len(m_json)

            if(len_message == 2):
                channel_id, elem_2 = m_json
                channel, symbol = self.channel_to_symbol[channel_id]

                if(channel == "trades"):
                    if (type(elem_2) is list):
                        self.__on_trades(channel_id, elem_2)
                elif(channel == "book"):
                    if(type(elem_2) is list):
                        for elem in elem_2:
                            elem.insert(0, channel_id)
                            self.__on_book(elem)

            elif(len_message == 4):
                self.__on_book(m_json)
            elif(len_message == 7):
                self.__on_trade(m_json)

    def __on_subscribe(self, m_json):
        channel_id = m_json["chanId"]
        symbol = m_json["pair"]
        channel = m_json["channel"]
        self.channel_to_symbol[channel_id] = (channel, symbol)

    def __on_book(self, m_json):
        channel_id, price, count, amount = m_json
        symbol = self.channel_to_symbol[channel_id][1]

        if symbol in self.books:
            book = self.books[symbol]
            book.on_book(price, count, amount)

            for l in self.listeners:
                l.on_market_update(symbol)

            LOGGER.debug(book.orderbook.toString(5))

    def __on_trades(self, channel_id, trades):
        channel, symbol = self.channel_to_symbol[channel_id]
        if symbol in self.books:
            book = self.books[symbol]

            trades.reverse()

            for t in trades:

                seq, timestamp, price, amount = t
                if (amount > 0):
                    side = OrderSide.BUY
                else:
                    side = OrderSide.SELL

                book.on_trade(side, price, amount, timestamp)

    def __on_trade(self, m_json):
        channel_id = m_json[0]
        timestamp = m_json[4]
        price = m_json[5]
        amount = m_json[6]

        channel, symbol = self.channel_to_symbol[channel_id]
        if symbol in self.books:
            book = self.books[symbol]

            if (amount > 0):
                side = OrderSide.BUY
            else:
                side = OrderSide.SELL

            book.on_trade(side, price, amount, timestamp)

            sid = SecurityManager().get_id_by_exchange_symbol(MD.EXCHANGE, symbol)

            for l in self.listeners:
                l.on_trade_update(sid)


class MDBook:

    def __init__(self, symbol, orderbook):
        self.symbol = symbol
        self.orderbook = orderbook
        self.orderbook.min_depth = 5

    def open(self):
        return

    def close(self):
        self.orderbook.clear()
        return

    def on_trade(self, side, price, amount, timestamp):
        self.orderbook.add_trade(side, price, amount, timestamp)

    def on_book(self, price, count, amount):

        if(amount > 0):
            side = BookSide.BID
        else:
            side = BookSide.ASK

        amount = abs(amount)

        if(count == 0):
            if (self.orderbook.has_price(side, price)):
                level = self.orderbook.level_at_price(side, price)
                self.orderbook.delete(side, price, level.amount, level.count)
        else:
            self.orderbook.add_or_modify(side, price, amount, count)

        LOGGER.debug(self.orderbook.toString(5))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    arg_parser = argparse.ArgumentParser(description = "Bitfinex Book Builder")

    args = arg_parser.parse_args()

    sm = SecurityManager()
    sm.init(configs.config.SECURITY_INFO_FILE)
    symbols = sm.get_ids_for_exchange(infra.metadata.markets.Exchange.BITFINEX)

    md = MD(symbols)

    # md.connect(ws_address = configs.config.BITFINEX_WS_ADDRESS)
    #
    # md.start()

    ex_conf = {
                "BITFINEX" : {
                       "data_dir":"/Users/siddharth/PycharmProjects/bitbet/raw_data",
                       "data_prefix": "bitfinex"
                    }
               }

    rdr = RecordedDataReader().init(ex_conf, "20170612")
    md.connect(mode="sim")
    md.start()