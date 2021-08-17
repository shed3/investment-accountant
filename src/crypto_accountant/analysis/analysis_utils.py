import pandas as pd
import numpy as np


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