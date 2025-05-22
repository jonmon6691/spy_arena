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
        gains.append(s)

    gains = sorted(gains, key=lambda x: x.annualized_gain())
    return gains


if __name__ == "__main__":
    import multiprocessing
    import matplotlib.pyplot as plt
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
    n_trials = 100

    # Load data
    rows = csv.reader(open(filename, "r"))
    next(rows)  # Skip header
    data = sorted([Day(row) for row in rows], key=lambda x: x.date)

    # Generate set of trials
    random.seed(b"diamondhandsalsothegame")
    trials = []
    random_length_trials = False
    if random_length_trials:
        while len(trials) < n_trials:
            start, end = tuple(
                sorted([random.randint(0, len(data)), random.randint(0, len(data))]))
            if 100 < (end - start) < 10000:
                trials.append((start, end))
    else:
        t_len = 1000
        while len(trials) < n_trials:
            start = random.randint(0, len(data) - t_len)
            trials.append((start, start + t_len))

    # Execute trials
    num_processes = min(len(strats), os.cpu_count())
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(try_strat, [(s, data, trials) for s in strats])

    # Plot
    fig, ax = plt.subplots(figsize=(18,10))
    ax.set_xlabel("Days since start")

    # Print results
    f = csv.writer(open("data.csv", "w", newline=""))
    f.writerow(["strat", "stat", "Day", "chart"])
    print(f"{n_trials=}")
    for strat, gains in zip(strats, results):
        min_ = gains[0]
        q1 = gains[len(gains) // 4]
        med = gains[len(gains) // 2]
        q3 = gains[len(gains) * 3 // 4]
        max = gains[-1]

        ax.set_ylabel(strat.__name__)
        for t in gains:
            ax.plot(range(len(t.value_chart)), t.value_chart, linewidth=0.5, alpha=0.2, color='blue')

        print(f"{strat.__name__} - {strat.__doc__}")
        print("              Gain     Trial Period                  Cal days  Trading days")
        print(f"\tmin = {min_}")
        print(f"\tq1  = {q1}")
        print(f"\tmed = {med}")
        print(f"\tq3  = {q3}")
        print(f"\tmax = {max}\n")

        for i, closing_price in enumerate(min_.value_chart):
            f.writerow([strat.__name__, "min", i, closing_price])
        for i, closing_price in enumerate(q1.value_chart):
            f.writerow([strat.__name__, "q1", i, closing_price])
        for i, closing_price in enumerate(med.value_chart):
            f.writerow([strat.__name__, "med", i, closing_price])
        for i, closing_price in enumerate(q3.value_chart):
            f.writerow([strat.__name__, "q3", i, closing_price])
        for i, closing_price in enumerate(max.value_chart):
            f.writerow([strat.__name__, "max", i, closing_price])

    plt.tight_layout()
    plt.show()