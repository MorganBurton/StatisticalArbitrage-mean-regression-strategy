from binance.client import Client

# uses the date_to_milliseconds and interval_to_milliseconds functions
# https://gist.github.com/sammchardy/3547cfab1faf78e385b3fcb83ad86395
# https://gist.github.com/sammchardy/fcbb2b836d1f694f39bddd569d1c16fe

import dateparser
import pytz
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from sklearn import preprocessing
#############
#STUFF FOR MICHAEL TO DO
#1. Get rid of copy paste for 2nd coin, add it to the first for loop if possible
#or just make it more efficient
#2. Add fee caclulations
#3. either scrape website for best coins to test, or get own correlation data n Gen
#a list for us to use
#4. add basic buy n sell for the short position.



#############

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)

def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms

def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get Historical Klines from Binance
    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/
    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str
    :return: list of OHLCV values
    """
    # create the Binance client, no need for api key
    client = Client("", "")

    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    # convert our date strings to milliseconds
    start_ts = date_to_milliseconds(start_str)

    # if an end time was passed convert it
    end_ts = None
    if end_str:
        end_ts = date_to_milliseconds(end_str)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # less than limit means present time
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data


def DataRetrieval():

    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    
    df_list = []
    marketdict = {'markets_list': [], 'no_markets': [],
                    'stance':[], 'TP': [],
                    'NB': [], 'NS': [],
                    'ActiveBalance': [], 'buy_list': [],
                    'sell_list': [], 'Buyin': [0],
                    'profit_list':[], 'ProfitableTradeRatio': [],
                    'NoOfLosses': [], 'NoOfGains': [],
                    'BTCBalance_list': [], 'x': [],
                    'TradeProfit': []
                    }


    for x in range(0,2):

        marketdict['markets_list'].append(input('Enter Market to backtest: '))
        
    interval = input('Enter kline interval:')
    
    start = "1 Sep, 2018"
    end = "7 Sep, 2018"
    
    for symbol in marketdict['markets_list']: 
        print ("this is x:" , symbol)
        klines = get_historical_klines(symbol, interval, start, end)
        # open a file with filename including symbol, interval and start and end converted to milliseconds
        with open(
            "Binance_{}_{}_{}-{}.json".format(
                symbol, 
                interval, 
                start,
                end
            ),
            'w' # set file write mode
        ) as f:
            f.write(json.dumps(klines))
        file = "Binance_{}_{}_{}-{}.json".format(
                symbol, 
                interval, 
                start,
                end)
        with open(file) as data_file:
            data_dict = json.load(data_file)

        df = pd.DataFrame.from_dict(data_dict).applymap(float)
        df.columns = ['Open Time'
                        ,'Open','High'
                        ,'Low','Close'
                        ,'Volume','Close Time'
                        ,'QA Volume','No Trades'
                        ,'TBBA volume','TBQA Volume','Ignore']
        df_list.append(df)


    df = pd.merge(df_list[0], df_list[1], on='Open Time')
   
    return df     
def normalise():
    df = DataRetrieval()
    
    buy_position = 0
    short_position = 0
    profit_buy = 0
    profit_short = 0

    buy_percentprofit = 0
    short_percentprofit = 0

    buy_avgprofit = 0
    short_avgprofit = 0

    buy_totalprofit = 0
    short_totalprofit = 0
    
    bought_x = 'no'
    bought_y = 'no'

    totalprofit = 0
    balance = 1
    altbalance = 0
    counter = 0
    percentprofittotals = 0
    stance = 'none'
    short_stance = 'none'

    #calc norms and spread in both directions
    df['norm_x'] = pd.Series((df['Close_x'] - df['Close_x'].mean()) / (df['Close_x'].max() - df['Close_x'].min()))
    df['norm_y'] = pd.Series((df['Close_y'] - df['Close_y'].mean()) / (df['Close_y'].max() - df['Close_y'].min()))
    df['difference_x'] = df['norm_y'] - df['norm_x']
    df['difference_y'] = df['norm_x'] - df['norm_y']
    df['date_x'] = pd.to_datetime(df['Close Time_x'])
    df['date_y'] = pd.to_datetime(df['Close Time_y'])

    df.to_csv('merge.csv')

    df = pd.read_csv('merge.csv')
 
   
    
    for x in range(len(df)):
        if stance == 'none':
            #buy x n short y
            if df['difference_x'][x] > 0.10:
            
                print ('Buying x at: ', df['Close_x'][x], 'BTC')
                print ("Starting short on y at: ", df['Close_y'][x], 'BTC')
                print ('Time: ', df['date_x'][x])

                stance = 'holding'
                buy_position = df['Close_x'][x]
                short_position = df['Close_y'][x]
                bought_x = 'yes'

            #buy y n short x
            elif df['difference_y'][x] > 0.10:
            
                print ('Buying y at: ', df['Close_y'][x], 'BTC')
                print ("Starting short on x at: ", df['Close_x'][x], 'BTC')
                print ('Time: ', df['date_y'][x])

                buy_position = df['Close_y'][x]
                short_position = df['Close_x'][x]
                buyin = df['Close_y'][x]
                stance = 'holding'
                bought_y = 'yes'

        elif stance == 'holding':
            if df['difference_x'][x] < 0 and bought_x == 'yes':

                stance = 'none'
                counter +=1
                bought_x = 'no'

                print ('Selling x at: ', df['Close_x'][x], 'BTC')
                print ('Shorting y at: ', df['Close_y'][x], 'BTC')
                print ('Time: ', df['date_x'][x])

                profit_buy = df['Close_x'][x] - buy_position
                profit_short = short_position - df['Close_y'][x]

                buy_percentprofit = ((df['Close_x'][x] - buy_position)/buy_position) * 100
                buy_totalprofit += buy_percentprofit
                

                short_percentprofit = ((short_position - df['Close_y'][x])/short_position) * 100
                short_totalprofit +=short_percentprofit
                

                print('Profit on Trade: ', round(buy_percentprofit,4), '%')
                print('Profit on Short: ', round(short_percentprofit,4), '%')
                print ()

            elif df['difference_y'][x] < 0 and bought_y == 'yes':

                stance = 'none'
                counter +=1
                bought_y = 'no'

                print ('Selling y at: ', df['Close_y'][x], 'BTC')
                print ('Shorting x at: ', df['Close_x'][x], 'BTC')
                print ('Time: ', df['date_y'][x])

                profit_buy = df['Close_y'][x] - buy_position
                profit_short = short_position - df['Close_x'][x]

                buy_percentprofit = ((df['Close_y'][x] - buy_position)/buy_position) * 100
                buy_totalprofit += buy_percentprofit

                short_percentprofit = ((short_position - df['Close_x'][x])/short_position) * 100
                short_totalprofit +=short_percentprofit

                print('Profit on Trade: ', round(buy_percentprofit,4), '%')
                print('Profit on Short: ', round(short_percentprofit,4), '%')
                print ()

    buy_avgprofit = buy_totalprofit/counter
    short_avgprofit = short_totalprofit/counter


    print ()
    print ('avg profit on buy: ', round(buy_avgprofit,4), '%')
    print ('avg profit on short: ', round(short_avgprofit,4), '%')
    print()
    
    #Graph is useless atm
    df['norm_x'].plot(label="1st")
    df['norm_y'].plot()
    plt.show()


    return df


    
    #print ((df_list[0]["Close"] - df_list[1]["Close"])/df_list[0]["Close"] * 100)

normalise();

