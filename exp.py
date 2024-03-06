"""
ToDo: decrease coefficient
ToDo: make date range floating +/- x days (may vary)
"""

import os
import csv
from datetime import datetime, timedelta
from datetime import date as dt
import statistics
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statistics

URL = 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YVZVEJUA1CP6BTICXPRM2QPXM9KPRKA3ST'
r = requests.get(url=URL)
data = r.json()

my_eth = 1.91029
current_eth_price = float(data['result'].get('ethusd'))
my_eth_earnings = round(current_eth_price * my_eth, 2)

coefficient = 1.3  #  minimum coefficient of growth
max_jump_range = 90  #  maximum jump range of growth (1, 90, 5) (start, stop, step)
min_exp_power = 7

dir_with_csv = r'C:\Users\estepanyshchenko\Documents\script\data'
print('_______________________________________')
for filename in os.listdir(dir_with_csv):
    print(f'Analyzing {filename}...')

    #  create 2 arrays for dates and prices
    array_dates = []
    array_prices = []
    with open(f'data/{filename}', 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            array_dates.append(row[0])
            #  remove dots and commas from array with prices
            array_prices.append(float(row[1].replace('.', '').replace(',', '.')))

    #  reverse arrays wit Dates and Prices, to show from oldest to newest date
    array_dates.reverse()
    array_prices.reverse()

    #  This will be final array of objects
    temp_array_with_high_exp = []
    final_array = []

    #  For every date, try different date ranges (jump lengths) from 1 to 28 with step 1
    for jump_range in range(1, max_jump_range, 1):  # (start, stop, step)
        temp_array = []

        #  iterate over all prices with current jumpRange (1-3, 2-4, 3-5...)
        for idx, val in enumerate(array_prices):

            #  if next jump is possible
            if idx < len(array_prices) - jump_range:

                # calculate current priceChange, create an object, fill it in with its data
                rounded_price_change = round(array_prices[idx + jump_range] / array_prices[idx], 2)
                obj = {}
                obj['jumpRange'] = jump_range
                obj['priceChange'] = rounded_price_change
                obj['fromDate'] = array_dates[idx]
                obj['fromPrice'] = val
                obj['toDate'] = array_dates[idx + jump_range]
                obj['toPrice'] = array_prices[idx + jump_range]
                if obj.get('priceChange') >= coefficient:
                    obj['exponentPower'] = 1

                # add object to temporary array
                temp_array.append(obj)

        #  iterate over temporary array with same jumps
        for idx, currentDict in enumerate(temp_array):

            # if there will be next jump, at the END of current jump, add jump range to current dict
            if idx < len(temp_array) - currentDict.get('jumpRange'):
                nextDict = temp_array[idx + currentDict.get('jumpRange')]

                # increase exponentPower of next jump on 1
                if 'exponentPower' in currentDict and 'exponentPower' in nextDict:
                    nextDict['exponentPower'] = currentDict.get('exponentPower') + 1

        #  create array of temporary dicts, which exponentPower >= minimumExponentPower and which are not finished in the past
        for idx, currentDict in enumerate(temp_array):
            today = dt.today()
            from_date = datetime.strptime(currentDict.get('fromDate'), '%d.%m.%Y')
            currentDict['fromDate'] = from_date
            to_date = datetime.strptime(currentDict.get('toDate'), '%d.%m.%Y')
            currentDict['toDate'] = to_date
            #  and (to_date + timedelta(days=currentDict.get('jumpRange')) > datetime.today())
            if 'exponentPower' in currentDict and (currentDict.get('exponentPower') >= min_exp_power):
                temp_array_with_high_exp.append(currentDict)

    newlist = sorted(temp_array_with_high_exp, key=lambda d: d['fromDate'])
    print(*newlist, sep="\n")
    print(f'length of newlist is {len(newlist)}')
    # beautiful plots
    for idx, dict in enumerate(newlist):
        jumprange = newlist[idx].get('jumpRange')
        dict.update({'nextExpectedDate': dict['toDate'] + timedelta(days=dict.get('jumpRange'))})
        nextExp9 = newlist[idx].get('nextExpectedDate')
        currentToDate = newlist[idx].get('toDate')
        currentFromDate = newlist[idx].get('fromDate')
        previousFromDateExp6 = currentFromDate - timedelta(days=jumprange)
        previousFromDateExp5 = previousFromDateExp6 - timedelta(days=jumprange)
        previousFromDateExp4 = previousFromDateExp5 - timedelta(days=jumprange)
        previousFromDateExp3 = previousFromDateExp4 - timedelta(days=jumprange)
        previousFromDateExp2 = previousFromDateExp3 - timedelta(days=jumprange)
        previousFromDateExp1 = previousFromDateExp2 - timedelta(days=jumprange)
        array = [previousFromDateExp1, previousFromDateExp2, previousFromDateExp3, previousFromDateExp4,
                 previousFromDateExp5, previousFromDateExp6, currentFromDate, currentToDate]

        date_time_exp1 = previousFromDateExp1.strftime("%d.%m.%Y")
        date_time_exp2 = previousFromDateExp2.strftime("%d.%m.%Y")
        date_time_exp3 = previousFromDateExp3.strftime("%d.%m.%Y")
        date_time_exp4 = previousFromDateExp4.strftime("%d.%m.%Y")
        date_time_exp5 = previousFromDateExp5.strftime("%d.%m.%Y")
        date_time_exp6 = previousFromDateExp6.strftime("%d.%m.%Y")
        date_time_exp7 = currentFromDate.strftime("%d.%m.%Y")
        date_time_exp8 = currentToDate.strftime("%d.%m.%Y")
        date_time_expFuture = nextExp9.strftime("%d.%m.%Y")

        index1 = array_dates.index(date_time_exp1)
        index2 = array_dates.index(date_time_exp2)
        index3 = array_dates.index(date_time_exp3)
        index4 = array_dates.index(date_time_exp4)
        index5 = array_dates.index(date_time_exp5)
        index6 = array_dates.index(date_time_exp6)
        index7 = array_dates.index(date_time_exp7)
        index8 = array_dates.index(date_time_exp8)
        indexFuture = array_dates.index(date_time_expFuture)

        #print(f'index 8 is {index8}')
        #print(f'price 8 is {array_prices[index8]}')

        arrayOfMaxDecreases = []
        min = array_prices[index1]
        for i in range(index1, index2):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index1], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index2]
        for i in range(index2, index3):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index2], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index3]
        for i in range(index3, index4):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index3], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index4]
        for i in range(index4, index5):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index4], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index5]
        for i in range(index5, index6):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index5], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index6]
        for i in range(index6, index7):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index6], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        min = array_prices[index7]
        for i in range(index7, index8):
            if array_prices[i] < min:
                min = array_prices[i]
        maxDecrease = round(100 - min*100/array_prices[index7], 2)
        arrayOfMaxDecreases.append(maxDecrease)

        minimum = array_prices[index8]
        for i in range(index8, indexFuture):
            if array_prices[i] < minimum:
                minimum = array_prices[i]
        maxDecrease = round(100 - minimum*100/array_prices[index8], 2)

        print(f'{idx} - {arrayOfMaxDecreases}, max: {max(arrayOfMaxDecreases)}, finish with: {maxDecrease}')

