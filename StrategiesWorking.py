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
def BB():


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

           
            df2['20 ma'] = df_list[y]['Open'].rolling(20).mean()
            df2['20 sd'] = df_list[y]['Open'].rolling(20).std()
            df2['upper band'] = df2['20 ma'] + (df2['20 sd']*2)
            df2['lower band'] = df2['20 ma'] - (df2['20 sd']*2)
            df2['mid band'] = (df2['upper band'] - df2['lower band'])/2 + df2['lower band']
            
            
           
            if stance == 'none':
                if df_list[y]['Open'][x] < (df2['lower band'][x]):
                    if ActiveBalance > df_list[y]['Open'][x]:

                        stance = 'holding'
                        print ("Buying {} @ {:.8f}".format(markets_list[y].replace('BTC',''), df_list[y]['Open'][x]), 'BTC')
                        Buyin = df_list[y]['Open'][x] 
                        buy_list.append(Buyin)
                        ActiveBalance = ActiveBalance - Buyin
                        print ('ACTIVE BALANCE: ',ActiveBalance)
                        print()
                        NB+=1

                    else:
                        print ("Not enough BTC to buy: ", markets_list[y])
                        print()
                        
                    
            elif stance == 'holding':

                if df_list[y]['Open'][x] > (df2['lower band'][x]):

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

        
        #df['Open'].plot(color='b')
        #df2['upper band'].plot(color='g')
        #df2['lower band'].plot(color='g')
        #df2['mid band'].plot(color='r')
        #plt.show()
        
    FinalBalance = sum(BTCBalance_list)
    TP = (TP/FinalBalance) * 100
    print('Total profit is: ', TP,'%')
    
    print("Final Balance is: ", FinalBalance, " BTC")
    #stylising graph and plotting 
    '''
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=1, colspan=1, facecolor='#E3F7FF')
   
    buydots = ax1.plot(buy_list, marker = 'o', color='r')
    selldots = ax1.plot(sell_list, marker = 'o', color='g')
    #annotations
    ax1.legend()
    leg = ax1.legend(loc=2, ncol=2, prop={'size':9})
    leg.get_frame().set_alpha(0.4)

    plt.title('Backtest for ' + symbol + ' in BTC')
    ax2 = plt.subplot2grid((6,1), (1,0), rowspan=4, colspan=1, facecolor='#E3F7FF', alpha=0.05)
    ax2v = ax2.twinx()
    ax2.axes.xaxis.set_ticklabels([])

    plt.ylabel('Backtest for ' + symbol + ' in BTC')
    ax3 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, facecolor='#E3F7FF', alpha=0.05)
    plt.ylabel('...')
    #ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #ax3.xaxis.set_major_locator(mticker.MaxNLocator(10))
    for label in ax3.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
#plotting candlesticks
    
    
    #ax2v.plot([],[], color='#0079a3', alpha=0.4, label='Volume')
    #ax2v.fill_between(df.date[-start:],0, df.volume[-start:], facecolor='#0079a3', alpha=0.4)
    ax2v.axes.yaxis.set_ticklabels([])
    ax2v.grid(False)
   # ax2v.set_ylim(0, 2*df.volume.max())
    ax2j = ax2.twiny()
    ax2j.plot(df_list[y]['Open'], linewidth=1)
    plt.ylabel('Open')
   
    ax2j.plot(df2['upper band'],linewidth=0.5,color='black')
    ax2j.plot(df2['lower band'],linewidth=0.5,color='black')
    ax2j.plot(df2['mid band'],linewidth=0.3,color='black')

    plt.setp(ax2j.get_xticklabels(), visible=False)
    ax2j.grid(False)
    
   # ax3.plot(df.date[-start:], ma1[-start:],linewidth=1, label=(str(MA1)+ 'MA'))
   # ax3.plot(df.date[-start:], ma2[-start:],linewidth=1, label=(str(MA2)+ 'MA'))

    ax2j.legend()
    leg = ax2j.legend(loc=1, ncol=5, prop={'size':9})
    leg.get_frame().set_alpha(0.4)

    ax2v.legend()
    leg = ax2v.legend(loc=2, ncol=5, prop={'size':9})
    leg.get_frame().set_alpha(0.4)

    ax3.legend()
    leg = ax3.legend(loc=2, ncol=2, prop={'size':9})
    leg.get_frame().set_alpha(0.4)

    plt.show()'''
    

def RSI(prices, n=10):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs= up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]

        if delta > 0:
            upval = delta
            downval = 0.

        else:
            upval = 0
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down

        rsi[i] = 100. -100./(1.+rs)


    return rsi

def backTesting():

    EMAPrices = EMA(df['Open'], 50)
    rsiLine = RSI(EMAPrices, n=1500)

    x = 0
    stance = 'none'
    lastBoughtFor = 0
    totalProfit = 0
    rsi_list = []
    df2 = pd.DataFrame(rsiLine)
    while x < len(rsiLine):
        rsi_list.append(rsiLine[x])
        print (rsiLine[x])
        if stance == 'none':
            if rsiLine[x] < 30:
                stance = 'holding'
                print ('buying NEO @', df['Open'][x], 'BTC')
                lastBoughtFor = df['Open'][x]
        
        elif stance == 'holding':
            if rsiLine[x] > 70:
                stance = 'none'
                print ('Selling NEO @', df['Open'][x], 'BTC')
                totalProfit += df['Open'][x]
        x+=1
    print ('Total Profit: ', totalProfit)

    fig1 = df['Open'].plot()
    fig2 = df2.plot()
    plt.show()

def EMA(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a
#backTesting()
