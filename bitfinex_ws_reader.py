import sys
import json
import websocket
import logging

LOGGER = logging.getLogger(__name__)

class BitfinexWSReader:

    def init(self, ws_address, symbols, listeners):
        self.ws_address=ws_address
        self.received_ob = False
        self.symbols = symbols
        self.listeners = listeners
        self.retry_count = 0
        self.stopped = False
        self.channel_symbol = {}

        print("Created Bitfinex web socket using websocket address "
                    + ws_address + " for symbols " + str(symbols))


    def on_message(self, ws, message):

        for l in self.listeners:
            l.on_message(message = json.loads(message))


    def on_error(self, ws, error):
        LOGGER.error(error)

    def on_close(self, ws):
        for l in self.listeners:
            l.close()

        LOGGER.info("Closed websocket")

    def on_open(self, ws):
        self.retry_count = 0
        for sym in self.symbols:
            req_book = {
                "event"   : "subscribe",
                "channel" : "book",
                "pair"    : sym,
                "prec"    : "P0",
                "freq"    : "F0"
            }

            ws.send(json.dumps(req_book))

            req_trade = {
                "event": "subscribe",
                "channel": "trades",
                "pair": sym
            }

            ws.send(json.dumps(req_trade))

    def start(self, auto_reconnect = False, retries = 3):

        for l in self.listeners:
            l.open()

        self.ws = websocket.WebSocketApp(self.ws_address,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

        print("Connecting to bitfinex websocket")

        if (not auto_reconnect):
            self.ws.run_forever()
        else:
            while (self.retry_count < retries and not self.stopped):
                self.ws.run_forever()
                self.retry_count += 1


    def stop(self):
        self.stopped = True
        self.ws.close()