# plot beautiful figure
        fig, ax = plt.subplots()  # Create a figure containing a single axes.
        ax.plot(array_dates, array_prices, color='blue', linewidth=1, linestyle=':')  # Plot some data on the axes.
        col = []
        for i in range(0, len(array_dates)):
            if datetime.strptime(array_dates[i], '%d.%m.%Y') in array:
                col.append('orange')
            if datetime.strptime(array_dates[i], '%d.%m.%Y') == nextExp9:
                col.append('red')
            else:
                col.append('white')

        for i in range(len(array_dates)):
            if col[i] == 'white':
                plt.scatter(array_dates[i], array_prices[i], c=col[i], s=5, linewidth=1)
            if col[i] == 'orange':
                plt.scatter(array_dates[i], array_prices[i], c=col[i], s=25, linewidth=1)
            if col[i] == 'red':
                plt.scatter(array_dates[i], array_prices[i], c=col[i], s=25, linewidth=1)

        plt.show()


# join similar dicts
"""
    for j in range(10):
        for i in range(10):
            for idx, currentDict in enumerate(newlist):
                if idx != len(newlist) - 1:
                    nextDict = newlist[idx + 1]
                    if currentDict.get('exponentPower') == nextDict.get('exponentPower') and ((nextDict.get('fromDate') - currentDict.get('fromDate')).days <= 10):
                        if currentDict['jumpRange'] < nextDict.get('jumpRange'):
                            currentDict['maxJumpRange'] = nextDict.get('jumpRange')
                        else:
                            currentDict['maxJumpRange'] = currentDict.get('jumpRange')
                            currentDict['jumpRange'] = nextDict.get('jumpRange')
                        if currentDict['fromDate'] < nextDict.get('fromDate'):
                            currentDict['maxFromDate'] = nextDict.get('fromDate')
                        else:
                            currentDict['maxFromDate'] = currentDict.get('fromDate')
                            currentDict['fromDate'] = nextDict.get('fromDate')
                        if currentDict['fromPrice'] < nextDict.get('fromPrice'):
                            currentDict['maxFromPrice'] = nextDict.get('fromPrice')
                        else:
                            currentDict['maxFromPrice'] = currentDict.get('fromPrice')
                            currentDict['fromPrice'] = nextDict.get('fromPrice')
                        if currentDict['toDate'] < nextDict.get('toDate'):
                            currentDict['maxToDate'] = nextDict.get('toDate')
                        else:
                            currentDict['maxToDate'] = currentDict.get('toDate')
                            currentDict['toDate'] = nextDict.get('toDate')
                        if currentDict['toPrice'] < nextDict.get('toPrice'):
                            currentDict['maxToPrice'] = nextDict.get('toPrice')
                        else:
                            currentDict['maxToPrice'] = currentDict.get('toPrice')
                            currentDict['toPrice'] = nextDict.get('toPrice')
                        if currentDict['priceChange'] < nextDict.get('priceChange'):
                            currentDict['maxPriceChange'] = nextDict.get('priceChange')
                        else:
                            currentDict['maxPriceChange'] = currentDict.get('priceChange')
                            currentDict['priceChange'] = nextDict.get('priceChange')
                        newlist.remove(nextDict)
                        #print(f'combined 2 similar dicts with same exponent power of {currentDict["exponentPower"]}')

        for i in range(10):
            for idx, currentDict in enumerate(newlist):
                if idx != len(newlist) - 1:
                    nextDict = newlist[idx + 1]
                    if currentDict['exponentPower'] < nextDict.get('exponentPower'):
                        if nextDict.get('maxFromPrice'):
                            if ((nextDict.get('fromDate') - currentDict.get('fromDate')).days <= 10):
                                if ((currentDict['fromPrice']) >= nextDict.get('fromPrice') and currentDict['fromPrice'] <= nextDict.get('maxFromPrice')):
                                    newlist.remove(currentDict)
                                    #print(f'found 2 similar dicts, and removed with exponent power of {currentDict["exponentPower"]}')

        for i in range(10):
            for idx, currentDict in enumerate(newlist):
                if idx != len(newlist) - 1:
                    nextDict = newlist[idx + 1]
                    if currentDict['exponentPower'] > nextDict.get('exponentPower'):
                        if ((nextDict.get('fromDate') - currentDict.get('fromDate')).days <= 10):
                            newlist.remove(nextDict)
                            #print(f'found 2 similar dicts with dirrefent exponents, removed with exponent power of {nextDict.get("exponentPower")}')

    print(*newlist, sep="\n")
    print(len(newlist))
    print(newlist[0])

    deltaMax = (newlist[0].get('maxToDate') - newlist[0].get('fromDate')).days
    deltaMin = (newlist[0].get('maxToDate') - newlist[0].get('maxFromDate')).days
    currentFromDate = newlist[0].get('fromDate')
    previousFromDateExp6 = currentFromDate - timedelta(days=deltaMax)
    previousToDateExp6 = currentFromDate - timedelta(days=deltaMin)
    previousFromDateExp5 = previousFromDateExp6 - timedelta(days=deltaMax)
    previousToDateExp5 = previousFromDateExp6 - timedelta(days=deltaMin)
    previousFromDateExp4 = previousFromDateExp5 - timedelta(days=deltaMax)
    previousToDateExp4 = previousFromDateExp5 - timedelta(days=deltaMin)
    previousFromDateExp3 = previousFromDateExp4 - timedelta(days=deltaMax)
    previousToDateExp3 = previousFromDateExp4 - timedelta(days=deltaMin)
    previousFromDateExp2 = previousFromDateExp3 - timedelta(days=deltaMax)
    previousToDateExp2 = previousFromDateExp3 - timedelta(days=deltaMin)
    previousFromDateExp1 = previousFromDateExp2 - timedelta(days=deltaMax)
    previousToDateExp1 = previousFromDateExp2 - timedelta(days=deltaMin)
    print(f'1 from {previousFromDateExp1} to {previousToDateExp1}')
    print(f'2 from {previousFromDateExp2} to {previousToDateExp2}')
    print(f'3 from {previousFromDateExp3} to {previousToDateExp3}')
    print(f'4 from {previousFromDateExp4} to {previousToDateExp4}')
    print(f'5 from {previousFromDateExp5} to {previousToDateExp5}')
    print(f'6 from {previousFromDateExp6} to {previousToDateExp6}')
    print(f'7 from {currentFromDate} to {newlist[0].get("maxFromDate")}')
    print(f'x from {newlist[0].get("toDate")} to {newlist[0].get("maxToDate")}')

    col = []
    for i in range(0, len(array_dates)):
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp1 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp1:
            col.append('red')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp2 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp2:
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp3 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp3:
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp4 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp4:
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp5 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp5:
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > previousFromDateExp6 and datetime.strptime(array_dates[i], '%d.%m.%Y') < previousToDateExp6:
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') > newlist[0].get('fromDate') and datetime.strptime(array_dates[i], '%d.%m.%Y') < newlist[0].get('maxFromDate'):
            col.append('grey')
        if datetime.strptime(array_dates[i], '%d.%m.%Y') >= newlist[0].get('toDate') and datetime.strptime(array_dates[i], '%d.%m.%Y') <= newlist[0].get('maxToDate'):
            col.append('grey')
        else:
            col.append('grey')

    for i in range(len(array_dates)):
        plt.scatter(array_dates[i], array_prices[i], c=col[i], s=10, linewidth=0)

    plt.show()
"""

