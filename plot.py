__author__ = 'mep'

import matplotlib.pyplot as plt

we = lambda old, opp, adj:  (1.0 / (10**(-(old - opp + adj)/400.0) + 1.0))


def plot_test(x, y):
    plt.plot(x, y, 'ro')
    plt.show()