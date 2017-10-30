import requests
import datetime

class CurrencyConverter:

    def __init__(self):
        self.today = ""
        self.price = 0

    def convert(self, base, to):
        today = datetime.datetime.now().strftime("%Y%m%d")

        if(self.today != today):
            r = requests.get("http://api.fixer.io/latest?base=" + base + "&symbols=" + to)
            self.price = r.json()["rates"][to]
            self.today = today


        return self.price