"""
    if final_array:
        dictWithMaxPriceChange = max(final_array, key=lambda x: x['medianPriceChange'])
        # print dates
        # print(currentDict)
        lastSeenDate = datetime.strptime(dictWithMaxPriceChange['lastSeenDate'], '%d.%m.%Y')
        nextExpectedDate = lastSeenDate + timedelta(days=dictWithMaxPriceChange.get('jumpRange'))
        nextExpectedDate = nextExpectedDate.strftime('%d.%m.%Y')
        dictWithMaxPriceChange.update({'nextExpectedDate': nextExpectedDate})
        nextExpectedPrice = round(dictWithMaxPriceChange.get('lastPrice') * dictWithMaxPriceChange.get('medianPriceChange'), 2)
        dictWithMaxPriceChange.update({'nextExpectedPrice': nextExpectedPrice})
        print(dictWithMaxPriceChange)
        print('Report:')
        print(f'We found {dictWithMaxPriceChange.get("exponentPower")} jumps, {dictWithMaxPriceChange.get("jumpRange")} days each.')
        print(f'Expecting value of ${nextExpectedPrice}, on {nextExpectedDate}.')
        print(f'mediana of {dictWithMaxPriceChange.get("medianPriceChange")}.')
        if filename == 'ETH_USD.csv':
            print(f'I`m going to increase value from ${my_eth_earnings} to ${round(nextExpectedPrice * my_eth, 2)}.')
            print('Hodl!')
    else:
        print(f'No results found for ExponentPower >= {min_exp_power}')

    print('_______________________________________')
    """
if __name__ == '__main__ ':
    print('The End')

