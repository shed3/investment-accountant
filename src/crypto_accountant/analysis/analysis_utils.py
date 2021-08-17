import pandas as pd
import numpy as np
import talib as ta
import bt
import datetime


def change_percent(frequency, dataset, append_column=True):
    # Get price value for each offset
    value = dataset["close"].pct_change(freq=frequency)
    if append_column:
        dataset[frequency+"_percent_change"] = value
    return value
    

def scaled_close(dataset, append_column=True):
    # Get price value for each offset
    value = dataset["close"] / max(dataset["close"])
    if append_column:
        dataset["scaled_close"] = value
    return value

def change_log(frequency, dataset, append_column=True):
    # Get price value for each offset
    if frequency+"_percent_change" in dataset:
        value = dataset[frequency+"_percent_change"].apply(lambda x: np.log(1+x))
    else:
        value = change_percent(frequency, dataset, False).apply(lambda x: np.log(1+x))
    if append_column:
        dataset[frequency+"_log_change"] = value 
    return value

def change_usd(frequency, dataset, append_column=True):
    # Get price value for each offset
    # This could be done better, see calc changes below
    if frequency+"_percent_change" in dataset:
        value = dataset.close * dataset[frequency+"_percent_change"]
    else:
        value = dataset.close * change_percent(frequency, dataset, False)
    if append_column:
        dataset[frequency+"_usd_change"] = value 
    return dataset

def asset_statistics(datasets, frequency):
    stats = {}
    log_change = merge_timeseries(datasets, frequency + "_log_change")
    stats["var"] = log_change.var()
    stats["cov"] = log_change.cov()
    stats["corr"] = log_change.corr()
    return stats

def calc_changes(datasets):
    for sym in datasets:
        datasets[sym]["1d_change_pct"] = datasets[sym]["close"].pct_change()
        datasets[sym]["3day_change_pct"] = datasets[sym]["close"].pct_change(3)
        datasets[sym]["7day_change_pct"] = datasets[sym]["close"].pct_change(7)
        datasets[sym]["30day_change_pct"] = datasets[sym]["close"].pct_change(30)
        datasets[sym]["3m_change_pct"] = datasets[sym]["close"].pct_change(90)
        datasets[sym]["6m_change_pct"] = datasets[sym]["close"].pct_change(180)
        datasets[sym]["1y_change_pct"] = datasets[sym]["close"].pct_change(365)
        datasets[sym]["2y_change_pct"] = datasets[sym]["close"].pct_change(730)
        datasets[sym]["1d_change"] = datasets[sym]["close"].diff()
        datasets[sym]["3d_change"] = datasets[sym]["close"].diff(3)
        datasets[sym]["7day_change"] = datasets[sym]["close"].diff(7)
        datasets[sym]["30day_change"] = datasets[sym]["close"].diff(30)
        datasets[sym]["3m_change"] = datasets[sym]["close"].diff(90)
        datasets[sym]["6m_change"] = datasets[sym]["close"].diff(180)
        datasets[sym]["1y_change"] = datasets[sym]["close"].diff(365)
        datasets[sym]["2y_change"] = datasets[sym]["close"].diff(730)
    return datasets

def calc_sma(datasets, column, timeperiod):
    for sym in datasets:
        col_array = datasets[sym][column].to_numpy()
        datasets[sym]["{}-sma-{}".format(column, timeperiod)] = ta.SMA(col_array,timeperiod)
    return datasets

def calc_rsi(datasets, timeperiod):
    for sym in datasets:
        col_array = datasets[sym]['close'].to_numpy()
        datasets[sym]["rsi-{}".format(timeperiod)] = ta.RSI(col_array,timeperiod)
    return datasets

def calc_bb(datasets, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
    for sym in datasets:
        col_array = datasets[sym]['close'].to_numpy()
        upperband, middleband, lowerband = ta.BBANDS(col_array, timeperiod, nbdevup, nbdevdn, matype)
        datasets[sym]["bb-{}-{}-{}-upper".format(timeperiod, nbdevup, nbdevup)] = upperband
        datasets[sym]["bb-{}-{}-{}-middle".format(timeperiod, nbdevup, nbdevup)] = middleband
        datasets[sym]["bb-{}-{}-{}-lower".format(timeperiod, nbdevup, nbdevup)] = lowerband
    return datasets

def calc_basic_stats(datasets):
    scaled_close(datasets)
    calc_changes(datasets)
    calc_sma(datasets, "close", 30)
    calc_sma(datasets, "close", 60)
    calc_sma(datasets, "close", 90)
    calc_sma(datasets, "scaled_close", 30)
    calc_sma(datasets, "scaled_close", 60)
    calc_sma(datasets, "scaled_close", 90)
    calc_sma(datasets, "volume", 30)
    calc_sma(datasets, "volume", 60)
    calc_sma(datasets, "volume", 90)
    calc_rsi(datasets, 7)
    calc_rsi(datasets, 14)
    calc_rsi(datasets, 28)
    calc_bb(datasets)
    return datasets

