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
        self.value_chart = []

    def run(self):
        yesterday = self.first_day
        for i in range(1, (self.last_day - self.first_day).days):
            today = self.first_day + timedelta(days=i)
            if today in self.data:
                self.daily_action(self.data[today], self.data[yesterday])
                self.value_chart.append(self.get_value(today))
                yesterday = today

    def buyall_at_open(self, today):
        self.shares += self.balance / today.open
        self.balance = 0.0

    def buyall_at_close(self, today):
        self.shares += self.balance / today.close
        self.balance = 0.0

    def sellall_at_open(self, today):
        self.balance += self.shares * today.open
        self.shares = 0.0

    def sellall_at_close(self, today):
        self.balance += self.shares * today.close
        self.shares = 0.0

    def get_value(self, day):
        return self.balance + self.data[day].close * self.shares

    def annualized_gain(self):
        value = self.get_value(self.last_day)
        gain = (value - Strat.initial_cash)/Strat.initial_cash
        return gain * 365 / (self.last_day - self.first_day).days

    def __repr__(self):
        return f"{self.annualized_gain():7.2%} [{self.first_day.strftime('%b %d, %Y')} - {self.last_day.strftime('%b %d, %Y')}], {(self.last_day - self.first_day).days:8}, {len(self.data):12}"  
