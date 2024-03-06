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

URL = 'https://api.etherscan.io/api?module=stats&action=ethprice&apikey=YVZVEJUA1CP6BTICXPRM2QPXM9KPRKA3ST'
r = requests.get(url=URL)
data = r.json()

my_eth = 0.937
current_eth_price = float(data['result'].get('ethusd'))
my_eth_earnings = round(current_eth_price * my_eth, 2)

coefficient = 1.4  #  minimum coefficient of growth
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

    #fig, ax = plt.subplots()  # Create a figure containing a single axes.
    #ax.plot(arrayDates, newOneArrayPrices, color='blue', linewidth=1, linestyle=':')  # Plot some data on the axes.
    #plt.scatter(arrayDates, newOneArrayPrices, s=5, c=[5, 16, 54, 124, 256], linewidths=1)
    #plt.show()

    #  This will be final array of objects
    final_array = []

    #  For every date, try different date ranges (jump lengths) from 1 to 28 with step 1
    for jump_range in range(1, max_jump_range, 1):  # (start, stop, step)
        temp_array = []
        temp_array_with_high_exp = []

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

            # if there will be next jump, at the END of current jump
            if idx < len(temp_array) - currentDict.get('jumpRange'):
                nextDict = temp_array[idx + currentDict.get('jumpRange')]

                # increase exponentPower of next jump on 1
                if 'exponentPower' in currentDict and 'exponentPower' in nextDict:
                    nextDict['exponentPower'] = currentDict.get('exponentPower') + 1

        #  create array of temporary dicts, which exponentPower >= minimumExponentPower and which are not finished in the past
        for idx, currentDict in enumerate(temp_array):
            today = dt.today()
            last_seen_date = datetime.strptime(currentDict.get('toDate'), '%d.%m.%Y')
            if 'exponentPower' in currentDict and (currentDict.get('exponentPower') >= min_exp_power) and (last_seen_date + timedelta(days=currentDict.get('jumpRange')) > datetime.today()):
                temp_array_with_high_exp.append(currentDict)

        #  find best temporary dict of all temp dicts with same step
        #  take each dict, and calculate its median priceChange, over steps
        for idx, currentDict in enumerate(temp_array_with_high_exp):
            #print(currentDict)
            array_of_price_changes = [currentDict.get('priceChange')]
            tempDict = currentDict
            for number in range(currentDict.get('exponentPower')):
                previousDict = [d for d in temp_array if d['toDate'] == tempDict.get('fromDate')]
                if previousDict:
                    #print(f'{previousDict[0].get("fromDate")} - {previousDict[0].get("toDate")} with growth of {previousDict[0].get("priceChange")}')
                    previous_price_change = previousDict[0].get('priceChange')
                    array_of_price_changes.append(previous_price_change)
                    tempDict = previousDict[0]
            #print(array_of_price_changes)
            median_price_change = statistics.median(array_of_price_changes)
            #print(f'Mediana of PriceChange is: {medianPriceChange}')
            currentDict.update({'medianPriceChange': round(median_price_change, 3)})

        # leave only dict with highest medianPriceChange or averagePriceChange
        for i in range(10):
            for idx, currentDict in enumerate(temp_array_with_high_exp):
                if idx != len(temp_array_with_high_exp) - 1:
                    nextDict = temp_array_with_high_exp[idx + 1]
                    if currentDict.get('medianPriceChange') > nextDict.get('medianPriceChange'):
                        temp_array_with_high_exp.remove(nextDict)
                    if currentDict.get('medianPriceChange') < nextDict.get('medianPriceChange'):
                        temp_array_with_high_exp.remove(currentDict)

        # Clear the date
        if len(temp_array_with_high_exp) == 1:
            bestDictForStep = temp_array_with_high_exp[0]
            bestDictForStep.pop('priceChange')
            bestDictForStep.pop('fromDate')
            bestDictForStep.pop('fromPrice')
            bestDictForStep['lastSeenDate'] = bestDictForStep.pop('toDate')
            bestDictForStep['lastPrice'] = bestDictForStep.pop('toPrice')

            final_array.append(bestDictForStep)

    if final_array:
        dictWithMaxPriceChange = max(final_array, key=lambda x: x['medianPriceChange'])
        # print dates
        # print(currentDict)
        """        arrayOfPriceChanges = []
        arrayOfPriceChanges.append(dictWithMaxPriceChange.get('priceChange'))
        tempDict = dictWithMaxPriceChange
        for number in range(dictWithMaxPriceChange.get('exponentPower')):
            previousDict = [d for d in finalArray if (d['toDate'] == tempDict.get('fromDate') and d['exponentPower'] == tempDict.get('exponentPower'))]
            if previousDict:
                print(f'{previousDict[0].get("fromDate")} - {previousDict[0].get("toDate")} with growth of {previousDict[0].get("priceChange")}')
                previousPriceChange = previousDict[0].get('priceChange')
                arrayOfPriceChanges.append(previousPriceChange)
                tempDict = previousDict[0]"""
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
            print(f'I`m going to increase value from ${my_eth_earnings} to ${round(nextExpectedPrice / my_eth, 2)}.')
            print('Hodl!')
    else:
        print(f'No results found for ExponentPower >= {min_exp_power}')

    print('_______________________________________')

if __name__ == '__main__ ':
    print('The End')

