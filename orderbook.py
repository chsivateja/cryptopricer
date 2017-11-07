from sortedcontainers import SortedDict
from collections import deque
import constants
from basic_types import BookSide

class OrderBookLevel:
    def __init__(self, side, price, amount, count):
        self.side = side
        self.price = price
        self.amount = amount
        self.count = count


class TradeInfo:
    __ID = 0

    def __init__(self, side, price, amount, timestamp):
        self.side = side
        self.price = price
        self.amount = amount
        self.timestamp = timestamp
        self.id = TradeInfo.__ID + 1

class TradesInfo:
    def __init__(self, max_length=20):
        self.max_length = max_length
        self.trades = deque([])

    def append(self, trade):
        self.trades.append(trade)

        while(len(self.trades) > self.max_length):
            self.trades.popleft()


class OrderBookSide:

    def __init__(self, side):
        self.bookSide = side
        if side == BookSide.BID:
            self.levels = SortedDict(lambda x:-x)
        else:
            self.levels = SortedDict()

    def depth(self):
        return len(self.levels)

    def price(self, num = 0):
        level = self.levels.peekitem(num)[1]
        return level.price

    def count(self, num = 0):
        level = self.levels.peekitem(num)[1]
        return level.count

    def amount(self, num = 0):
        level = self.levels.peekitem(num)[1]
        return level.amount

    def level(self, num):
        return self.levels.peekitem(num)[1]

    def has_price(self, price):
        return (price in self.levels)

    def index(self, price):
        return self.levels.index(price)

    def level_at_price(self, price):
        return self.levels[price]

    def add(self, price, amount, count):

        if price not in self.levels:
            self.levels[price] = OrderBookLevel(self.bookSide, price, 0, 0)

        level = self.levels[price]
        level.amount += amount
        level.count += count

    def clear(self):
        self.levels.clear()

    def delete(self, price, amount, count):
        level = self.levels[price]
        level.amount -= amount
        level.count -= count

        if(level.count == 0 or level.amount <= constants.ONE_SATOSHI):
            del self.levels[price]

    def get_top_levels(self, num):
        i = 0
        l = []
        for k,v in self.levels.iteritems():
            l.append(v)
            i += 1
            if(i == num):
                break

        while(i<num):
            l.append(OrderBookLevel(self.bookSide, 0, 0, 0))
            i += 1

        return l

class OrderBook:

    def __init__(self, symbol, min_depth = 5, has_count = True):
        self.symbol = symbol
        self.books = [None, None]
        self.min_depth = min_depth
        self.books[BookSide.BID.value] = OrderBookSide(BookSide.BID)
        self.books[BookSide.ASK.value] = OrderBookSide(BookSide.ASK)
        self.trades = [TradesInfo(), TradesInfo()]
        self.last_update_level = -1

    def add_trade(self, side, price, amount, timestamp):
        trade = TradeInfo(side, price, amount, timestamp)
        self.trades[side.value].append(trade)

    def ready(self):
        if(self.books[BookSide.BID.value].depth() >= self.min_depth and
                   self.books[BookSide.ASK.value].depth() >= self.min_depth):
            return True
        else:
            return False

    def clear(self):
        self.books[BookSide.BID.value].clear()
        self.books[BookSide.ASK.value].clear()

    def depth(self, side):
        return self.books[side.value].depth()

    def price(self, side, num = 0):
        return self.books[side.value].price(num)

    def mid(self):
        return (self.price(BookSide.BID) + self.price(BookSide.ASK)) / 2.0

    def count(self, side, num = 0):
        return self.books[side.value].count(num)

    def amount(self, side, num = 0):
        return self.books[side.value].amount(num)

    def level(self, side, num):
        return self.books[side.value].level(num)

    def level_at_price(self, side, price):
        return self.books[side.value].level_at_price(price)

    def has_price(self, side, price):
        return self.books[side.value].has_price(price)

    def add(self, side, price, amount, count):
        self.books[side.value].add(price, amount, count)
        self.last_update_level = self.books[side.value].index(price)

    def add_or_modify(self, side, price, amount, count):
        if (self.has_price(side, price)):
            level = self.level_at_price(side, price)
            level.count = count
            level.amount = amount
        else:
            self.books[side.value].add(price, amount, count)

        self.last_update_level = self.books[side.value].index(price)

    def delete(self, side, price, amount, count):
        self.last_update_level = self.books[side.value].index(price)
        self.books[side.value].delete(price, amount, count)

    def toString(self, levels):
        bids = self.books[BookSide.BID.value].get_top_levels(levels)
        asks = self.books[BookSide.ASK.value].get_top_levels(levels)
        str = "\n"

        for i in range(0, levels):
            str += "%16.8f %18.8f | %-20.8f %-16.8f\n" % \
                   (bids[i].amount, bids[i].price, asks[i].price,
                    asks[i].amount)

        return str


