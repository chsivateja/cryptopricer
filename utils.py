import datetime

class Utils:

    @staticmethod
    def get_date(minus_days):
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=minus_days)
        return (today - delta).strftime("%Y%m%d")


    @staticmethod
    def get_data_filename(data_dir, symbol, exchange, curr_date):
        return data_dir + "/" + exchange + "." + symbol.replace("/", "") + "." + curr_date + ".dat"

    @staticmethod
    def mid(bid, ask):
        return (bid + ask) / 2.0

    @staticmethod
    def ratio_interval_seconds():
        return 60

    @staticmethod
    def arb_interval_seconds():
        return 60 * 5

    @staticmethod
    def ratio_tracker_email_interval_seconds():
        return 1800

    @staticmethod
    def arb_tracker_email_interval_seconds():
        return 1800