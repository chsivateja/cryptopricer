from enum import Enum

class BookSide(Enum):
    BID = 0
    ASK = 1

    @staticmethod
    def toBookSide(str):
        if(str.lower() == "buy"):
            return BookSide.BID
        else:
            return BookSide.ASK

    def __str__(self):
        return self.name


class OrderSide(Enum):
    BUY = BookSide.BID.value
    SELL = BookSide.ASK.value

    @staticmethod
    def toOrderSide(str):
        if (str.lower() == "buy" or str.lower() == "bid"):
            return OrderSide.BUY
        else:
            return OrderSide.SELL

    def __str__(self):
        return self.name


class OrderStatus(Enum):
    NEW = 0
    CONFIRMED = 1
    TRADED = 2
    CANCELLED = 3
    REJECTED = 4

    def __str__(self):
        return self.name


class OrderType(Enum):
    LIMIT = 0
    MARKET = 1

    @staticmethod
    def toOrderType(str):
        str = str.lower()
        if(str == "limit"):
            return OrderType.LIMIT
        elif(str == "market"):
            return OrderType.MARKET

    def __str__(self):
        return self.name


class TimeInForce(Enum):
    DAY = 0
    IOC = 1

    def __str__(self):
        return self.name
