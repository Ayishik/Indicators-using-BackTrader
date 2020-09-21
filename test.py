from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np 
import argparse
import backtrader as bt 
import backtrader.indicators as btind
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import datetime 
# import matplotlib
# from matplotlib.dates import warnings
from strats import GoldenCross,BollingerBands,StochasticOscillator,RSI_IchCloud,ADX

# change the "default=XYZ" values if required
parser = argparse.ArgumentParser(description='Backtest the strategy')
parser.add_argument('-df','--datafile',type=str,default='/home/ayishik/BackTraderPrac/Sample Data(.txt)/orcl-1995-2014.txt',help='Path to the data file')
parser.add_argument('-C','--CASH',type=float,default=1000.0,help='Total Cash')
parser.add_argument('-S','--STAKE',type=float,default=5,help='Stake')
parser.add_argument('-CM','--COMMISSION',type=float,default=0.001,help='Commission')

args = parser.parse_args()

cerebro = bt.Cerebro()

# Add/Change the strategy
# You may want to change the default cash for different strategy
cerebro.addstrategy(ADX)

# Datas are in a subfolder of the samples. Need to find where the script is
# because it could have been called from anywhere

data_path = args.datafile

data = bt.feeds.YahooFinanceCSVData(
        dataname= data_path,
        # Do not pass values before this date
        fromdate=datetime.datetime(1999, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2014, 12, 31),
        # Do not pass values after this date
        reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Set the specifications
cerebro.broker.setcash(args.CASH)
cerebro.addsizer(bt.sizers.FixedSize, stake=args.STAKE)
cerebro.broker.setcommission(commission=args.COMMISSION)
cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


thestrats = cerebro.run()
thestrat = thestrats[0]

print('Sharpe Ratio:', thestrat.analyzers.mysharpe.get_analysis())

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot()
