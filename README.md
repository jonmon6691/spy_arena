# spy_arena
Toy framework to test basic trading strategies based only on intraday historical data

## Data source

1. Pulled from yahoo finance historical data (inspect element, copy \<table\>...\</table\>)
<br />i.e. https://finance.yahoo.com/quote/%5EGSPC/history/

2. Converted to CSV using https://www.convertcsv.com/html-table-to-csv.htm

## Random sampling

Strategies are executed thousands of times using random date ranges, then performance statistics are printed per-strategy

## Example output
Note: Gain is annualized
```
n_trials=1000
Long -  Invest as early as possible... hodl... profit.
              Gain     Trial Period                  Cal days  Trading days
        min = -17.22% [Feb 27, 1987 - Nov 12, 1987],      258,          181
        q1  =   7.91% [Jul 13, 1987 - Oct 11, 1993],     2282,         1582
        med =  12.11% [May 31, 1996 - Dec 19, 2018],     8237,         5678
        q3  =  19.91% [Aug 11, 2005 - Feb 21, 2025],     7134,         4914
        max =  39.71% [Nov 25, 1985 - Jul 18, 2018],    11923,         8229

Opposite - What goes up must come down
              Gain     Trial Period                  Cal days  Trading days
        min = -38.33% [Feb 27, 1987 - Nov 12, 1987],      258,          181
        q1  =   8.16% [Nov 16, 2009 - Feb 06, 2019],     3369,         2321
        med =  13.81% [Jun 27, 1996 - Nov 12, 2009],     4886,         3369
        q3  =  18.70% [Sep 26, 2005 - Jul 11, 2019],     5036,         3471
        max =  34.40% [Apr 04, 2002 - Feb 03, 2023],     7610,         5247

Opposite2 - Like Opposite, but only sell if today opened lower than yesterday closed
              Gain     Trial Period                  Cal days  Trading days
        min =  -9.86% [Feb 27, 1987 - Nov 12, 1987],      258,          181
        q1  =  19.16% [Feb 25, 2015 - Dec 12, 2018],     1386,          958
        med =  51.83% [Jul 02, 2003 - Oct 13, 2011],     3025,         2088
        q3  = 123.35% [May 20, 1992 - Mar 25, 2015],     8344,         5755
        max = 533.73% [Nov 25, 1985 - Jul 18, 2018],    11923,         8229

SellHigh - Buy low, sell high
              Gain     Trial Period                  Cal days  Trading days
        min = -52.50% [Feb 27, 1987 - Nov 12, 1987],      258,          181
        q1  =  -5.89% [Mar 29, 2011 - Jun 22, 2021],     3738,         2576
        med =  -3.91% [Sep 12, 1995 - Dec 03, 2015],     7387,         5094
        q3  =  -2.76% [May 06, 1992 - May 15, 2023],    11331,         7814
        max =   7.46% [Oct 14, 2003 - Dec 20, 2007],     1528,         1055

SellHigh2 - That sucks, lets do the opposite
              Gain     Trial Period                  Cal days  Trading days
        min =   0.02% [Feb 05, 2002 - Aug 31, 2007],     2033,         1404
        q1  =  12.14% [Sep 11, 1990 - Dec 09, 1996],     2281,         1581
        med =  30.53% [Aug 01, 1991 - Aug 29, 2013],     8064,         5564
        q3  =  75.42% [Dec 18, 2006 - Sep 23, 2015],     3201,         2206
        max = 178.51% [Mar 24, 2009 - Sep 09, 2024],     5648,         3892

DCA - Dollar Cost Averaging... doesn't really work in a sumlation where the strategy assumes no outside money coming in
              Gain     Trial Period                  Cal days  Trading days
        min = -23.02% [Feb 27, 1987 - Nov 12, 1987],      258,          181
        q1  =   3.29% [Feb 23, 1988 - Oct 10, 2011],     8630,         5960
        med =   5.96% [Dec 29, 1988 - Apr 23, 2004],     5594,         3864
        q3  =   7.96% [Oct 26, 2015 - Apr 27, 2017],      549,          379
        max =  15.39% [Jan 14, 1991 - Feb 09, 1999],     2948,         2041
```