from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math 

# Import the backtrader platform
import backtrader as bt

class GoldenCross(bt.Strategy) :
    
    params = (('fast',200),('slow',50))
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__ (self) :
        self.sma1 = bt.indicators.SMA(self.data.close, period = self.params.fast, plotname = '200 moving average') 
        self.sma2 = bt.indicators.SMA(self.data.close, period = self.params.slow, plotname = '50 moving average') 
        
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2) 
        # If sma2 is going above sma1, crossover is 1 and when sma1 is going above sm2, crossover is -1
        # We want to buy when crossover is 1 and sell when crossover is -1
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self) :
        if self.position.size == 0 :   
            if self.crossover > 0 :
                self.numShares = math.floor(self.broker.cash * 0.90/self.data.close)
                
                print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
                self.buy(size = self.numShares)
        
        if self.position.size > 0 :
            if self.crossover < 0 :
                
                print("SELL {} shares at {}".format(self.numShares,self.data.close[0]))
                self.close()

class BollingerBands(bt.Strategy) :
    
#     params = (('period',20))
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__ (self) :
        self.bband = bt.indicators.BBands(self.datas[0], period=20)
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
        
    def next(self) :        
        if not self.position :
            if self.data.close[0] < self.bband.lines.bot :
                self.numShares = math.floor(self.broker.cash * 0.95/self.data.close)
                
                print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
                self.buy(size = self.numShares)
            
            elif self.data.close[0] < self.bband.lines.mid :
                self.numShares = math.floor(self.broker.cash * 0.95/self.data.close)
                
                print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
                self.buy(size = self.numShares)
        
        else :
            if self.data.close[0] > self.bband.lines.top :
                print('SELL shares at {}'.format(self.data.close[0]))
                self.close()
            
            elif self.data.close[0] > self.bband.lines.mid :
                print('SELL shares at {}'.format(self.data.close[0]))
                self.close()

class StochasticOscillator(bt.Strategy) :
    params =(('periodK',14),('periodD',3),('percent',0.95))
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__ (self) :
        self.highest = bt.indicators.Highest(self.data.high, period = self.params.periodK)
        self.lowest = bt.indicators.Lowest(self.data.low, period = self.params.periodK)
        self.k = (self.data.close[0] - self.lowest) * 100 / (self.highest - self.lowest)
        self.d = bt.indicators.SMA(self.k, period = self.params.periodD, plotname = '%D') 
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self) :
        if not self.position and self.k > self.d and self.data.close[0] < self.data[-1]  :
            self.numShares = math.floor(self.broker.cash * self.params.percent/self.data.close)
                
            print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
            self.buy(size = self.numShares)
        
        if self.position and self.k < self.d and self.data.close[0] > self.data[-1] and self.data.close[-1] > self.data[-2] :
            print('SELL shares at {}'.format(self.data.close[0]))
            self.close()  

class RSI_IchCloud(bt.Strategy) :
    params =(('period',14),('percent',0.95),('overbought',70),('oversold',30))
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__ (self) :
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period= self.params.period)
        self.ishimoku = bt.indicators.Ichimoku()
        self.spanA = self.ishimoku.lines.senkou_span_a
        self.spanB = self.ishimoku.lines.senkou_span_b
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self) :   
        # Checking whether the stock is oversold or over bought and then using Ichimoku Cloud
        if not self.position and self.rsi < self.params.oversold:
            # Checking whether the trend is negative(red cloud) and then,if its green cloud,whether the close is below the cloud
            if self.spanA < self.spanB or (self.spanA > self.spanB and self.data.close[0] < self.spanB) :
                self.numShares = math.floor(self.broker.cash * self.params.percent/self.data.close)
    #             self.numShares = 100

                print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
                self.buy(size = self.numShares)
            
        if self.position and self.rsi > self.params.overbought:
            #Checking if its upward trend(green cloud) and whether the close value above the green cloud
            if self.spanA > self.spanB or (self.spanA > self.spanB and self.data.close[0] > self.spanA) :
                print('SELL shares at {}'.format(self.data.close[0]))
                self.close()

class ADX(bt.Strategy) :
    params =(('period',14),('percent',0.95))
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__ (self) :
        self.avgDirIdx = bt.indicators.AverageDirectionalMovementIndex()
        self.plusDM = bt.indicators.PlusDirectionalIndicator(period= self.params.period)
        self.minusDM = bt.indicators.MinusDirectionalIndicator(period= self.params.period)
        self.DIP = self.plusDM.lines.plusDI
        self.DIM = self.minusDM.lines.minusDI
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self) :   
        if not self.position and self.DIP > self.DIM and self.avgDirIdx.adx > 25 and self.data.close[-1] > self.data.close[0] :
            self.numShares = math.floor(self.broker.cash * self.params.percent/self.data.close)
                
            print("BUY {} shares at {}".format(self.numShares,self.data.close[0]))
            self.buy(size = self.numShares)
        
        if self.position and self.DIP < self.DIM and self.avgDirIdx.adx > 25 and self.data.close[-1] < self.data.close[0] :
            print("SELL {} shares at {}".format(self.numShares,self.data.close[0]))
            self.close()

