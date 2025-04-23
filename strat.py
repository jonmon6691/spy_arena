from datetime import datetime, timedelta


def as_float(cell: str):
    return float(cell.replace(",", ""))


class Day:
    def __init__(self, row):
        self.date = datetime.strptime(row[0], "%b %d, %Y")
        self.open = as_float(row[1])
        self.close = as_float(row[4])
        self.gain = float(self.close - self.open) / float(self.open)
        self.volume = as_float(row[6])

    def __repr__(self):
        return f"{self.open} - {self.close} : {self.gain*100:+.2}"


class Strat:
    initial_cash = 1000.0

    def __init__(self, data):
        self.balance: float = Strat.initial_cash
        self.shares: float = 0.0
        self.first_day: datetime = min(data.keys())
        self.last_day: datetime = max(data.keys())
        self.data = data

    def run(self):
        yesterday = None
        for i in range((self.last_day - self.first_day).days):
            try:
                today = self.data[self.first_day + timedelta(days=i)]
                if yesterday is not None:
                    self.daily_action(today, yesterday)
                yesterday = today
            except KeyError:
                pass

    def buyall_at_open(self, today):
        self.shares += self.balance / today.open
        self.balance = 0.0

    def buyall_at_close(self, today):
        self.shares += self.balance / today.close
        self.balance = 0.0

    def sellall_at_open(self, today):
        self.balance += today.open * self.shares
        self.shares = 0

    def sellall_at_close(self, today):
        self.balance += today.close * self.shares
        self.shares = 0

    def annualized_gain(self):
        value = self.balance + self.data[self.last_day].close * self.shares
        gain = (value - Strat.initial_cash)/Strat.initial_cash * 100
        return gain * 365 / (self.last_day - self.first_day).days

    def __repr__(self):
        value = self.balance + self.data[self.last_day].close * self.shares
        gain = (value - Strat.initial_cash)/Strat.initial_cash * 100
        return f"{self.__class__.__name__}\n" +\
            f"\t{self.balance=:.2f} {self.shares=}\n" +\
            f"\tValue: {value:0.2f} ({self.get_gain_per_year():+0.2f}%)"
