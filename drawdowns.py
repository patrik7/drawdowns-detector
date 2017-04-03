#!/usr/bin/python

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

import matplotlib.pyplot as plt
import matplotlib

from collections import deque #dequeue allows O(1) popleft
from collections import namedtuple

import sys

Drawdown = namedtuple('Drawdown', 'start end percentage start_date end_date')

#assumes data formated same way as: http://chart.finance.yahoo.com/table.csv?s=^GSPC&a=0&b=3&c=1950&d=1&e=3&f=2017
def get_dataframe(file_name):
    df = pd.read_csv(file_name, index_col='Date', parse_dates=True)
    return df.reindex(index=df.index[::-1])


def find_drawdowns(df, percentage_limit):
    #this has disadvantage of detecting extra maximums for [1,3,3,2,2,1], similar problem for minimums, we need to compensate
    drawdown_start_indexes = deque(argrelextrema(df.Close.values, np.greater_equal)[0])
    drawdown_end_indexes = deque(argrelextrema(df.Close.values, np.less_equal)[0])

    #note: np.less or np.greater does not detect [2,3,3,2] as maximum as it looks at the learest neighbor only

    drawdowns = []

    global_maximum_price = 0

    while drawdown_start_indexes and drawdown_end_indexes:

        local_maximum_idx = drawdown_start_indexes.popleft()

        if df.iloc[local_maximum_idx].Close > global_maximum_price:
            drowdown_start = local_maximum_idx
            global_maximum_price = df.iloc[local_maximum_idx].Close


        #compensate for extra minimums
        while drawdown_end_indexes[0] <= drowdown_start:
            drawdown_end_indexes.popleft()
            if not drawdown_end_indexes:
                return drawdowns

        drowdown_end = drawdown_end_indexes.popleft()

        #compensate for extra maximums
        while drawdown_start_indexes[0] <= drowdown_end:
            drawdown_start_indexes.popleft()
            if not drawdown_start_indexes:
                return drawdowns

        drawdown_percentage = 100 - 100*df.iloc[drowdown_end].Close/global_maximum_price

        if drawdown_percentage >= percentage_limit:

            drawdowns.append(Drawdown(drowdown_start, drowdown_end, drawdown_percentage, df.index[drowdown_start], df.index[drowdown_end]))

    return drawdowns


def plot_drawdown(df, drawdown, days_before=12, days_after=12):
    data = df[max(drawdown.start - days_before, 0):min(drawdown.end + days_after, len(df.index))]

    fig = plt.figure(figsize=(15, 9))

    plt.axvspan(df.index[drawdown.start], df.index[drawdown.end], color='red', alpha=0.3)

    ax = fig.add_subplot(1,1,1)
    ax.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.9]]))
    ax.plot(data.index, data.Close, color='blue')

    ax2 = ax.twinx()
    ax2.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.32]]))
    ax2.bar(data.index, data.Volume, color='red')

    plt.show()


if __name__ == "__main__":
    #the script was executed directly

    if len(sys.argv) != 3:
        print "Usage: %s <csv file> <percentage>" % sys.argv[0]
        sys.exit(1)

    plt.style.use('ggplot')

    #read command line arguments
    csv_file = sys.argv[1]
    drawdown_limit = float(sys.argv[2])

    df = get_dataframe(csv_file)

    drawdowns = find_drawdowns(df, drawdown_limit)
    drawdowns.sort(key=lambda x: x.percentage, reverse=True)

    for d in drawdowns:
        print d

    for d in drawdowns:
        plot_drawdown(df, d)
