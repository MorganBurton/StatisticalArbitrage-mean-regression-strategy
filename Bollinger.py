from APIcall import DataRetrieval
import pickle, os, requests, urllib.request, urllib.error, urllib.parse, quandl, time, matplotlib
import datetime as dt 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib import style
from matplotlib.finance import candlestick_ohlc
import plotly.plotly as py

def Buy():

	stance = 'holding'
	print ("Buying {} @ {:.8f}".format(markets_list[y].replace('BTC',''), df_list[y]['Open'][x]), 'BTC')
	
	Buyin = df_list[y]['Open'][x]
	buy_list.append(Buyin)
    ActiveBalance = ActiveBalance - Buyin
    NB+=1

    print ('ACTIVE BALANCE: ',ActiveBalance)
    print()
    

def Sell():

	stance ='none'
	print ("Selling {} @ {:.8f}".format(markets_list[y].replace('BTC',''), df_list[y]['Open'][x]), 'BTC')
    sell_list.append(df_list[y]['Open'][x])
    NS+=1
    TradeProfit = float(df_list[y]['Open'][x]) - Buyin
    print ('Profit is: ', float("{:.8f}".format(TradeProfit)))
    
    if TradeProfit < 0:
        NoOfLosses +=1
    else:
        NoOfGains +=1

    TP += df_list[y]['Open'][x] - Buyin
    ActiveBalance = ActiveBalance + df_list[y]['Open'][x]
    print ('ACTIVE BALANCE: ',ActiveBalance)
    print()

##########STRATEGIES##########
def BollingerBands():

			df2['20 ma'] = df_list[y]['Open'].rolling(20).mean()
            df2['20 sd'] = df_list[y]['Open'].rolling(20).std()
            df2['upper band'] = df2['20 ma'] + (df2['20 sd']*2)
            df2['lower band'] = df2['20 ma'] - (df2['20 sd']*2)
            df2['mid band'] = (df2['upper band'] - df2['lower band'])/2 + df2['lower band']
            

            if df_list[y]['Open'][x] < (df2['lower band'][x]):
            	Buy()
            elif stance == 'holding':
                if df_list[y]['Open'][x] > (df2['lower band'][x]):
                    Sell()


#########RUN##########                   
def RunBacktest():

	df, symbol, markets_list, df_list = DataRetrieval() 
    print ("checking: ", markets_list)
    
    df2 = pd.DataFrame()
    BTCBalance_list = []
    FinalBalance = 0
    for y in range(0, len(df_list)):

        x = 0
        stance = 'none'
        TP = 0
        NB = 0
        NS = 0
        ActiveBalance = 1/len(markets_list) # in BTC
        Sold = 0
        buy_list = []
        sell_list = []
        Buyin = 0
        profit_list = []
        ProfitableTradeRatio = 0
        NoOfLosses = 0
        NoOfGains = 0

        while x < len(df['Open']):
            if stance == 'none':
               if ActiveBalance > df_list[y]['Open'][x]:
               		BollingerBands()

            x+=1
            ALTBalance = (NB - NS) * Buyin
            profit_list.append(TP)

            if NoOfGains and NoOfLosses > 0:
                
                ProfitableTradeRatio = NoOfGains / NoOfLosses

        BTCBalance = ALTBalance + ActiveBalance 
        BTCBalance_list.append(BTCBalance)

        print ("{} balance: {}".format(markets_list[y].replace('BTC',''), ALTBalance))
        print ('BTC Balance: ', BTCBalance)
        print ('Active Balance: ', ActiveBalance)
        print ('NB:', NB)
        print ('NS:', NS)
        print ("ProfitableTradeRatio: ", ProfitableTradeRatio)
        print ("Profit From {} is:  {:.8f}".format(markets_list[y],TP), 'BTC')
        print()

    FinalBalance = sum(BTCBalance_list)
    TP = (TP/FinalBalance) * 100

    print('Total profit is: ', TP,'%')
    print("Final Balance is: ", FinalBalance, " BTC")








