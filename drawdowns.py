#!/usr/bin/python

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
import matplotlib

plt.style.use('ggplot')

from collections import namedtuple

import sys

Drawdown = namedtuple('Drawdown', 'start end percentage')


def get_dataframe(file_name):
    df = pd.read_csv(file_name, index_col='Date', parse_dates=True)
    return df.reindex(index=df.index[::-1])


def find_drawdowns(df, percentage_limit):
    current_max_idx = 0
    current_max_price = 0

    last_price = 0

    drawdowns = []

    for idx, price in enumerate(df['Close']):
        if price > last_price:
            if current_max_price > price:
                #end of a drawdown

                drawdown_percentage = 100 - 100*price/current_max_price

                if drawdown_percentage >= percentage_limit:

                    drawdowns.append(Drawdown(current_max_idx, idx - 1, drawdown_percentage))

            current_max_idx = idx
            current_max_price = price

        last_price = price

    return drawdowns


def plot_drawdown(df, drawdown):
    data = df[max(drawdown.start - 4, 0):min(drawdown.end + 4, len(df.index))]

    fig = plt.figure(figsize=(15, 9))

    plt.axvspan(df.index[drawdown.start], df.index[drawdown.end], color='red', alpha=0.3)

    ax = fig.add_subplot(1,1,1)
    ax.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.9]]))
    ax.plot(data.index, data.Close, color='blue')

    ax2 = ax.twinx()
    ax2.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.32]]))
    ax2.bar(data.index, data.Volume, 0.3, color='red')

    plt.show()


if __name__ == "__main__":
    #the script was executed directly

    if len(sys.argv) != 3:
        print "Usage: %s <csv file> <percentage>" % sys.argv[0]
        sys.exit(1)

    df = get_dataframe(sys.argv[1])
    drawdown_limit = int(sys.argv[2])

    drawdowns = find_drawdowns(df, drawdown_limit)
    drawdowns.sort(key=lambda x: x.percentage, reverse=True)

    for d in drawdowns:
        print d
        
    for d in drawdowns:
        plot_drawdown(df, d)