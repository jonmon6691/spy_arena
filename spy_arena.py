#!/bin/env python3
from strat import Day, Strat

# Class decorator that enlists the strategy type in the simulation run
strats = []
def run(strat):
    strats.append(strat)
    return strat


@run
class Long(Strat):
    """ Invest as early as possible... hodl... profit."""

    def daily_action(self, today: Day, yesterday: Day):
        if self.balance > 0:
            self.buyall_at_open(yesterday)


@run
class Opposite(Strat):
    """What goes up must come down"""

    def daily_action(self, today: Day, yesterday: Day):
        if  yesterday.open < yesterday.close:
            # Sell if yesterday was up, must come down
            self.sellall_at_open(today)
        else:
            # Buy if yesterday was down, most go up
            self.buyall_at_open(today)


@run
class Opposite2(Strat):
    """Like Opposite, but only sell if today opened lower than yesterday closed"""

    def daily_action(self, today: Day, yesterday: Day):
        if  yesterday.open < yesterday.close:
            # Sell if yesterday was up and opening isn't higher
            if today.open < yesterday.close:
                self.sellall_at_open(today)
        else:
            # Buy if yesterday was down
            self.buyall_at_open(today)


@run
class SellHigh(Strat):
    """Buy low, sell high"""

    def daily_action(self, today: Day, yesterday: Day):
        if yesterday.close > today.open:
            self.buyall_at_open(today)

        if today.open < today.close:
            self.sellall_at_close(today)


@run
class SellHigh2(Strat):
    """That sucks, lets do the opposite"""

    def daily_action(self, today: Day, yesterday: Day):
        if yesterday.close < today.open:
            self.buyall_at_open(today)

        if today.open > today.close:
            self.sellall_at_close(today)


@run
class SellHigh3(Strat):
    """Accidentally discovered with a typo :)"""

    def daily_action(self, today: Day, yesterday: Day):
        if yesterday.close < today.open:
            self.buyall_at_open(today)

        if today.open < today.close:
            self.sellall_at_close(today)


@run
class DCA(Strat):
    """Dollar Cost Averaging... doesn't really work in a sumlation where the strategy assumes no outside money coming in"""

    def daily_action(self, today: Day, yesterday: Day):
        if "daily_ammount" not in self.__dir__():
            self.daily_ammount = self.balance / (len(self.data) - 1)
        self.shares += self.daily_ammount / today.open
        self.balance -= self.daily_ammount

#@run
class VolatilityAverse(Strat):
    """Get out of the market when yesterday was a big volumne day. Needs work to handle historically variable volume i.e. no magic number"""

    def daily_action(self, today: Day, yesterday: Day):
        if yesterday.volume > 4000000000:
            self.sellall_at_open(today)
        else:
            self.buyall_at_open(today)


def try_strat(strat: type, data, trials):
    """Worker thread that runs through all the trials in a given strat"""
    gains = []
    for start, end in trials:
        s = strat(data={day.date: day for day in data[start:end]})
        s.run()
        gains.append((s.annualized_gain(), (s.first_day.strftime(
            "%b %d, %Y"), s.last_day.strftime("%b %d, %Y")), (s.last_day - s.first_day).days, len(s.data)))

    gains = sorted(gains, key=lambda x: x[0])
    return gains


if __name__ == "__main__":
    import multiprocessing
    import os
    import csv
    import random

    # Pulled from yahoo finance historical data (inspect element, copy <table>...</table>)
    # Converted to CSV using https://www.convertcsv.com/html-table-to-csv.htm
    #
    # Header
    #     0       1       2      3       4         5           6
    # ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    # Note: pre April 1982 seems glitched (opening = 0.0) so this is only data after that
    filename = "sp500_all_daily.csv"
    n_trials = 1000

    # Load data
    rows = csv.reader(open(filename, "r"))
    next(rows)  # Skip header
    data = sorted([Day(row) for row in rows], key=lambda x: x.date)

    # Generate set of trials
    random.seed(b"diamondhandsalsothegame")
    trials = []
    while len(trials) < n_trials:
        start, end = tuple(
            sorted([random.randint(0, len(data)), random.randint(0, len(data))]))
        if 100 < (end - start) < 10000:
            trials.append((start, end))

    # Execute trials
    num_processes = min(len(strats), os.cpu_count())
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(try_strat, [(s, data, trials) for s in strats])

    # Print results
    print(f"{n_trials=}")
    pp = lambda g: f"{g[0]:7.2%} [{g[1][0]} - {g[1][1]}], {g[2]:8}, {g[3]:12}"
    for strat, gains in zip(strats, results):
        print(f"{strat.__name__} - {strat.__doc__}")
        print("              Gain     Trial Period                  Cal days  Trading days")
        print(f"\tmin = {pp(gains[0])}")
        print(f"\tq1  = {pp(gains[len(gains) // 4])}")
        print(f"\tmed = {pp(gains[len(gains) // 2])}")
        print(f"\tq3  = {pp(gains[len(gains) * 3 // 4])}")
        print(f"\tmax = {pp(gains[-1])}\n")
